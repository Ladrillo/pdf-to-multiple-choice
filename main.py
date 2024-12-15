import sys
import time
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

temperature = 0
num_ctx = 16384
# model = "llama3.3"
# model = "gpt-4o"
model = "llama3.3:70b-instruct-q6_K"

pipeline = [
    'pdf_convert',
    'markdown_split',
    'markdown_classify',
    'markdown_clean',
    'quiz_create',
]


class PipelineCompleteError(Exception):
    """Exception raised when the pipeline is complete."""
    pass


def get_pointer(output_dir_path, subdir_paths):
    pointer = 0
    if not output_dir_path.exists() or not output_dir_path.is_dir():
        return pointer
    else:
        for subdir_path in subdir_paths:
            if subdir_path.exists() and subdir_path.is_dir():
                pointer += 1
            else:
                print(f"Pointer is {pointer}: {pipeline[pointer]}")
                return pointer
    raise PipelineCompleteError(
        "The pipeline is complete: all subfolders exist."
    )


def get_folders(path):
    file_path = Path(path)
    output_dir_path = file_path.parent / file_path.stem
    subdir_paths = [
        output_dir_path / f"{idx + 1}_{val}" for idx, val in enumerate(pipeline)
    ]
    result = (output_dir_path, subdir_paths)
    return result


def make_folders(path):
    (output_dir_path, subdir_paths) = get_folders(path)
    pointer = get_pointer(output_dir_path, subdir_paths)
    if pointer == 0:
        if output_dir_path.exists() and output_dir_path.is_dir():
            shutil.rmtree(output_dir_path)
        output_dir_path.mkdir(parents=True, exist_ok=True)
    for subdir_path in subdir_paths[pointer:]:
        if subdir_path.exists() and subdir_path.is_dir():
            shutil.rmtree(subdir_path)
        subdir_path.mkdir(parents=True, exist_ok=True)
    return (subdir_paths, pointer)


def call_model(messages):
    if model == "gpt-4o":
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    else:
        response = chat(
            model=model,
            options={"temperature": temperature, "num_ctx": num_ctx},
            messages=messages
        )
        return response['message']['content']


def pdf_convert(pdf_path, output_path):
    markdown = pymupdf4llm.to_markdown(pdf_path)
    clean_markdown = markdown.encode('utf-8', errors='ignore').decode('utf-8')
    output_file_path = output_path / "complete.md"
    output_file_path.write_text(clean_markdown, encoding='utf-8')


def markdown_split(input_path, output_path):
    print(f"Splitting Markdown to {output_path}...")
    split_by = [("#", "H1"), ("##", "H2"), ("###", "H3")] #, ("####", "H4")]
    splitter = MarkdownHeaderTextSplitter(split_by, strip_headers=False)
    markdown_path = list(input_path.iterdir())[0]
    markdown = markdown_path.read_text(encoding='utf-8')
    splits = splitter.split_text(markdown)
    contents = [splits[i].page_content for i in range(len(splits))]
    for idx, content in enumerate(contents):
        file_name = f"fragment_{idx + 1}.md"
        file_path = output_path / file_name
        file_path.write_text(content, encoding='utf-8')
    print(f"Splitting done")


def markdown_classify(input_path, output_path):
    print(f"Classifying Markdown to {output_path}...")
    for file_path in input_path.iterdir():
        sys.stdout.write(f"\rClassifying {file_path.stem}...")
        sys.stdout.flush()
        markdown = file_path.read_text(encoding='utf-8')
        prompt_classify = "Classify as either \"Body\" or \"Paratext\":\n"
        response = call_model([
            {"role": "system", "content": prm.CLASSIFY},
            {"role": "user", "content": prompt_classify + markdown},
        ])
        parameter = "body" if "body" in response.lower() else "paratext"
        file_name = f"{file_path.stem}_{parameter}.md"
        file_path_new = output_path / file_name
        file_path_new.write_text(markdown, encoding='utf-8')
    print(f"Clasifying done")


def markdown_clean(input_path, output_path):
    print(f"Cleaning Markdown to {output_path}...")
    for file_path in input_path.iterdir():
        sys.stdout.write(f"\rCleaning {file_path.stem}...")
        sys.stdout.flush()
        markdown = file_path.read_text(encoding='utf-8')
        response = call_model([
            {"role": "system", "content": prm.CLEAN},
            {"role": "user", "content": markdown}
        ])
        clean_markdown = mdformat.text(response)
        file_name = f"{file_path.stem}_clean.md"
        file_path_new = output_path / file_name
        file_path_new.write_text(clean_markdown, encoding='utf-8')
    print(f"Cleaning done")


def quiz_create(input_path, output_path):
    print(f"Creating MCQs to {output_path}...")
    for file_path in input_path.iterdir():
        sys.stdout.write(f"\rCreating MCQs {file_path.stem}...")
        sys.stdout.flush()
        markdown = file_path.read_text(encoding='utf-8')
        file_name = f"{file_path.stem}_quiz.md"
        file_path_new = output_path / file_name
        if "_paratext_" in file_path.stem:
            file_path_new.write_text("<!-- paratext -->", encoding='utf-8')
        else:
            response = call_model([
                {'role': 'system', 'content': prm.MCQ},
                {'role': 'user', 'content': markdown},
            ])
            response_improved = call_model([
                {'role': 'system', 'content': prm.MCQ},
                {'role': 'user', 'content': markdown},
                {'role': 'assistant', 'content': response},
                {'role': 'user', 'content': prm.IMPROVE_MCQ},
            ])
            file_path_new.write_text(response_improved, encoding='utf-8')
    print(f"Creating MCQs done")


tools = [
    pdf_convert,
    markdown_split,
    markdown_classify,
    markdown_clean,
    quiz_create,
]


def process(pdf_path):
    (subdir_paths, pointer) = make_folders(pdf_path)
    for idx in range(pointer, len(subdir_paths)):
        if idx == 0:
            # the first tool is a special case
            tools[idx](pdf_path, subdir_paths[0])
        else:
            tools[idx](subdir_paths[idx - 1], subdir_paths[idx])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        process(file_path)
    except Exception as e:
        print(e)
