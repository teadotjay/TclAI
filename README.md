## Introduction
TclAI lets you control a Tcl application from ChatGPT or other LLM API, using a Gradio user interface.

![image](https://github.com/user-attachments/assets/86f5d0d5-903f-490e-9193-505b2691ef2c)

## Usage
1. Obtain an API key from OpenAI, if you haven't already, or modify the code to work with a different chat API
2. Set OPENAI_API_KEY in your environment or `.env` file
3. Add any missing requirements: `pip install -r requirements.txt`
4. Source `tclai.tcl` within your Tcl application
   - This will launch a Gradio application in your browser to communicate with a listening process in your Tcl session
5. Ask it a question
   - It has been prompted to write Tcl code in response to your queries
6. If the response contains Tcl code, Click "Run Tcl Code" to run it directly in your application
   - The result will be returned in chat
7. Press Ctrl-C to stop the server
   - You may have to manually exit the Tcl application and close the browser
8. If your shell is interactive, you can press Enter to pause the server and enter commands in the terminal.
   - To resume the server, type `resume`
  
## Limitations
- If the Tcl application terminates without exiting the server, it may continue running in the background, but without API access. Use your OS to find and kill the process manually, or start a new Tcl server and press Ctrl-C to exit them both.
- In CLI-only applications, the browser interface will pause when you enter interactive commands in the Tcl shell. This may not be a limitation for GUI applications.
- The Tcl code and output are passed directly in the chat message history, rather than being encapsulated in a tool call. This ensures compatibility with a wider range of models, but you may prefer (and your model may work better with) a tool call structure.
- Owing to the limitation above, if the model suggests two sections of Tcl code in a single chat message, only the first will be executed on clicking Run Tcl Code.

