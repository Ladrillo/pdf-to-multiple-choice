# PDF to Multiple-Choice Questions

A Python utility for converting PDF documents into multiple-choice questions in Markdown.

The documents must be of decent quality as no OCR is performed, only straight text extraction.

## Usage

Open the project inside a [DevContainer](https://code.visualstudio.com/docs/devcontainers/containers).

You must have the [Ollama](https://github.com/ollama/ollama/tree/main) server running on your system.

```bash
python main.py documents/sample.pdf
```
