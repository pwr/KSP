import logging
import binascii
from http.client import responses as HTTP_MESSAGES

from content import date_header, str_


class DummyResponse (object):
	"""an HTTP response for downloading book files"""
	def __init__(self, status = 200, headers = None, data = None):
		self.status = status
		self.reason = HTTP_MESSAGES[status]
		self.body = data
		self.length = len(data or b'')

		self.headers = {} if headers is None else dict(headers)
		self.headers['Server'] = 'Amazon Web Server'
		self.headers['Date'] = date_header()
		# if data is not None:
		self.headers['Content-Length'] = self.length
		self.will_close = 'close' == self.headers.get('Connection')
		self.content_type = self.headers.get('Content-Type')

	def write_to(self, stream_out):
		if not self.body:
			return 0
		stream_out.write(self.body)
		return self.length

	def __str__(self):
		t = "[DUMMY] %d %s (%d) %s" % (self.status, self.reason, self.length, self.headers)
		if self.body:
			if self.content_type is None \
					or self.content_type.startswith('text/') \
					or self.content_type.startswith('application/xml-') \
					or self.content_type == 'application/json':
				t += "\n" + str_(self.body)
			elif len(self.body) < 2048:
				t += "\n[HEX] " + str(binascii.hexlify(self.body), 'ascii')
		return t


class ExceptionResponse (Exception):
	"""
	an exception wrapping a response
	used to return a response out-of-order
	"""
	def __init__(self, *args, **kwargs):
		self.response = DummyResponse(*args, **kwargs)


def _path_matches(path, expected_path):
	# logging.debug("matching %s agains %s", path, expected_path)
	return path == expected_path or path.startswith(expected_path + '?') or path.startswith(expected_path + '/')


class Dummy (object):
	"""
	dummy response, ignores the call
	while returning an empty response
	"""
	def __init__(self, service, path, command = None):
		if not path:
			raise Exception("path required", str(self))
		self.service = service
		self.expected_path = path
		self.expected_command = command

	def accept(self, request):
		"""returns True if this handler can process the given request"""
		if type(self.expected_path) == str:
			if not _path_matches(request.path, self.expected_path):
				return False
		else:
			if not any(( _path_matches(request.path, p) for p in self.expected_path )):
				return False
		if self.expected_command and request.command != self.expected_command:
			return False
		return True

	def call(self, request, device):
		"""produces a response for this request"""
		return 200
