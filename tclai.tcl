source tcl/exec_server.tcl

# If your application does *not* provide a redirect function, uncomment the following line to use the included one
source tcl/redirect.tcl

# If your application *does* provide a redirect function, uncomment and define it here
# namespace eval redirect {
#     proc redirect::redirect {command outvar} {
#         upvar $outvar out_value
#         ::redirect -tee -variable out_value $command
#     }
# }

# Set the server and port
exec_server::start_server
exec_server::start_client tclai_config.py

# Enter event loop until Enter is pressed
namespace import exec_server::resume
resume
