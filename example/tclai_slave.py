import os; import sys; sys.path.append("common")
import argparse

# Define the system prompt for your Tcl application
SYSTEM_PROMPT = """
You are a helpful assistant that answers questions using Tcl code.
You can execute Tcl code on behalf of the user by wrapping it in a tcl code block with the first line as "### tcl".
You can prompt the user to click the Run Tcl Code button to execute the code.
If the user does click the button, the API will return one or more of the following:
- output: output produced by the code block (if any), which may include error messages
- result: the result of the last command in the code block (if non-empty)
- silent completion: if the code produced no output and no result
In general, you should prefer returning a result over using puts to produce output.
If the user asks for something else, you will provide a regular response.
""".strip()

def tclai_gradio():
    from dotenv import load_dotenv
    import gradio_server as ai
    from openai import OpenAI  # replace if using a different AI library

    # Load your API key(s) from the environment
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Set the completion command for your AI model
    openai = OpenAI()
    default_model = "gpt-4o-mini"
    models = sorted([model.id for model in openai.models.list()])
    completions_command = lambda messages, model=default_model: \
        openai.chat.completions.create(model=model, messages=messages, stream=True)

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
