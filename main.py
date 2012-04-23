#!/usr/bin/env python

__version__ = '0.7'

import sys, os, os.path


def abspath(p, mkdir = False):
	if not p:
		return None
	if p[0] == '~':
		if os.environ['HOME']:
			p = os.environ['HOME'] + p[1:]
		elif os.environ['USERPROFILE']:
			p = os.environ['USERPROFILE'] + p[1:]
		else:
			raise Exception("don't know how to translate ~ to $HOME")
	elif not os.path.isabs(p):
		p = os.path.join(os.path.dirname(__file__), p)
	p = os.path.abspath(p)
	if mkdir and not os.path.exists(p):
		os.makedirs(p)
	return p

def _args():
	import argparse
	p = argparse.ArgumentParser(description = "Kindle Store proxy", prog = 'ksp')
	p.add_argument('--config', dest = 'etc_path', default = 'etc',
								help = "Path to the configration folder")
	p.add_argument('--loglevel', dest = 'log_level', choices = ('debug', 'info', 'warn'), default = 'debug',
								help = "Set the minimum logging level in the server")
	p.add_argument('--console', dest = 'console', action = 'store_const', const = True, default = False,
								help = "Log to the console instead of a log file")
	p.add_argument('--control-pipe', dest = 'control_pipe',
								help = "Use the given pipe to read server control commands")
	return p.parse_args()


import logging


def _make_root_logger(stream, log_level = 'NOTSET'):
	handler = logging.StreamHandler(stream)
	fmt = logging.Formatter('[%(asctime)-12s.%(msecs)03d] %(levelname)-8s {%(filename)s:%(lineno)d %(funcName)s %(threadName)s} %(message)s', '%Y-%m-%d %H:%M:%S')
	handler.setFormatter(fmt)
	# handler.addFilter(lambda logrecord: logrecord.name != 'access')
	log = logging.getLogger()
	log.setLevel(getattr(logging, log_level.upper()))
	log.addHandler(handler)
	logging.captureWarnings(True)
	return log

def _make_access_log(filename):
	log = logging.getLogger('access')
	log.addHandler(logging.FileHandler(filename, 'a'))
	return log

def _stdstream(path, console):
	from codecs import open as codecs_open

	if not console:
		server_log = os.path.join(path, 'server.log')
		sys.stdout = codecs_open(server_log, mode = 'a', encoding = 'latin1', errors = 'backslashreplace')
		sys.stderr = sys.stdout # open(os.path.join(config.logs_path, 'stderr.log'), 'w', 1)

	if sys.__stdout__ is None:
		sys.__stdout__ = sys.stdout
	if sys.__stderr__ is None:
		sys.__stderr__ = sys.stderr

	return sys.stdout

def main():
	args = _args()
	sys.path.append(abspath(args.etc_path))

	import config
	config.logs_path = abspath(config.logs_path, True)
	_make_root_logger(_stdstream(config.logs_path, args.console), args.log_level)

	config.database_path = abspath(config.database_path, True)
	if hasattr(config, 'server_certificate'):
		config.server_certificate = abspath(config.server_certificate)
	else:
		config.server_certificate = None

	# add the src/ folder to the import path
	sys.path.append(abspath('src'))

	# doing this here because if the pipe does not exit, we want to fail fast,
	# before we load the devices and calibre databases
	import ctrl
	pipe_file = None if not args.control_pipe else open(args.control_pipe, 'rb')

	try:
		logging.info("%s start-up", '*' * 20)

		# import calibre and devices here because the config has to be fully processed for them to work
		import devices, calibre
		access_log = _make_access_log(os.path.join(config.logs_path, 'access.log'))

		from http_server import Server
		server = Server(access_log)
		if pipe_file:
			ctrl.start_server_controller(server, pipe_file, args.control_pipe)
		server.run()
	except:
		logging.exception("")
	finally:
		if pipe_file:
			try: pipe_file.close()
			except: pass
		devices.save_all()

	logging.info("%s shutdown", '*' * 20)
	logging.shutdown()


if __name__ == '__main__':
	main()
	os._exit(0)
