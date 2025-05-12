import os; import sys; sys.path.append("python")
from dotenv import load_dotenv
import gradio_server as ai
from openai import OpenAI  # replace if using a different AI library

# Load your API key(s) from the environment
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Set the bot function to use (bot_chatgpt or bot_dummy for testing)
bot = "bot_chatgpt"

# Set the completion command for your AI model
openai = OpenAI()
MODEL = "gpt-4o-mini"
completions_command = lambda messages: \
    openai.chat.completions.create(model=MODEL, messages=messages, stream=True)

# Define the system prompt for your Tcl application
system_prompt = """
You are a helpful assistant that answers questions using Tcl code.
The user can execute Tcl code using the 'Run Tcl Code' button.
On clicking Run Tcl Code, the user message will hold the API response in the following format:
    stdout:
    ```
    <stdout output>
    ```
    stderr:
    ```
    <stderr output>
    ```
    result:
    ```
    <result>
    ```
If there is no output, the API will respond "silent completion" and the stdout, stderr, and result sections will be empty.
The stdout, stderr, and result sections will only be included if there is correspodning output.

If your response calls for Tcl code, you will provide it in the following format:
    ```tcl
    <tcl code>
    ```

If the user asks for something else, you will provide a regular response.
"""

# Test for the OpenAI API key
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    raise ValueError("OpenAI API Key not set")

# Start the Gradio interface
ai.TclAI(completions_command, system_prompt, bot=bot)