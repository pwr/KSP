import logging, time
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler

from handlers import ExceptionResponse
from content import compress, decompress, read_chunked, str_headers, str_
import devices
import config, features


class Handler (BaseHTTPRequestHandler):
	"""
	Main request handler
	"""
	# this needs to be as light as possible, because one instance gets created for each request (actually, this _is_ the request)
	# of course, this is the part that grew quite a lot during development...
	protocol_version = 'HTTP/1.1'
	error_message_format = ''
	error_content_type = 'text/plain'
	# wbufsize = 16 * 1024 # 16k

	_prefix_len = 0 if not config.server_path_prefix else len(config.server_path_prefix) - 1 # without the final /

	def ignore_request(self):
		# we ignore requests not targeted to our service
		if self.request_version != self.protocol_version: # all kindle requests SHOULD be HTTP/1.1
			return True
		if config.server_path_prefix:
			if not self.path.startswith(config.server_path_prefix):
				return True
		# if config.server_hostname:
		# 	host = self.headers.get('Host')
		# 	# hrm, will let requests without a 'Host' header pass till I establish all the corner cases
		# 	if host and host != config.server_hostname:
		# 		logging.warn("got funny Host header: %s", host)
		# 		return True
		return False

	def handle_call(self):
		# logging.debug("## %s", self.requestline)

		# look for a device record, will be automatically created if the features is enabled
		device = devices.detect(self._client_ip(), self._xfsn())
		if not device:
			logging.error("failed to identify device for %s", self.requestline)
			return 403
		if device.context_failed(): # failed to create a proper SSL context
			logging.warn("denying access to unregistered device %s", device)
			return 401

		self._read_body_and_length()
		logging.debug(str(self))

		# strip possible path prefix
		self.path = self.path[self._prefix_len:]

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

		self.close_connection = response.will_close == True # will_close is a tristate...

		logging.info("replying with %s", response)
		self.send_response_only(response.status, response.reason)

		header_strings = [k + ': ' + v for k, v in list(response.headers.items())]
		self.wfile.write(bytes('\r\n'.join(header_strings), 'latin1'))
		self.wfile.write(b'\r\n\r\n')

		byte_count = response.write_to(self.wfile) # writes the body
		self.log_request(response.status, byte_count)

		# logging.debug("%%%% %s", self.requestline)
		return 0

	def _do_any(self):
		self.started_at = time.time() # almost

		if self.ignore_request():
			logging.warn("ignoring request (%s) %s", self.headers.get('Host'), self.requestline)
			# now for most requests, a 404 might be enough, or just closing the connection (impolite, but cheap)
			# but some idiots retry the request when receiving a 404, so we'll have to be mean to everybody -- redirect them into limbo
			self.wfile.write(bytes(self.request_version, 'ascii'))
			self.wfile.write(b' 301 Moved Permanently\r\nConnection: close\r\n\r\n')
			self.close_connection = 1
			return

		try:
			status = self.handle_call()
			if status > 0:
				self.send_error(status)
		except:
			logging.exception("handling %s", self.requestline)
			self.send_error(500)

	do_GET = _do_any
	do_POST = _do_any
	do_PUT = _do_any
	do_HEAD = _do_any

	def _read_body_and_length(self):
		"""
		fully reads the request body, also handles chunked content
		gzipped content is read as-is
		sets self.body, self.length and self.content_encoding
		"""
		self.content_encoding = self.headers.get('Content-Encoding')
		if self.content_encoding:
			logging.warn("request (%s) has Content-Encoding %s", self.requestline, self.content_encoding)

		transfer_encoding = self.headers['Transfer-Encoding']
		if transfer_encoding:
			if 'chunked' != transfer_encoding:
				raise Exception("Transfer-Encoding not supported", transfer_encoding)
			logging.warn("request (%s) has chunked body", self.requestline)
			self.body = read_chunked(self.rfile)
			self.length = 0 if self.body is None else len(self.body)
			del self.headers['Content-Length']
			self.headers['Content-Length'] = self.length
			del self.headers['Transfer-Encoding']
			return

		self.length = int(self.headers.get('Content-Length', 0))
		if self.length > 0:
			self.body = self.rfile.read(self.length)
		else:
			self.body = None

	def _xfsn(self):
		xfsn = self.headers.get('X-fsn')
		if xfsn:
			return xfsn
		cookie = self.headers.get('Cookie')
		if cookie and cookie.startswith('x-fsn='):
			return cookie[6:]
		return None

	def _client_ip(self):
		return self.headers.get('X-Forwarded-For') or self.client_address[0]

	def get_query_params(self):
		path, qmark, query = self.path.partition('?')
		params = {} if not query else parse_qs(query)
		# logging.debug("query params %s", params)
		params = { k : (v[0] if v else v) for k, v in params.items() }
		# logging.debug("query params %s", params)
		return params

	def update_body(self, new_body = None):
		self.body = compress(new_body, self.content_encoding)
		self.length = 0 if new_body is None else len(self.body)
		del self.headers['Content-Length']
		self.headers['Content-Length'] = str(self.length)

	def __str__(self):
		txt = "%s %s %s\n\t%s" % (self.command, self.path, self.request_version, str_headers(self.headers._headers))
		if self.body:
			plain = decompress(self.body, self.content_encoding)
			txt += "\n" + str_(plain)
		return txt

	def version_string(self):
		return "Amazon Web Server"

	def log_request(self, code = '-', size = '-'):
		if hasattr(self, 'started_at'):
			duration = time.time() - self.started_at
		else:
			duration = 0
		self.server.access_log.info('%s - - [%s] "%s" %s %s (%.3f)',
				self.client_address[0], self.log_date_time_string(), self.requestline, str(code), str(size), duration)
		if duration > 5:
			logging.warn("call took %.3f seconds: %s", duration, self.requestline)

	def log_error(self, format, *args):
		logging.error(format, *args)
