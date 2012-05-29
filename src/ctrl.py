import os, threading, logging


def _wait_conmand(pipe_file, server):
	with pipe_file:
		while True:
			try:
				b = pipe_file.read(1)
				if b == b'C':
					logging.info("read close command from the control pipe")
					break
			except:
				logging.exception("reading pipe command")
	server.shutdown()

def start_server_controller(server, pipe_file, pipe_path):
	ctrl_thread = threading.Thread(target = _wait_conmand, name = 'ServerControl', args = (pipe_file, server))
	ctrl_thread.daemon = True
	ctrl_thread.start()
	logging.info("started control thread %s listening on control pipe %s", ctrl_thread, pipe_path)


#from signal import signal, getsignal, SIGINT, SIGTERM, SIG_DFL
from signal import signal, SIGTERM, SIG_DFL

#def check_signals():
#	logging.debug("SIGINT = %s", getsignal(SIGINT))
#	logging.debug("SIGTERM = %s", getsignal(SIGTERM))

def signal_handler(sig, frame):
	logging.debug("signal %s frame %s", sig, frame)
	if sig == 15:
		# funny story: first the signal will interrupt the http server's accept()
		# then it needs to be enabled again to actually propagate and interrupt the server
		# I'm probably doing something wrong here, but I don't know what.
		signal(SIGTERM, SIG_DFL)

#signal(SIGINT, signal_handler)
signal(SIGTERM, signal_handler)

