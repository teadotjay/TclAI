import re
import time  # Import the time module
import exec_client
import os
import shutil
import subprocess
import pyclip
import exec_client
import asyncio

# Get the port and API key from the environment variables
API_PORT = os.environ.get('API_PORT')
API_KEY = os.environ.get('API_KEY')
API_SERVER = os.environ.get('API_SERVER')  # The server is running on the same machine

def extract_tcl(text):
    """
    Extracts TCL code from a string.

    Args:
        text: The string to search for TCL code.

    Returns:
        The TCL code as a string, or None if no code is found.
    """
    match = re.search(r"###\s*tcl\s*\n(.*)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def process_tcl(text):
    """
    Processes Tcl through the server if found in text, else returns

    Args:
        text: The string to search for TCL code.
    """

    tcl_code = extract_tcl(text)
    if not tcl_code: return

    print("Tcl detected; executing on server.")
    # Call the external API to execute the TCL code
    result, output = asyncio.run( exec_client.execute_script(tcl_code, API_SERVER, API_PORT, API_KEY) )
    
    # Format the response
    api_result = "api_response:"
    if output:
        api_result += f"\n- output:\n```\n{output}\n```\n"
    if result:
        api_result += f"\n- result:\n```\n{result}\n```\n"

    #print(f"{api_result = }")
    pyclip.copy(api_result or "silent completion")
    print("Server response copied to clipboard.")
    
def try_paste():
    try:
        return pyclip.paste()
    except Exception as e:
        return None

def wait_clip(clipnotify_path=None):
    if clipnotify_path:
        # use clipnotify if its path is provided
        subprocess.run([clipnotify_path, "-s", "clipboard"])
    else:
        # otherwise loop and watch for changes
        old_contents = try_paste()
        new_contents = old_contents
        while old_contents == new_contents:
            time.sleep(0.25)
            new_contents = try_paste()

    # return clipboard contents
    return new_contents.decode('utf-8') if new_contents else ""
    
def run(system_prompt=None):
    clipnotify_path = shutil.which('clipnotify')

    if(system_prompt):
        print("Copying system prompt to clipboard.")
        pyclip.copy(system_prompt)

    print("Starting clipboard monitor.")
    while True:
        try:
            contents = wait_clip(clipnotify_path)
        except KeyboardInterrupt:
            print("Exiting clipboard monitor.")
            return
        process_tcl(contents)


if __name__ == "__main__":
    prompt = os.environ.get("API_PROMPT") or 'You are a Tcl assistant. To execute Tcl code, add "### tcl" to the start of the code block.'
    run(prompt)
