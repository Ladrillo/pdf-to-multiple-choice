import sys
from string import Template
from pathlib import Path
import mdformat
import shutil
import pymupdf4llm
from ollama import chat
from openai import OpenAI
from langchain_text_splitters import MarkdownHeaderTextSplitter

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


class Conversion():
    def __init__(self, pdf_path, title):
        self.temperature = 0
        self.num_ctx = 8192
        self.model = "gpt-4o-mini"
        self.title = title
        self.pdf_path = pdf_path
        self.pipeline = [
            self.pdf_convert,
            self.markdown_split,
            self.markdown_classify,
            self.markdown_clean,
            self.quiz_create,
        ]
        self.output_dir_path = self.get_output_dir_path()
        self.output_subdir_paths = self.get_output_subdir_paths()
        self.pointer = self.get_pointer()
        self.make_folders()

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

    def call_model(self, messages):
        if "gpt-4o" in self.model:
            response = client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
            )
            return response.choices[0].message.content
        else:
            response = chat(
                model=self.model,
                options={"temperature": self.temperature,
                         "num_ctx": self.num_ctx},
                messages=messages,
            )
            return response['message']['content']

    def pdf_convert(self, output_path):
        markdown = pymupdf4llm.to_markdown(self.pdf_path)
        clean_markdown = markdown.encode(
            'utf-8', errors='ignore').decode('utf-8')
        output_file_path = output_path / "complete.md"
        output_file_path.write_text(clean_markdown, encoding='utf-8')

    def markdown_split(self, input_path, output_path):
        print(f"Splitting Markdown to {output_path}...")
        split_by = [("#", "H1"), ("##", "H2"), ("###", "H3"), ("####", "H4")]
        splitter = MarkdownHeaderTextSplitter(split_by, strip_headers=False)
        markdown_path = sorted(input_path.iterdir())[0]
        markdown = markdown_path.read_text(encoding='utf-8')
        splits = splitter.split_text(markdown)
        contents = [splits[i].page_content for i in range(len(splits))]
        for idx, content in enumerate(contents):
            file_name = f"fragment_{idx + 1}.md"
            file_path = output_path / file_name
            file_path.write_text(content, encoding='utf-8')
        print(f"Splitting done")

    def markdown_classify(self, input_path, output_path):
        print(f"Classifying Markdown to {output_path}...")
        instructions = Template(prm.CLASSIFY)
        instructions_sub = instructions.substitute(doc_title=self.title)
        for file_path in sorted(input_path.iterdir()):
            sys.stdout.write(f"\rClassifying {file_path.stem}...")
            sys.stdout.flush()
            markdown = file_path.read_text(encoding='utf-8')
            response = self.call_model([
                {"role": "system", "content": instructions_sub},
                {"role": "user", "content": markdown},
            ])
            parameter = "body" if "body" in response.lower() else "paratext"
            file_name = f"{file_path.stem}_{parameter}.md"
            file_path_new = output_path / file_name
            file_path_new.write_text(markdown, encoding='utf-8')
        print(f"Clasifying done")

    def markdown_clean(self, input_path, output_path):
        print(f"Cleaning Markdown to {output_path}...")
        for file_path in sorted(input_path.iterdir()):
            sys.stdout.write(f"\rCleaning {file_path.stem}...")
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
                file_path_new.write_text(clean_markdown, encoding='utf-8')
        print(f"Cleaning done")

    def quiz_create(self, input_path, output_path):
        print(f"Creating MCQs to {output_path}...")
        for file_path in sorted(input_path.iterdir()):
            sys.stdout.write(f"\rCreating MCQs {file_path.stem}...")
            sys.stdout.flush()
            markdown = file_path.read_text(encoding='utf-8')
            file_name = f"{file_path.stem}_quiz.md"
            file_path_new = output_path / file_name
            if "_paratext" in file_path.stem:
                file_path_new.write_text("<!-- paratext -->", encoding='utf-8')
            else:
                response = self.call_model([
                    {'role': 'system', 'content': prm.MCQ},
                    {'role': 'user', 'content': markdown},
                ])
                response_improved = self.call_model([
                    {'role': 'system', 'content': prm.MCQ},
                    {'role': 'user', 'content': markdown},
                    {'role': 'assistant', 'content': response},
                    {'role': 'user', 'content': prm.IMPROVE_MCQ},
                ])
                file_path_new.write_text(response_improved, encoding='utf-8')
        print(f"Creating MCQs done")

    def run(self):
        for idx in range(self.pointer, len(self.output_subdir_paths)):
            if idx == 0:
                # the first tool is a special case
                self.pipeline[idx](self.output_subdir_paths[0])
            else:
                self.pipeline[idx](
                    self.output_subdir_paths[idx - 1],
                    self.output_subdir_paths[idx]
                )


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
