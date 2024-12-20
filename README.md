# PDF to Multiple-Choice Questions

A Python utility for converting PDF documents into multiple-choice questions stored in Markdown files.

The documents must be of decent quality as no OCR is performed for now, only straight text extraction.

## Usage

Create a `.env` file inside `.devcontainer` for your development environment variables.

Create a `prompts.py` file at the root of the project for your custom prompts.

Open the project inside a [DevContainer](https://code.visualstudio.com/docs/devcontainers/containers).

The [Ollama](https://github.com/ollama/ollama) server must be up and running on your system.

Configure your Docker settings to "Enable host networking".

```bash
python main.py ./sample.pdf 'Programming For Newbies' # path and description
```
