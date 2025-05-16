source common/exec_server.tcl

# If your application provides a redirect function, modify capture function 
# to use this instead of the built-in one (example below).

#namespace eval exec_server {
#    proc run_command {command outvar} {
#        upvar $outvar out_value
#        ::redirect -tee -variable out_value {
#            set code [catch {uplevel #0 $command} result]
#            if {$code == 1} {
#                set result "error: $result"; list
#            }
#        }
#        return $result
#    }
#}

# Start the Tcl server and Python application
exec_server::start_server
exec_server::start_client example/tclai_slave.py --clipboard

# Enter event loop until Enter is pressed
namespace import exec_server::resume
resume
