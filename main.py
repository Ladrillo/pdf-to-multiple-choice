import sys
import os
import time
from string import Template
from pathlib import Path
import mdformat
import shutil
import pymupdf4llm
from ollama import chat
from openai import OpenAI
from langchain_text_splitters import MarkdownHeaderTextSplitter
from pydantic import BaseModel
from natsort import natsorted

model = "llama3.3"

generation_params = {
    # int - Enables Mirostat for controlling perplexity (0=off, 1/2=on).
    "mirostat": 0,
    # float - Learning rate for Mirostat; higher = faster adjustments.
    "mirostat_eta": 0.1,
    # float - Balances coherence vs. diversity; lower = more focused.
    "mirostat_tau": 5.0,
    # int - Size of the context window for generating tokens.
    "num_ctx": 8192,
    # int - How far back to look to avoid repetition (-1 = full context).
    "repeat_last_n": 64,
    # float - Penalizes repetition (higher = stronger penalty).
    "repeat_penalty": 1.1,
    # float - Controls creativity; higher = more random output.
    "temperature": 0,
    # int - Random seed for reproducibility (0 = random).
    "seed": 0,
    # string[] - Stop generation when encountering these patterns.
    "stop": [],
    # float - Tail-free sampling; reduces less probable tokens.
    "tfs_z": 1.0,
    # int - Max tokens to predict (-1 = infinite).
    "num_predict": 8192,
    # int - Limits token pool to top-k most likely tokens.
    "top_k": 40,
    # float - Nucleus sampling; considers tokens with cumulative prob <= p.
    "top_p": 0.9,
    # float - Filters tokens below this probability threshold.
    "min_p": 0.05
}


try:
    import prompts as prm
except ImportError:
    import prompts_default as prm
    import warnings
    warnings.warn("Using default constants.")

client = OpenAI()


class PipelineCompleteError(Exception):
    """Exception raised when the pipeline is complete."""
    pass


class Option(BaseModel):
    option_text: str
    is_correct: bool


class Question(BaseModel):
    question_title: str
    question_text: str
    options: list[Option]


class QuestionsList(BaseModel):
    questions: list[Question]


