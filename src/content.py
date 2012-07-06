import logging, gzip, time
from urllib.parse import parse_qs


def str_(bytes_buffer):
	if type(bytes_buffer) == str:
		return bytes_buffer
	for encoding in [ 'utf-8', 'latin1', None ]:
		try: return str(bytes_buffer, encoding)
		except: pass
	return '<failed to decode bytes>'

def query_params(text):
	if not text:
		return {}
	if type(text) == bytes:
		text = str(text, 'UTF-8')
	params = parse_qs(text)
	params = { k : (v[0] if v else v) for k, v in params.items() }
	return params

def date_header(timestamp = None):
	return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(time.time() if timestamp is None else timestamp))

def date_iso(timestamp = None):
	return time.strftime('%Y-%m-%dT%H:%M:%S+0000', time.gmtime(time.time() if timestamp is None else timestamp))

def date_izo(timestamp = None):
	return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() if timestamp is None else timestamp))

def read_chunked(stream):
	"""
	reads a chunked body from the stream
	does not support chunk extensions (;token=value)
	does not support trailer headers
	"""
	def _read_chunked(stream):
		size = 1
		while size > 0:
			size = stream.readline(100) # the chunk size is on a single line
			size = 0 if size == b'0\r\n' else int(size, 16)
			if size > 0:
				yield stream.read(size)
			stream.read(2) # a CRLF MUST follow the chunk

	return b''.join(_read_chunked(stream))

def decompress(data, encoding = None):
	"""check for content gzip encoding"""
	if not data or not encoding:
		return data
	if 'gzip' == encoding.lower():
		return gzip.decompress(data)
	raise Exception("decompress: unknown encoding", encoding)

def compress(data, encoding = None):
	if not encoding:
		return data
	if 'gzip' == encoding.lower():
		return gzip.compress(data)
	raise Exception("compress: unknown encoding", encoding)

def copy_streams(stream_in, stream_out, max_bytes, buffer_size = 32 * 1024):
	# sendfile would be nice, but it's not cross-platform
	if max_bytes < 0:
		raise Exception("max_bytes must be positive")
	if max_bytes == 0:
		return 0
	bytes = 0
	buffview = memoryview(bytearray(buffer_size))
	while max_bytes < 0 or bytes < max_bytes:
		max_read = buffer_size if max_bytes < 0 else min(buffer_size, max_bytes - bytes)
		# logging.debug("will read %s bytes, we're at %s from %s", max_read, bytes, max_bytes)
		count = stream_in.readinto(buffview[:max_read])
		if not count:
			break
		stream_out.write(buffview[:count])
		bytes += count
	# 	logging.debug("read chunk of %s bytes, we're at %s from %s", count, bytes, max_bytes)
	# logging.debug("done reading %s bytes out of expected %s", bytes, max_bytes)
	buffview.release() # not sure it's strictly necessary
	return bytes
