source exec_server.tcl

exec_server::start_server
exec_server::start_client gradio_server.py

# timeout after 1 seconds (long enough for test)
vwait forever