## Introduction
TclAI lets you control a Tcl application from GhatGPT or other LLM API, using a Gradio user interface.

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
  
## Limitations
- The Tcl caller enters a `vwait` loop indefinitely, so you will have to terminate the appliation manually. Since all Tcl applications are different, you'll need to modify this based on the application's UI and your interactivity needs.
- The Tcl code and output are passed directly in the chat message history, rather than being encapsulated in a tool call. This ensures compatibility with a wider range of models, but you may prefer (and your model may work better with) a tool call structure.
- Owing to the limitation above, if the model suggests two sections of Tcl code in a single chat message, only the first will be executed on clicking Run Tcl Code.

