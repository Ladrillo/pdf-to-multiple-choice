# PDF to Multiple-Choice Questions

A Python utility for converting PDF documents into multiple-choice questions stored in Markdown files.

The documents must be of decent quality as no OCR is performed for now, only straight text extraction.

## Usage

Create a `.env` file inside `.devcontainer` to keep your development environment variables.

Open the project inside a [DevContainer](https://code.visualstudio.com/docs/devcontainers/containers).

You must have the [Ollama](https://github.com/ollama/ollama) server running on your system.

```bash
python main.py ./sample.pdf
```
