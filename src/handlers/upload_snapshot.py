import logging

from handlers import Upstream, DummyResponse, is_uuid
from handlers import CDE, CDE_PATH
import calibre, devices, postprocess
import features


def process_books_on_device(device, book_ids):
	# need to better express this, without exposing device.books
	for asin, last_downloaded in list(device.books.items()):
		if asin not in book_ids and last_downloaded > 0:
			# we know snapshot lists ALL books on the device
			logging.warn("%s no longer has book %s %s", device, asin, calibre.book(asin))
			device.books[asin] = 0

	for asin in book_ids:
		book = calibre.book(asin)
		if book:
			book.mark_on_device(device)
		else:
			logging.debug("%s has book unknown book %s", device, asin)


class CDE_UploadSnapshot (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'UploadSnapshot', 'POST')

	def call(self, request, device):
		if device.is_provisional():
			# bingo! now we get the device serial from the headers
			xdsn = request.headers.get('X-DSN')
			if xdsn is None:
				logging.warn("did not find X-DSN header in request! cannot register device %s", device)
			else:
				devices.confirm_device(device, xdsn)
			return DummyResponse()

		request = self.clean_snapshot(request, device)
		return self.call_upstream(request, device)

	def clean_snapshot(self, request, device):
		"""remove calibre book ids from snapshot uploads"""

		# the snapshot upload tells the upstream server all the books that are on the device
		# but it includes all books, not only the ones it thinks it got from the Amazon service
		# so we update the set of books that we know the device has
		# but don't update the list of books it should remove from the device if they are not found in the calibre library

		was_updated = False
		books_on_device = set()

		lines = []
		for line in request.body.splitlines(True):
			if line.startswith(b'Type=EBOK,Key=') and len(line) == 50 + (line[-1] == ord('\n')):
				asin = str(line[14:50], 'ascii') # SHOULD be uuid
				if is_uuid(asin):
					books_on_device.add(asin)
					if features.scrub_uploads:
						was_updated = True
						continue
			elif line.startswith(b'Type=PDOC,Key=') and len(line) == 46 + (line[-1] == ord('\n')):
				asin = str(line[14:46], 'ascii')
				if is_uuid(asin):
					books_on_device.add(asin)
					if features.scrub_uploads:
						was_updated = True
						continue
			lines.append(line)

		if books_on_device:
			postprocess.enqueue(process_books_on_device, device, books_on_device)

		if was_updated:
			request.update_body(b''.join(lines))
		return request
