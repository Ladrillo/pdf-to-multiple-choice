from transformers import AutoTokenizer
import tiktoken
import sys

# MODEL_ID = "meta-llama/Llama-3.3-70B-Instruct"
MODEL_ID = "microsoft/deberta-base"
# MODEL_ID = "gpt-4o"


def count_tokens(input_data, model_id=MODEL_ID, is_file_path=False):
    """
    Counts the number of tokens in the given text or text from a file using a specified tokenizer model.

    Args:
        input_data (str): The text or file path containing the text.
        model_id (str): Model ID to load the tokenizer.
        is_file_path (bool): If True, treats input_data as a file path.

    Returns:
        int: The number of tokens in the text.
    """
    try:
        if is_file_path:
            with open(input_data, 'r') as file:
                text = file.read()
        else:
            text = input_data
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{input_data}' was not found.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")

    try:
        encoder = tiktoken.encoding_for_model(MODEL_ID)
        encoded = encoder.encode(text)
        return len(encoded)
    except Exception as e:
        print(f"Not an OpenAI model: {e}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        tokens = tokenizer.tokenize(text)
        return len(tokens)
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tokencounter.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        num_tokens = count_tokens(file_path, is_file_path=True)
        print(f"Number of tokens in your text: {num_tokens}")
    except Exception as e:
        print(e)
