#!/usr/bin/env tclsh

namespace eval exec_server {

    # Calculate a random API key
    proc generate_api_key {} {
        set characters "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        set key_length 64
        set api_key ""
        for {set i 0} {$i < $key_length} {incr i} {
            set rand_index [expr {int(rand() * [string length $characters])}]
            append api_key [string index $characters $rand_index]
        }
        return $api_key
    }

    proc start_server {{server localhost} {port 0}} {
        set api_key [generate_api_key]
        #puts "Generated API Key: $api_key"

        set sock [socket -server [list exec_server::accept_connection $api_key] -myaddr $server $port]
        set port [fconfigure $sock -sockname]
        set port [lindex $port end]

        puts "Starting exec server on $server:$port (key=$api_key)"

        # Set the environment variables for the Python script
        set ::env(API_SERVER) $server
        set ::env(API_PORT) $port
        set ::env(API_KEY) $api_key
    }

    proc start_client {python_script} {
        puts $::env(API_SERVER)
        # Launch the Python script
        puts "Starting exec client: $python_script"
        # Use 'exec' to run the python script in the background (&)
        eval exec python $python_script &
    }

    # Callback function to handle incoming connections
    proc accept_connection {api_key client_socket address port} {
        puts "Connection accepted from $address:$port"

        # Deafult to invalid
        set valid 0

        # Read the header from the client socket
        gets $client_socket header
        #puts "Header: $header"

        # Header format is "KEY api-key"
        set valid 0
        
        # Check if the header matches the expected format
        if {[regexp {^KEY\s+(.+)$} $header -> received_api_key]} {
            incr valid
        } else {
            puts "Error: Invalid header format received from client."
            #puts "Received header: $header"
            set valid 0
            close $client_socket
            return
        }

        # Verify the API key
        if {$received_api_key eq $api_key} {
            incr valid
        } else {
            #puts "Error: Invalid API key received: '$received_api_key', expected '$api_key'"
            set valid 0
            close $client_socket
            return
        }
        
        # Read the preamble from the client socket
        gets $client_socket preamble
        #puts "Preamble: $preamble"

        if [string equal $preamble "BEGIN SCRIPT"] {
            #puts "Preamble matches 'BEGIN SCRIPT'."
            incr valid
        } else {
            puts "Error: Invalid preamble received from client."
            set valid 0
            close $client_socket
            return
        }

        # Read the code from the client socket until END SCRIPT
        set code ""
        set end_code_found 0
        while {[gets $client_socket line] >= 0} {
            #puts "Line: $line"
            if {[string equal $line "END SCRIPT"]} {
                #puts "End code found."
                set end_code_found 1
                break
            }
            append code $line "\n"
        }
        if {$end_code_found} {
            puts "Code received from client:"
            puts $code
            incr valid
        } else {
            puts "Error: 'END SCRIPT' not found in the received data."
            set valid 0
            close $client_socket
            return
        }
        
        # Execute the code received from the client
        if {$valid==4} {
            puts $client_socket "BEGIN EXECUTION"
            puts "Executing code..."
            set result [redirect::redirect $code out]
        } else {
            puts "Error: Failed valid check."
            close $client_socket
            return
        }
        
        # Send output and result back to the client
        if {[string trim $out] ne ""} {
            puts "Sending OUTPUT to client..."
            puts $client_socket "BEGIN OUTPUT\n$out\nEND OUTPUT"
        }
        if {$result ne ""} {
            puts "Sending RESULT to client..."
            puts $client_socket "BEGIN RESULT\n$result\nEND RESULT"
        }

        # Close the connection
        puts $client_socket "END EXECUTION"
        close $client_socket
        puts "Disconnected from $address:$port"
        puts "Listening for browser input. Press Enter to break or Ctrl-C to quit..."
        return
    }  
    
    # Enter event loop until Enter is pressed
    proc resume {} {
        global keyPressed
        # Set up a fileevent to read from stdin
        fileevent stdin readable exec_server::readInput

        # Main program
        puts "Starting browser interface. Press Enter to break or Ctrl-C to quit..."
        set keyPressed 0  
        vwait keyPressed  ;# Wait until keyPressed changes

        puts "Entering interactive mode (if supported); type `resume` to continue in browser."
    }

    # Callback function to handle key press
    proc readInput {} {
        global keyPressed
        gets stdin
        set keyPressed 1  ;# Change the variable to indicate a key was pressed
    }

    namespace export start_server start_client resume
}