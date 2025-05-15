import exec_client
import os
import asyncio

# Get the port and API key from the environment variables
API_PORT = int(os.environ.get('API_PORT'))
API_KEY = os.environ.get('API_KEY')
API_SERVER = os.environ.get('API_SERVER')  # The server is running on the same machine

async def main():
    # Example scripts to execute
    script1 = """
        for {set i 1} {$i <= 3} {incr i} {
            puts stderr $i
            puts [expr $i * $i]
        }
        expr $i
    """
    script2 = "expr 1 + 1"
    script3 = "abadcommand"  # Invalid command
    script4 = "puts \"Hello, World!\""
    script5 = "puts stderr \"Error message\""

    scripts = [script5, script4, script3, script2, script1] 

    for script in scripts:
        print(f"Executing script:\n{script}")
        result, stdout, stderr = await exec_client.execute_script(script, API_SERVER, API_PORT, API_KEY)

        if result or stdout or stderr:
            print(f"{result = }")
            print(f"{stdout = }")
            print(f"{stderr = }")
        else:
            print("Failed to get a response from the server.")
            

if __name__ == "__main__":
    asyncio.run(main())
