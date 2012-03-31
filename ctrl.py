import os, threading, logging


def _wait_conmand(pipe_file, server):
	while True:
		b = pipe_file.read(1)
		if b == b'C':
			logging.info("read close command from the control pipe")
			break
	pipe_file.close()
	server.shutdown()

def start_server_controller(server, pipe_file, pipe_path):
	ctrl_thread = threading.Thread(target = _wait_conmand, name = 'ServerControl', args = (pipe_file, server))
	ctrl_thread.daemon = True
	ctrl_thread.start()
	logging.info("started control thread %s listening on control pipe %s", ctrl_thread, pipe_path)