class Conversion():
    def __init__(self, pdf_path, title):
        self.model = model
        self.generation_params = generation_params
        self.title = title
        self.pdf_path = pdf_path
        self.pipeline = [
            self.pdf_convert,
            self.markdown_split,
            self.markdown_classify,
            self.markdown_clean,
            self.quiz_create,
            self.quiz_to_json,
        ]
        self.output_dir_path = self.get_output_dir_path()
        self.output_subdir_paths = self.get_output_subdir_paths()
        self.pointer = self.get_pointer()
        self.make_folders()

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def get_pointer(self):
        pointer = 0
        if not self.output_dir_path.exists() or not self.output_dir_path.is_dir():
            return pointer
        else:
            for subdir_path in self.output_subdir_paths:
                if subdir_path.exists() and subdir_path.is_dir():
                    pointer += 1
                else:
                    print(f"Pointer is {pointer}: {
                          self.pipeline[pointer].__name__}")
                    return pointer
        raise PipelineCompleteError(
            "The pipeline is complete: all subfolders exist."
        )

    def get_output_dir_path(self):
        file_path = Path(self.pdf_path)
        output_dir_path = file_path.parent / file_path.stem
        return output_dir_path

    def get_output_subdir_paths(self):
        output_subdir_paths = [
            self.output_dir_path / f"{idx + 1}_{val.__name__}" for idx, val in enumerate(self.pipeline)
        ]
        return output_subdir_paths

    def make_folders(self):
        if self.pointer == 0:
            if self.output_dir_path.exists() and self.output_dir_path.is_dir():
                shutil.rmtree(self.output_dir_path)
            self.output_dir_path.mkdir(parents=True, exist_ok=True)
        for subdir_path in self.output_subdir_paths[self.pointer:]:
            if subdir_path.exists() and subdir_path.is_dir():
                shutil.rmtree(subdir_path)
            subdir_path.mkdir(parents=True, exist_ok=True)

    def call_model(self, messages, format=None):
        if "gpt-4o" in self.model:
            response = client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=messages,
            )
            return response.choices[0].message.content
        else:
            response = chat(
                model=self.model,
                options=self.generation_params,
                messages=messages,
                format=format
            )
            return response['message']['content']

    def safely_write_file(self, file_path, content):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            # Read back to verify
            with open(file_path, "r", encoding="utf-8") as f:
                written_content = f.read()
            if written_content != content:
                raise ValueError(f"Content mismatch in {file_path}")
        except (IOError, ValueError) as e:
            print(f"Error during file write/read for {file_path}")
            raise

    def pdf_convert(self, output_path):
        markdown = pymupdf4llm.to_markdown(self.pdf_path)
        clean_markdown = markdown.encode(
            'utf-8', errors='ignore'
        ).decode('utf-8')
        output_file_path = output_path / "complete.md"
        self.safely_write_file(output_file_path, clean_markdown)

    def markdown_split(self, input_path, output_path):
        split_by = [("#", "H1"), ("##", "H2"), ("###", "H3"), ("####", "H4")]
        splitter = MarkdownHeaderTextSplitter(split_by, strip_headers=False)
        markdown_path = natsorted(input_path.iterdir())[0]
        markdown = markdown_path.read_text(encoding='utf-8')
        splits = splitter.split_text(markdown)
        contents = [splits[i].page_content for i in range(len(splits))]
        for idx, content in enumerate(contents):
            file_name = f"fragment_{idx + 1}.md"
            file_path = output_path / file_name
            self.safely_write_file(file_path, content)

    def markdown_classify(self, input_path, output_path):
        instructions = Template(prm.CLASSIFY)
        instructions_sub = instructions.substitute(doc_title=self.title)
        for file_path in natsorted(input_path.iterdir()):
            sys.stdout.write(f"\r=> Processing {file_path.stem}")
            sys.stdout.flush()
            markdown = file_path.read_text(encoding='utf-8')
            response = self.call_model([
                {"role": "system", "content": instructions_sub},
                {"role": "user", "content": markdown},
            ])
            parameter = "body" if "body" in response.lower() else "paratext"
            file_name = f"{file_path.stem}_{parameter}.md"
            file_path_new = output_path / file_name
            self.safely_write_file(file_path_new, markdown)

    def markdown_clean(self, input_path, output_path):
        for file_path in natsorted(input_path.iterdir()):
            sys.stdout.write(f"\r=> Processing {file_path.stem}")
            sys.stdout.flush()
            markdown = file_path.read_text(encoding='utf-8')
            file_name = f"{file_path.stem}_clean.md"
            file_path_new = output_path / file_name
            if "_paratext" in file_path.stem:
                file_path_new.write_text("<!-- paratext -->", encoding='utf-8')
            else:
                response = self.call_model([
                    {"role": "system", "content": prm.CLEAN},
                    {"role": "user", "content": markdown}
                ])
                clean_markdown = mdformat.text(response)
                self.safely_write_file(file_path_new, clean_markdown)

    def quiz_create(self, input_path, output_path):
        for file_path in natsorted(input_path.iterdir()):
            instructions = Template(prm.MCQ)
            instructions_sub = instructions.substitute(doc_title=self.title)
            sys.stdout.write(f"\r=> Processing {file_path.stem}")
            sys.stdout.flush()
            markdown = file_path.read_text(encoding='utf-8')
            file_name = f"{file_path.stem}_quiz.md"
            file_path_new = output_path / file_name
            if "_paratext" in file_path.stem:
                file_path_new.write_text("<!-- paratext -->", encoding='utf-8')
            else:
                response = self.call_model([
                    {'role': 'system', 'content': instructions_sub},
                    {'role': 'user', 'content': markdown},
                ])
                response_improved = self.call_model([
                    {'role': 'system', 'content': instructions_sub},
                    {'role': 'user', 'content': markdown},
                    {'role': 'assistant', 'content': response},
                    {'role': 'user', 'content': prm.IMPROVE_MCQ},
                ])
                self.safely_write_file(
                    file_path_new, mdformat.text(response_improved)
                )

    def quiz_to_json(self, input_path, output_path):
        for file_path in natsorted(input_path.iterdir()):
            sys.stdout.write(f"\r=> Processing {file_path.stem}")
            sys.stdout.flush()
            markdown = file_path.read_text(encoding='utf-8')
            file_name = f"{file_path.stem}.json"
            file_path_new = output_path / file_name
            if "_paratext" in file_path.stem:
                file_path_new.write_text('{"questions":[]}', encoding='utf-8')
            else:
                response = self.call_model(
                    [
                        {'role': 'system', 'content': prm.OUTPUT_JSON},
                        {'role': 'user', 'content': markdown},
                    ],
                    QuestionsList.model_json_schema()
                )
                mcqs = QuestionsList.model_validate_json(response)
                mcqs_json = mcqs.model_dump_json()
                self.safely_write_file(file_path_new, mcqs_json)

    def run(self):
        for idx in range(self.pointer, len(self.output_subdir_paths)):
            print(f"Step {self.pipeline[idx].__name__} started")
            start_time = time.time()
            if idx == 0:
                # the first tool is a special case
                self.pipeline[idx](self.output_subdir_paths[0])
            else:
                self.pipeline[idx](
                    self.output_subdir_paths[idx - 1],
                    self.output_subdir_paths[idx]
                )
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Step {self.pipeline[idx].__name__} took {self.format_time(elapsed_time)} (hh:mm:ss)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <file_path> <title>")
        sys.exit(1)

    file_path = sys.argv[1]
    title = sys.argv[2]

    try:
        conversor = Conversion(file_path, title)
        conversor.run()
    except Exception as e:
        print(e)
