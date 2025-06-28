import os; import sys
common_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../common"))
sys.path.append(common_dir)
import argparse
import re

# Define the system prompt for your Tcl application
SYSTEM_PROMPT = """
You are a helpful assistant that answers questions using Tcl code.
You can execute Tcl code on behalf of the user by wrapping it in a ```tcl code block. This only applies to the first code block in the message.
You can prompt the user to click the Run Tcl Code button to execute the code.
If the user does click the button, the API will return one or more of the following:
- output: output produced by the code block (if any), which may include error messages
- result: the result of the last command in the code block (if non-empty)
- silent completion: if the code produced no output and no result
You should prefer returning a result over using puts to produce output.
If the user asks for something else, you should provide a regular response.
""".strip()

# OpenAI chat models:
# ['gpt-4-0613', 'gpt-4', 'gpt-3.5-turbo', 'gpt-4-1106-preview', 'gpt-3.5-turbo-1106', 'gpt-4-0125-preview', 'gpt-4-turbo-preview', 'gpt-3.5-turbo-0125', 'gpt-4-turbo', 'gpt-4-turbo-2024-04-09', 'gpt-4o', 'gpt-4o-2024-05-13', 'gpt-4o-mini-2024-07-18', 'gpt-4o-mini', 'gpt-4o-2024-08-06', 'chatgpt-4o-latest', 'o1-preview-2024-09-12', 'o1-preview', 'o1-mini-2024-09-12', 'o1-mini', 'gpt-4o-2024-11-20', 'gpt-4.5-preview', 'gpt-4.5-preview-2025-02-27', 'gpt-4o-search-preview-2025-03-11', 'gpt-4o-search-preview', 'gpt-4o-mini-search-preview-2025-03-11', 'gpt-4o-mini-search-preview', 'gpt-4.1-2025-04-14', 'gpt-4.1', 'gpt-4.1-mini-2025-04-14', 'gpt-4.1-mini', 'gpt-4.1-nano-2025-04-14', 'gpt-4.1-nano', 'gpt-3.5-turbo-16k']

# Exclude models with a date postfix (e.g., gpt-4o-mini-2024-07-18)
VALID_MODELS_PATTERN = r"^(gpt-4|gpt-3|o1|microsoft|meta-llama)[^-]*(?:-(?!\d{4}-\d{2}(?:-\d{2})?$)[^-]*)*$"
PREFERRED_MODELS = ["gpt-4o-mini", "microsoft/Phi-4"]

def tclai_gradio():
    from dotenv import load_dotenv
    import gradio_server as ai
    from openai import OpenAI  # replace if using a different AI library

    # Load your API key(s) from the environment
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Set the completion command for your AI model
    openai = OpenAI()
    models = sorted([model.id for model in openai.models.list() if re.match(VALID_MODELS_PATTERN, model.id)])
    default_model = next((m for m in PREFERRED_MODELS if m in models), models[0] if models else None)
    completions_command = openai.chat.completions.create

    # Test for the OpenAI API key
    if openai_api_key:
        print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
    else:
        raise ValueError("OpenAI API Key not set")

    # Start the Gradio interface
    ai.TclAI(completions_command, SYSTEM_PROMPT, default_model=default_model, all_models=models, dummy=False, app_name="Tcl")

def tclai_clipboard():
    import clipboard_monitor
    clipboard_monitor.run(SYSTEM_PROMPT)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clipboard", action="store_true", help="use the clipboard monitor instead of gradio")
    args = parser.parse_args()
    if args.clipboard:
        tclai_clipboard()
    else:
        tclai_gradio()
