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
  
## TODO
Currently the code enters a `vwait` loop indefinitely, so you will have to terminate the appliation manually. Since all Tcl applications are different, you'll need to modify this based on the application's UI and your interactivity needs.
