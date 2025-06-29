import gradio as gr
import re
import requests
import time  # Import the time module
import exec_client
import os
import random
import sys
sys.path.append(".")
from token_count import get_token_count, get_token_count_with_tiktoken
import mimetypes
from pathlib import Path
import uuid
import PyPDF2
import tempfile
import json
import re

# Get the port and API key from the environment variables
API_PORT = int(os.environ.get('API_PORT'))
API_KEY = os.environ.get('API_KEY')
API_SERVER = os.environ.get('API_SERVER')  # The server is running on the same machine

file_content_store = {}

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text.strip() or "[No text found in PDF]"
    except Exception as e:
        return f"[Failed to extract PDF: {e}]"

def extract_text_from_file(file_path):
    mime, _ = mimetypes.guess_type(file_path)
    ext = Path(file_path).suffix.lower()
    print("Uploaded file:", file_path, "MIME type:", mime, "Extension:", ext)
    try:
        if mime == "application/pdf":
            text = extract_text_from_pdf(file_path)
        elif (mime and mime.startswith("text")) or ext in [".md", ".markdown", ".py", ".csv", ".json", ".yaml", ".yml"]:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            text = f"[Unsupported file type: {Path(file_path).name}]"
    finally:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Failed to delete temp file {file_path}: {e}")
    return text

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
            file_name = Path(x).name
            file_content = extract_text_from_file(x)
            file_id = str(uuid.uuid4())
            file_content_store[file_id] = file_content
            # Use a plain dict with metadata
            history.append({
                "role": "user",
                "content": "",
                "metadata": {"id": file_id, "title": file_name}
            })
        if message["text"] is not None:
            history.append({"role": "user", "content": message["text"]})
        return history, gr.MultimodalTextbox(value=None, interactive=False)

    def add_note(history, message):
        note_text = message.get("text") if isinstance(message, dict) else message
        if note_text:
            history.append({"role": "assistant", "content": note_text, "metadata": {"title": "Note"}})
        return history, gr.MultimodalTextbox(value=None, interactive=True)

    def format_token_count(token_count):
        if token_count is None or token_count == "--":
            return "**Tokens:** --"
        try:
            return f"**Tokens:** {int(token_count)}"
        except Exception:
            return f"**Tokens:** {token_count}"

    def bot_dummy(history: list, model_name: str, system_message: str):
        yield history, gr.update(interactive=False), gr.update(interactive=False), format_token_count(None)
        bot_message = random.choice([
            f'{model_name} says:\n```tcl\nputs "Incrementing"\nincr i\n```',
            f'{model_name} says:\n```tcl\nerror "something went wrong"\n```',
            f"{model_name} says:\nThis ain't tcl"
        ])
        history.append({"role": "assistant", "content": ""})
        for character in bot_message:
            history[-1]['content'] += character
            time.sleep(0.01)
            yield history, gr.update(interactive=False), gr.update(interactive=False), format_token_count(None)
        enable_tcl_button = check_for_tcl_code(history)
        token_count = get_token_count_with_tiktoken(history, model=model_name)
        # Combine updates for the chat_input (third and fifth outputs)
        yield history, gr.update(interactive=enable_tcl_button), gr.update(interactive=True), format_token_count(token_count)

    def format_messages(history, system_message):
        messages = [{"role": "system", "content": system_message}]
        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")
            metadata = msg.get("metadata") or {}
            file_id = metadata.get("id")
            if metadata.get("title") in ["Note", "Info"]:
                continue  # Skip notes for the bot
            if file_id and file_id in file_content_store:
                # Add file content to the message
                file_content = file_content_store[file_id]
                content = f"{content}\n\nFILE CONTENT:\n{file_content}"
            messages.append({"role": role, "content": content})
        return messages

    def bot_chatgpt(history: list, model_name: str, system_message: str):
        messages = format_messages(history, system_message)

        # Disable input at the start of streaming
        yield history, gr.update(interactive=False), gr.update(interactive=False), format_token_count(None)
        stream = completions_command(
            model=model_name,
            messages=messages,
            stream=True)
        history.append({"role": "assistant", "content": ""})
        for chunk in stream:
            history[-1]['content'] += chunk.choices[0].delta.content or ''
            yield history, gr.update(interactive=False), gr.update(interactive=False), format_token_count(None)

        # Check if response contains tcl code and enable/disable the button
        enable_tcl_button = check_for_tcl_code(history)

        # Compute token count using formatted messages (sans system prompt) + last response
        formatted_messages = messages[1:] + [history[-1]]
        token_count = get_token_count(completions_command, formatted_messages, model=model_name)

        # Yield the updated history, button state, and token count
        yield history, gr.update(interactive=enable_tcl_button), gr.update(interactive=True), format_token_count(token_count)

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
        history.append({"role": "assistant", "metadata": {"title": "Info"}, "content": f"Model {model_name} selected."})
        return history

    def save_chat(history, prompt, model, token_text):
        """
        Save the full chat history, including system_message and model
        """
        # Parse out the token count as an integer from the token_text (e.g., "**Tokens:** 123")
        parts = token_text.split()
        if len(parts) > 1:
            try:
                token_count = int(parts[1])
            except Exception:
                token_count = token_count
        chat_data = {
            "system_prompt": prompt,
            "model": model,
            "tokens": token_count,
            "history": history
        }
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
            return [gr.Button(visible=False), gr.DownloadButton(value=f.name, visible=True)]

    def download_chat():
        # Remove the temporary file after download
        if download_chat_button.value:
            try:
                os.remove(download_chat_button.value)
            except Exception:
                pass
        return [gr.Button(visible=True), gr.DownloadButton(visible=False)]

    # Create the Gradio interface
    with gr.Blocks(css="""
#chatbot {
    height: 60vh !important;
    min-height: 250px !important;
}
""") as demo:
        with gr.Row():
            with gr.Column(scale=1, min_width=0):
                modelPicker = gr.Dropdown(
                    label="Model",
                    choices=all_models,
                    value=default_model,
                    interactive=True,
                )
            with gr.Column(scale=2):
                prompt_input = gr.Textbox(
                    label="System Prompt",
                    value=system_message,
                    interactive=True,
                    lines=2,
                    max_lines=4,
                )
        chatbot = gr.Chatbot(
            elem_id="chatbot",
            type="messages",
            editable="all",
            label="TclAI",
            avatar_images=(None, "https://www.tcl-lang.org/images/plume.png"),
            value=[{"role": "assistant", "metadata": {"title": "Info"}, "content": f"Connected to {app_name}, using {default_model}. How can I help you?"}],
        )
        chatbot.show_copy_all_button = True
        modelPicker.change(change_model, [modelPicker, chatbot], [chatbot])
        
        with gr.Row():
            with gr.Column(scale=1, min_width=0):
                token_count_display = gr.Markdown("**Tokens:** 0", elem_id="token-count-display")
            with gr.Column(scale=2):
                run_tcl_button = gr.Button("Run Tcl Code", interactive=False)
            with gr.Column(scale=1, min_width=0):
                add_note_button = gr.Button("Add Note", variant="secondary")
            with gr.Column(scale=1, min_width=0):
                save_chat_button = gr.Button("Save Chat", variant="secondary")
                download_chat_button = gr.DownloadButton(label="Download Chat", visible=False)

        chat_input = gr.MultimodalTextbox(
            interactive=True,
            file_count="multiple",
            placeholder="Enter message or upload file...",
            show_label=False,
            sources=["upload"],
            autofocus=True
        )

        chatbot.undo(undo, chatbot, [chatbot, chat_input, run_tcl_button])
        chat_msg = chat_input.submit(
            add_message, [chatbot, chat_input], [chatbot, chat_input]
        ).then(
            bot, [chatbot, modelPicker, prompt_input], [chatbot, run_tcl_button, chat_input, token_count_display], api_name="bot_response"
        )

        run_tcl_button.click(
            execute_tcl_code, [chatbot], [chatbot, run_tcl_button]
        ).then(
            bot, [chatbot, modelPicker, prompt_input], [chatbot, run_tcl_button, chat_input, token_count_display]
        )

        add_note_button.click(
            add_note, [chatbot, chat_input], [chatbot, chat_input]
        )

        save_chat_button.click(save_chat, [chatbot, prompt_input, modelPicker, token_count_display], [save_chat_button, download_chat_button])
        download_chat_button.click(download_chat, [], [save_chat_button, download_chat_button])

    demo.launch(inbrowser=True, share=False)
