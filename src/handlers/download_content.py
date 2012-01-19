import os, os.path, logging, time, re

from handlers import Upstream, DummyResponse, is_uuid
from handlers import CDE, CDE_PATH
from content import copy_streams, str_headers
import calibre


class _BookResponse (DummyResponse):
	"""an HTTP response for downloading book files"""
	_BUFFER_SIZE = 64 * 1024 # 64k
	_HEADERS = {
			'Hint-Sidecar-Download': '0',
			'Accept-Ranges': 'bytes',
			# 'Connection': 'close',
		}

	def __init__(self, book, bytes_range = None):
		status = 200 if bytes_range is None else 206 # 'OK' or 'Partial Content'
		DummyResponse.__init__(self, status, self._HEADERS)
		self.book = book
		self.length = book.file_size

		if bytes_range is None:
			self.range_begin = 0
			self.range_end = self.length - 1
			self.range_length = self.length
			self.headers['Content-Length'] = str(self.length)
		else:
			self.range_begin = bytes_range[0]
			self.range_end = bytes_range[1]
			self.range_length = bytes_range[2]
			self.headers['Content-Range'] = 'bytes=%d-%d/%d' % ( self.range_begin, self.range_end, self.length )
			self.headers['Content-Length'] = str(self.range_length)

		self.headers['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(book.file_path)
		self.headers['Content-Type'] = book.content_type
		# TODO no point in enabling this until I figure out MBP uploads
		# if book.mbp_path:
		# 	self.headers['Hint-Sidecar-Download'] = '1'

	def write_to(self, stream_out):
		bytes_count = 0
		with open(self.book.file_path, 'rb', self._BUFFER_SIZE) as file_stream:
			if self.range_begin > 0:
				file_stream.seek(self.range_begin)
			bytes_count = copy_streams(file_stream, stream_out, self.range_length, self._BUFFER_SIZE)
		return bytes_count

	def __str__(self):
		return "200 OK %s\n%s [%s] %d-%d/%d" % ( str_headers(self.headers.items()), self.book, self.book.file_path, self.range_begin, self.range_end, self.length )


_RANGE_FORMAT = re.compile('^bytes=([0-9]*)-([0-9]*)$')

def _range(range_header, max_size):
	if range_header is None:
		return None

	if not range_header.startswith('bytes='):
		raise ExceptionResponse(416) # 'Requested Range Not Satisfiable'

	global _RANGE_FORMAT
	m = _RANGE_FORMAT.match(range_header)
	if m is None:
		raise ExceptionResponse(416) # 'Requested Range Not Satisfiable'

	group1 = m.group(1)
	group2 = m.group(2)
	if not group1: # suffix byte range
		count = int(group2)
		begin - max_size - count
		end = max_size - 1
	else:
		begin = int(group1)
		if group2:
			end = int(group2)
		else:
			end = max_size - 1
		count = 1 + end - begin

	# the kindle should not be doing this kind of crap, but who knows?
	if begin < 0 or end > max_size - 1 or begin > end:
		raise ExceptionResponse(416) # 'Requested Range Not Satisfiable'
	if count == 0:
		raise ExceptionResponse(204) # No content

	bytes_range = ( begin, end, count )
	logging.debug("parsed range header '%s' as %s", range_header, bytes_range)
	return bytes_range


class CDE_DownloadContent (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'FSDownloadContent?', 'GET')

	def call(self, request, device):
		q = request.get_query_params()
		if 'key' in q and q.get('type') in ['EBOK', 'PDOC']:
			key = q['key']
			if is_uuid(key): # very likely comes from our library
				return self.book_response(key, device, request.headers.get('Range'))

		redirect_header = { 'Location': 'https://cde-g7g.amazon.com/' + request.path }
		return DummyResponse(302, redirect_header)
		# return self.call_upstream(request, device)

	def book_response(self, asin, device, range_header):
		"""
		builds a BookResponse object for downloading the book contents
		"""
		book = calibre.book(asin, True)
		if not book:
			logging.warn("device %s tried to download book %s, but it is not in the library (anymore?)", device, asin)
			return None
		if not book.file_path:
			logging.warn("device %s tried to download book %s, but it has no file available", device, asin)
			return None

		bytes_range = _range(range_header, book.file_size)
		return _BookResponse(book, bytes_range)
