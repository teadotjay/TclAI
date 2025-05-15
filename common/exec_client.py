import asyncio
import os
import re  # Import the regular expression module

async def execute_script(script, server, port, key):
    """
    Asynchronously executes script on the server, including the API key,
    and receives the response, line by line. Parses the response into
    result, stdout, and stderr.

    Args:
        script (str): The code to execute on the server.

    Returns:
        tuple: (result, output),  Any of these can be None
            if the server sends no data.
    """
    try:
        # Connect to the server
        reader, writer = await asyncio.open_connection(server, port)

        # Send preamble with API key
        preamble = f"KEY {key}\n"
        #print("Sending preamble")  # debugging
        writer.write(preamble.encode('utf-8'))

        # Send BEGIN SCRIPT
        writer.write(b"BEGIN SCRIPT\n")

        # Send the script to execute
        #print(f"Sending code: {script}")  # debugging
        writer.write(script.encode('utf-8'))

        # Send END SCRIPT
        writer.write(b"\nEND SCRIPT\n")
        await writer.drain() # Ensure all data is sent

        # Receive the response from the server, line by line
        result = ""
        output = ""
        receiving_result = False
        receiving_output = False

        try:
            while True:
                line = await reader.readline()
                if not line:
                    break  # Connection closed by server

                line = line.decode('utf-8').strip()
                #print(f"{line = }")  # debugging

                if "BEGIN RESULT" in line:
                    receiving_result = True
                    continue
                elif "END RESULT" in line:
                    receiving_result = False
                    continue
                elif "BEGIN OUTPUT" in line:
                    receiving_output = True
                    continue
                elif "END OUTPUT" in line:
                    receiving_output = False
                    continue

                if receiving_result:
                    result += line + "\n"  # Add newline back
                elif receiving_output:
                    output += line + "\n" 
        except asyncio.TimeoutError:
            print("Timed out waiting for server response.")

        # Close the connection
        writer.close()
        await writer.wait_closed()

        #print(f"{output = }")
        #print(f"{result = }")
        return result, output

    except Exception as e:
        print(f"Error sending message: {e}")
        return None, None
