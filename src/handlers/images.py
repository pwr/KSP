import logging
import os.path

from handlers.dummy import Dummy, DummyResponse
from handlers import is_uuid
import calibre


_ECX = 'g-ecx.images-amazon.com'
_HEADERS = { 'Content-Type': 'image/jpeg', 'Cache-Control': 'max-age=300,public' }

class ECX_Images (Dummy):
	def __init__(self):
		Dummy.__init__(self, _ECX, '/images')

	def call(self, request, device):
		if request.path.startswith('/images/P/'):
			asin = asin[10:asin.find('.', 11)]
			if is_uuid(asin):
				book = calibre.book(asin)
				# logging.debug("looking for cover of %s %s", asin, book)
				if book and book.file_path:
					image_path = os.path.join(os.path.dirname(book.file_path), "cover.jpg")
					image_data = None
					if os.path.isfile(image_path):
						try:
							with open(image_path, 'rb') as fi:
								image_data = fi.read()
						except:
							logging.exception("failed to read cover for %s", book)
					if image_data:
						return DummyResponse(headers = _HEADERS, data = image_data)
				return 404 # forces Kindle 4 PC to use the cover from the .mobi file, if any

		return DummyResponse(303, headers = { 'Location: http://' + _ECX + request.path })
