import gradio as gr
import re
import requests
import time  # Import the time module
import exec_client
import os
from dotenv import load_dotenv
from openai import OpenAI
import random

# Get the port and API key from the environment variables
API_PORT = int(os.environ.get('API_PORT'))
API_KEY = os.environ.get('API_KEY')
API_SERVER = os.environ.get('API_SERVER')  # The server is running on the same machine

def echo(message, history):
    """
    Simulates a bot response.  It will include TCL code if the user's message
    contains the word "tcl".
    """
    if "tcl" in message.lower():
        return "Here's some Tcl code:\n```tcl\nset myVar 10\nputs \"The value is: $myVar\"\n```"
    else:
        return "This is a regular response."

def extract_tcl_code(text):
    """
    Extracts TCL code from a string.

    Args:
        text: The string to search for TCL code.

    Returns:
        The TCL code as a string, or None if no code is found.
    """
    match = re.search(r"```tcl\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

async def execute_tcl_code(chat_history):
    """
    Executes the TCL code found in the last bot response using an external API.

    Args:
        chat_history: The chat history.

    Returns:
        The updated chat history with the result of the TCL code execution.
    """

    if not chat_history:
        chat_history.append({"role": "system", "content": "No chat history yet."})
        return chat_history, gr.update(interactive=False)

    last_bot_response = chat_history[-1]["content"]
    tcl_code = extract_tcl_code(last_bot_response)

    if tcl_code:
        try:
            # Call the external API to execute the TCL code
            result, stdout, stderr = await exec_client.execute_script(tcl_code, API_SERVER, API_PORT, API_KEY)
            
            # Format the response
            api_result = ""
            if stdout:
                api_result += f"stdout:\n```\n{stdout}\n```\n"
            if stderr:
                api_result += f"stderr:\n```\n{stderr}\n```\n"
            if result:
                api_result += f"result:\n```\n{result}\n```\n"
        except requests.exceptions.RequestException as e:
            api_result = f"Error calling API: {e}"
        
        # Prepare the chat message
        chat_history.append(gr.ChatMessage(role="user", content=api_result or "silent completion", 
            metadata={"title": "API Response"}))
        
        # Disable the button after execution
        return chat_history, gr.update(interactive=False)
    else:
        chat_history.append({"role": "system", "content": "No Tcl code found to execute."})
        return chat_history, gr.update(interactive=False)

def check_for_tcl_code(chat_history):
    """
    Checks if the last bot response contains TCL code.  This function is used
    to determine whether to enable or disable the "Run Tcl Code" button.

    Args:
        chat_history: The chat history.

    Returns:
        True if TCL code is found, False otherwise.
    """
    if not chat_history:
        return False
    last_bot_response = chat_history[-1]["content"]
    return bool(extract_tcl_code(last_bot_response))

# Initialization
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
MODEL = "gpt-4o-mini"
openai = OpenAI()

system_message = """
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

def add_message(history, message):
    for x in message["files"]:
        history.append({"role": "user", "content": {"path": x}})
    if message["text"] is not None:
        history.append({"role": "user", "content": message["text"]})
    return history, gr.MultimodalTextbox(value=None, interactive=False)

def bot_dummy(history: list):
    bot_message = random.choice([
        '```tcl\nputs "Incrementing"\nincr i\n```',
        '```tcl\nputs stderr "something went wrong"\n```',
        "This ain't tcl"
    ])
    history.append({"role": "assistant", "content": ""})
    for character in bot_message:
        history[-1]['content'] += character
        time.sleep(0.01)
        yield history, gr.update(interactive=False)
    
    # Enable/disable the button based on the bot's response
    enable_tcl_button = check_for_tcl_code(history)
    yield history, gr.update(interactive=enable_tcl_button)

def bot_chatgpt(history: list):
    messages = [{"role": "system", "content": system_message}] + history
    stream = openai.chat.completions.create(model=MODEL, messages=messages, stream=True)
    history.append({"role": "assistant", "content": ""})
    for chunk in stream:
        history[-1]['content'] += chunk.choices[0].delta.content or ''
        yield history, gr.update(interactive=False)
    
    # Enable/disable the button based on the bot's response
    enable_tcl_button = check_for_tcl_code(history)
    yield history, gr.update(interactive=enable_tcl_button)

# Set the bot function to use
bot = bot_chatgpt

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(elem_id="chatbot", type="messages", editable="all")
    run_tcl_button = gr.Button("Run Tcl Code", interactive=False)  # Initially disabled
    
    chat_input = gr.MultimodalTextbox(
        interactive=True,
        file_count="multiple",
        placeholder="Enter message or upload file...",
        show_label=False,
        sources=["upload"],
    )
    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    bot_msg = chat_msg.then(bot, chatbot, [chatbot, run_tcl_button], api_name="bot_response")
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

    run_tcl_button.click(execute_tcl_code, [chatbot], [chatbot, run_tcl_button]).then(
        bot, chatbot, [chatbot, run_tcl_button]
    )

demo.launch(inbrowser=True)
