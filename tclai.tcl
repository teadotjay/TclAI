source tcl/exec_server.tcl

# Set the server and port
exec_server::start_server
exec_server::start_client tclai_config.py

# Enter event loop until Enter is pressed
namespace import exec_server::resume
resume
