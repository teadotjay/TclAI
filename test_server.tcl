source exec_server.tcl

exec_server::start_server
exec_server::start_client test_client.py

# timeout after 1 seconds (long enough for test)
after 1000 {set timeout 1}
vwait timeout