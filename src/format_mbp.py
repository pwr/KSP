import os.path, logging
import struct

from handlers import DummyResponse
from content import copy_streams, str_headers
import calibre, qxml


class _MBPResult (DummyResponse):
	_HEADERS = { 'Content-Type': 'application/x-mobipocket-sidecar' }
	def __init__(self, book):
		DummyResponse.__init__(self, 200, self._HEADERS)
		self.book = book
		self.length = os.path.getsize(book.mbp_path)
		self.headers['Content-Length'] = str(self.length)

	def write_to(self, stream_out):
		bytes_count = 0
		with open(self.book.mbp_path, 'rb') as file_stream:
			bytes_count = copy_streams(file_stream, stream_out, self.length)
		return bytes_count

	def __str__(self):
		return "200 OK %s\n%s [%s]" % ( str_headers(self.headers.items()), self.book, self.book.mbp_path )


def response(asin):
	book = calibre.book(asin)
	if not book.mbp_path or not os.path.isfile(book.mbp_path):
		return None

	return _MBPResult(book)

def process_xbook(x_book):
	# create/update MBP file for the book
	# logging.debug("processing xbook %s", x_book)
	# x_last_read = qxml.get_child(x_book, 'last_read')
	# if x_last_read:
	# 	calibre.process_last_read(asin, dict(x_last_read.attributes.items()))
	pass # TODO
