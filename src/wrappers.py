from http.client import HTTPResponse
import binascii

from content import *


# enhance response objects with some extra methods

def _response_update_body(self, new_body = None):
	if self.content_encoding:
		new_body = compress(new_body, self.content_encoding)
	self.body = new_body
	self.length = 0 if new_body is None else len(new_body)
	del self.headers['Content-Length']
	self.headers['Content-Length'] = str(self.length)

def _response_write_to(self, stream_out):
	if self.length == 0:
		return 0
	stream_out.write(self.body)
	return len(self.body)

def _response_readinto(self, buffer):
	return self.fp.readinto(buffer)

def _response__str__(self):
	txt = "%d %s (%d) {%s}" % (self.status, self.reason, self.length, ', '.join(self.headers))
	if self.body:
		txt += "\n" + str_(decompress(self.body, self.content_encoding))
		# if not self.content_type or self.content_type.startswith('text/') or self.content_type.startswith('application/xml+'):
		# 	txt += '\n' + str_(decompress(self.body, self.content_encoding))
		# else:
		# 	txt += '\nbytes hex: ' + str(binascii.hexlify(self.body), 'ascii')
	return txt

def wrap_response(r):
	r.content_type = r.headers.get('Content-Type', '')
	r.content_encoding = r.headers.get('Content-Encoding')
	r.body = r.read() # the implementation will fully read the body
	r.length = 0 if r.body is None else len(r.body)
	if r.chunked:
		# the content we've read from upstream was chunked
		# the one we'll reply with obviously won't be
		del r.headers['Transfer-Encoding']
	return r


"""
attaches extra methods to the response classes
"""
HTTPResponse.update_body = _response_update_body
HTTPResponse.write_to = _response_write_to
HTTPResponse.readinto = _response_readinto
HTTPResponse.__str__ = _response__str__
