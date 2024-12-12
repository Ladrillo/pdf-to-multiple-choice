import sys
import pathlib
from pathlib import Path
import mdformat
import shutil
import pymupdf4llm
from ollama import chat
from langchain_text_splitters import MarkdownHeaderTextSplitter

try:
    import prompts as prm
except ImportError:
    import prompts_default as prm
    import warnings
    warnings.warn("Using default constants.")

temperature = 0
num_ctx = 16384
model = "llama3.3"
# model = "llama3.3:70b-instruct-q6_K"


def create_output_dir(path):
    file_path = Path(path)
    stem = file_path.stem
    parent_dir = file_path.parent
    output_dir = parent_dir / stem
    if output_dir.exists() and output_dir.is_dir():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Folder '{stem}' created at {output_dir}")
    return output_dir


def turn_pdf_to_markdown(path):
    file_path = Path(path)
    stem = file_path.stem
    output_dir = create_output_dir(path)
    output_path = f"{output_dir}/{stem}.md"
    markdown = pymupdf4llm.to_markdown(path)
    pathlib.Path(output_path).write_bytes(markdown.encode())
    return (stem, markdown, output_dir)


def split_markdown_by_headers(title, markdown, output_dir):
    headers_to_split_on = [
        ("#", "H1"),
        ("##", "H2"),
        ("###", "H3"),
        ("####", "H4"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on, strip_headers=False
    )
    md_header_splits = markdown_splitter.split_text(markdown)
    contents = [
        md_header_splits[i].page_content for i in range(len(md_header_splits))
    ]
    for idx, content in enumerate(contents):
        file_name = f"{title}_fragment_{idx + 1}.md"
        file_path = output_dir / file_name
        file_path.write_text(content, encoding='utf-8')
    return contents


def reformat_markdowns_by_LLM(title, markdowns, output_dir):
    for idx, content in enumerate(markdowns):
        word_count = len(content.split())
        print(f"RATING a Markdown {word_count} words long, {
              idx + 1} / {len(markdowns)}")
        prompt_classify = f"The following text comes from a book on {title}, it's about {
            word_count} words in length. Classify it as either \"Body\" or \"Paratext\":\n\n"
        response_classify = chat(model=model, options={"temperature": temperature, "num_ctx": num_ctx}, messages=[
            {
                'role': 'system',
                'content': prm.YOU_RATE_CONTENT
            },
            {
                'role': 'user',
                'content': prompt_classify + content
            },
        ])
        response_classify_content = response_classify['message']['content']
        print(f"{idx + 1} --> ", response_classify_content)

        def should_process(s): return "body" in s.lower()
        file_name_clean = f"{title}_clean_{idx + 1}.md"
        file_path_clean = output_dir / file_name_clean
        file_name_quiz = f"{title}_QUIZ_{idx + 1}.md"
        file_path_quiz = output_dir / file_name_quiz
        if should_process(response_classify_content):
            print(f"Cleaning Markdown {idx + 1} / {len(markdowns)}")
            response_cleaning = chat(model=model, options={"temperature": temperature, "num_ctx": num_ctx}, messages=[
                {
                    'role': 'system',
                    'content': prm.YOU_ARE_A_MARKDOWN_CLEANER
                },
                {
                    'role': 'user',
                    'content': content
                },
            ])
            response_cleaning_content = response_cleaning['message']['content']
            clean_markdown = mdformat.text(response_cleaning_content)
            file_path_clean.write_text(clean_markdown, encoding='utf-8')

            print(f"Creating Quiz     {idx + 1} / {len(markdowns)}")
            response_quiz = chat(model=model, options={"temperature": temperature, "num_ctx": num_ctx}, messages=[
                {
                    'role': 'system',
                    'content': prm.YOU_ARE_A_MULTIPLE_CHOICE_QUIZ_BUILDER
                },
                {
                    'role': 'user',
                    'content': clean_markdown
                },
            ])
            response_quiz_content = response_quiz['message']['content']
            formatted_quiz = mdformat.text(response_quiz_content)
            file_path_quiz.write_text(formatted_quiz, encoding='utf-8')
        else:
            file_path_clean.write_text("<!-- paratext -->", encoding='utf-8')
            file_path_quiz.write_text("<!-- paratext -->", encoding='utf-8')


def process(pdf_path):
    title, markdown, output_dir = turn_pdf_to_markdown(pdf_path)
    split_markdowns = split_markdown_by_headers(title, markdown, output_dir)
    reformat_markdowns_by_LLM(title, split_markdowns, output_dir)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        process(file_path)
    except Exception as e:
        print(e)
