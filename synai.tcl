source tcl/exec_server.tcl

exec_server::start_server
exec_server::start_client python/gradio_server.py

vwait forever