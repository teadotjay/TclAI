import os; import sys; sys.path.append("python")
from dotenv import load_dotenv
import gradio_server as ai
from openai import OpenAI  # replace if using a different AI library

# Load your API key(s) from the environment
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Set the completion command for your AI model
openai = OpenAI()
DEFAULT_MODEL = "gpt-4o-mini"
MODELS = sorted([model.id for model in openai.models.list()])
completions_command = lambda messages, model=DEFAULT_MODEL: \
    openai.chat.completions.create(model=model, messages=messages, stream=True)

# Define the system prompt for your Tcl application
system_prompt = """
You are a helpful assistant that answers questions using Tcl code.
The user can execute *first* Tcl code block in your response using the 'Run Tcl Code' button.
Clicking the Run Tcl Code button will execute this code block and provide the output in a series of code blocks defined below:
- output: output produced by the code block (if any), which may include error messages
- result: the result of the last command in the code block (if non-empty)
- "silent completion": if the code block does not produce any output and the result is empty
If your response calls for Tcl code, put it in a Tcl code block, like this:
    ```tcl
    <tcl code>
    ```
In general, you should prefer delivering a result over using puts to produce output.
Do not call `return` outside of a function.
If the user asks for something else, you will provide a regular response.
"""

# Test for the OpenAI API key
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    raise ValueError("OpenAI API Key not set")

# Start the Gradio interface
ai.TclAI(completions_command, system_prompt, default_model=DEFAULT_MODEL, all_models=MODELS, dummy=False, app_name="Tcl")