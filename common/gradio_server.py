import gradio as gr
import re
import requests
import time  # Import the time module
import exec_client
import os
import random

# Get the port and API key from the environment variables
API_PORT = int(os.environ.get('API_PORT'))
API_KEY = os.environ.get('API_KEY')
API_SERVER = os.environ.get('API_SERVER')  # The server is running on the same machine

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
            result, output = await exec_client.execute_script(tcl_code, API_SERVER, API_PORT, API_KEY)
            
            # Format the response
            api_result = ""
            if output:
                api_result += f"output:\n```\n{output}\n```\n"
            if result:
                api_result += f"result:\n```\n{result}\n```\n"
        except requests.exceptions.RequestException as e:
            api_result = f"Error calling API: {e}"
        
        # Prepare the chat message
        #print(f"{api_result = }")
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

def TclAI(completions_command, system_message, default_model="gpt-4o-mini", all_models=None, dummy=False, app_name="Tcl"):
    """
    Launches a Gradio interface for the TclAI chatbot.
    Args:
        completions_command: The function to call for generating completions.
        system_message: The system message to use for the chatbot.
        default_model: The default model to use.
        all_models: List of available models.
        dummy: If True, use a dummy bot for testing.
        app_name: The name of the application.
    """

    def add_message(history, message):
        for x in message["files"]:
            history.append({"role": "user", "content": {"path": x}})
        if message["text"] is not None:
            history.append({"role": "user", "content": message["text"]})
        return history, gr.MultimodalTextbox(value=None, interactive=False)

    def bot_dummy(history: list, model_name: str):
        bot_message = random.choice([
            f'{model_name} says:\n```tcl\nputs "Incrementing"\nincr i\n```',
            f'{model_name} says:\n```tcl\nerror "something went wrong"\n```',
            f"{model_name} says:\nThis ain't tcl"
        ])
        history.append({"role": "assistant", "content": ""})
        for character in bot_message:
            history[-1]['content'] += character
            time.sleep(0.01)
            yield history, gr.update(interactive=False)
        
        # Enable/disable the button based on the bot's response
        enable_tcl_button = check_for_tcl_code(history)
        yield history, gr.update(interactive=enable_tcl_button)

    def bot_chatgpt(history: list, model_name):
        messages = [{"role": "system", "content": system_message}] + history
        stream = completions_command(messages, model_name)
        history.append({"role": "assistant", "content": ""})
        for chunk in stream:
            history[-1]['content'] += chunk.choices[0].delta.content or ''
            yield history, gr.update(interactive=False)
        
        # Enable/disable the button based on the bot's response
        enable_tcl_button = check_for_tcl_code(history)
        yield history, gr.update(interactive=enable_tcl_button)

    bot = bot_dummy if dummy else bot_chatgpt
        
    def undo(retry_data: gr.UndoData, history: list[gr.MessageDict]):
        """
        Undo the last message in the chat history.
        """
        history = history[:retry_data.index]
        last_message = retry_data.value
        return history, last_message, gr.update(interactive=check_for_tcl_code(history))

    def change_model(model_name: str, history: list[gr.MessageDict]):
        """
        Change the model used for generating completions.
        """
        history.append({"role": "assistant", "content": f"Model {model_name} selected."})
        return history

    # Create the Gradio interface
    with gr.Blocks() as demo:
        modelPicker = gr.Dropdown(
            label="Model",
            choices=all_models,
            value=default_model,
            interactive=True,
        )
        chatbot = gr.Chatbot(elem_id="chatbot", type="messages", editable="all", height=800,
            label="TclAI", avatar_images = (None, "https://www.tcl-lang.org/images/plume.png"),
            value=[{"role": "assistant", "content": f"Connected to {app_name}, using {default_model}. How can I help you?"}])
        chatbot.show_copy_all_button = True
        run_tcl_button = gr.Button("Run Tcl Code", interactive=False)  # Initially disabled
        modelPicker.change(change_model, [modelPicker, chatbot], [chatbot])
        
        chat_input = gr.MultimodalTextbox(
            interactive=True,
            file_count="multiple",
            placeholder="Enter message or upload file...",
            show_label=False,
            sources=["upload"],
        )
        chatbot.undo(undo, chatbot, [chatbot, chat_input, run_tcl_button])
        chat_msg = chat_input.submit(
            add_message, [chatbot, chat_input], [chatbot, chat_input]
        )
        bot_msg = chat_msg.then(bot, [chatbot, modelPicker], [chatbot, run_tcl_button], api_name="bot_response")
        bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

        run_tcl_button.click(execute_tcl_code, [chatbot], [chatbot, run_tcl_button]).then(
            bot, [chatbot, modelPicker], [chatbot, run_tcl_button]
        )

    demo.launch(inbrowser=True, share=False)
