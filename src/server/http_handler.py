import logging, time
from http.server import BaseHTTPRequestHandler

from handlers import ExceptionResponse
from content import decompress, str_
import devices
import config, features

from server import logger
access_log = logger('access', False, 'INFO')
http_debug = logger('http_debug', 'DEBUG').debug
del logger

import server.request as request


class Handler (BaseHTTPRequestHandler):
	"""
	Main request handler
	"""
	# this needs to be as light as possible, because one instance gets created for each client connection (and is the actual HTTP request object)
	# of course, this is the part that grew quite a lot during development...
	protocol_version = 'HTTP/1.1'
	error_message_format = ''
	error_content_type = 'text/plain'
	# wbufsize = 16 * 1024 # 16k

	_prefix_len = len(config.server_path_prefix or b'x') - 1 # without the final /

	def handle_call(self, device):
		# logging.debug("## %s", self.requestline)

		request.read_body_and_length(self)
		http_debug("%s", self)

		# and finally got to the part where we handle the request
		handler = self.server.find_handler(self)
		response = None
		if handler:
			try:
				response = handler.call(self, device)
			except ExceptionResponse as er:
				response = er.response
		if response is None:
			logging.warn("not found (%s) %s", self.headers.get('Host'), self.requestline)
			return 404
		if type(response) == int: # returned just a status code
			return response

		self.close_connection = response.will_close == True # will_close is a tristate...

		http_debug("replying with %s", response)
		self.send_response_only(response.status, response.reason)

		header_strings = [ k + ': ' + str(v) for k, v in response.headers.items() ]
		self.wfile.write(bytes('\r\n'.join(header_strings), 'latin1'))
		self.wfile.write(b'\r\n\r\n')

		byte_count = response.write_to(self.wfile) # writes the body
		self.log_request(response.status, byte_count)

	def setup(self):
		BaseHTTPRequestHandler.setup(self)
		self.last_device = None

	def is_secure(self):
		return type(self.request).__name__ == 'SSLSocket'

	def ignore_request(self):
		# we ignore requests not targeted to our service
		if self.request_version != self.protocol_version: # all kindle requests SHOULD be HTTP/1.1
			return True
		if config.server_path_prefix:
			if not self.path.startswith(config.server_path_prefix):
				logging.warn("expected path prefix %s", config.server_path_prefix)
				return True
		return False

	def _detect_device(self):
		# all requests handled by the same Handler instance come from the same device, always
		device = self.last_device
		# if device:
		# 	logging.debug("%s last_device = %s", id(self), device)
		if not device:
			# look for a device record, will be automatically created if the features is enabled
			device = devices.detect(request.client_ip(self), cookie = request.xfsn(self),
									kind = request.guess_client(self), serial = request.get_device_serial(self))
			if not device:
				logging.error("failed to identify device for %s", self.requestline)
				return None, 403
			# if self.last_device != device:
			# 	logging.debug("identified device %s", device)
			if not device.is_provisional():
				self.last_device = device
				# logging.debug("guessed device %s", device)
		if device.context_failed(): # failed to create a proper SSL context
			logging.warn("denying access to unregistered device %s", device)
			return None, 401
		return device, None

	def _do_any(self):
		self.started_at = time.time() # almost

		if self.path.startswith('//'):
			self.path = self.path[1:]

		if self.ignore_request():
			logging.warn("ignoring request %s", self.requestline)
			# now for most requests, a 404 might be enough, or just closing the connection (impolite, but cheap)
			# but some idiots retry the request when receiving a 404, so we'll have to be mean to everybody -- redirect them into limbo
			self.wfile.write(bytes(self.request_version, 'ascii'))
			self.wfile.write(b' 301 Moved Permanently\r\nConnection: close\r\n\r\n')
			self.close_connection = 1
			return

		self.path = self.path[self._prefix_len:]
		if self.path.startswith('//'):
			self.path = self.path[1:]

		if self.path.lower() == '/poll':
			self.wfile.write(b'HTTP/1.1 418 I\'m a teapot\r\nConnection: close\r\nServer: Amazon Web Server\r\nContent-Length: 0\r\n\r\n')
			self.close_connection = 1
			return

		device, status = self._detect_device()
		if status is None:
			try:
				status = self.handle_call(device)
			except:
				logging.exception("handling %s", self.requestline)
				status = 500

		if status is not None:
			try:
				self.send_response_only(status)
				if status >= 400:
					self.close_connection = 1
					self.wfile.write(b'Connection: close\r\n')
				if status != 100:
					self.wfile.write(b'Server: Amazon Web Server\r\nContent-Length: 0\r\n\r\n')
			except:
				logging.exception("failed to reply with status %d", status)
			finally:
				self.log_request(status)

	do_GET = _do_any
	do_POST = _do_any
	do_PUT = _do_any
	# do_HEAD = _do_any

	body_text = request.body_text
	update_body = request.update_body
	is_signed = request.is_signed
	get_query_params = request.get_query_params

	def __str__(self):
		headers = ( k + ': ' + str(v) for k, v in self.headers.items() )
		txt = "%s\n\t{%s}" % (self.requestline, ', '.join(headers))
		if hasattr(self, 'body') and self.body:
			plain = decompress(self.body, self.content_encoding)
			txt += "\n" + str_(plain)
		return txt

	def version_string(self):
		return 'Amazon Web Server'

	def log_request(self, code = '-', size = '-'):
		duration = (time.time() - self.started_at) if hasattr(self, 'started_at') else 0
		access_log.info('%s - - [%s] "%s" %s %s (%.3f)', self.client_address[0], self.log_date_time_string(), self.requestline, code, size, duration)
		if duration > 5: # call took more than 5 seconds to handle
			logging.warn("call took %.3f seconds: %s", duration, self.requestline)

	def log_error(self, format, *args):
		logging.error(format, *args)
