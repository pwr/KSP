import logging, time
import xml.dom.minidom as minidom

from handlers import Upstream, DummyResponse
from handlers import TODO, TODO_PATH
from content import date_iso
import calibre, qxml
import features


def _book_node(doc, book):
	"""builds a xml node from book info to be added to the add_update_list node"""
	book_node = doc.createElement('meta_data')

	# we keep the same tag order as in Amazon's proper responses
	qxml.add_child(book_node, 'ASIN', book.asin)
	qxml.add_child(book_node, 'title', book.title)

	authors_node = qxml.add_child(book_node, 'authors')
	for author in book.authors:
		qxml.add_child(authors_node, 'author', author)

	publishers_node = qxml.add_child(book_node, 'publishers')
	for publisher in book.publishers:
		qxml.add_child(publishers_node, 'publisher', publisher)
	qxml.add_child(book_node, 'publication_date', date_iso(book.last_modified))

	qxml.add_child(book_node, 'cde_contenttype', book.cde_content_type)
	qxml.add_child(book_node, 'content_type', book.content_type)

	if book.languages:
		qxml.add_child(book_node, 'content_language', book.languages[0])

	return book_node

def _slim_book_node(doc, asin, cde_content_type):
	"""builds a xml node from book info to be added to the removal_list node"""
	book_node = doc.createElement('meta_data')
	qxml.add_child(book_node, 'ASIN', asin)
	qxml.add_child(book_node, 'cde_contenttype', cde_content_type)
	return book_node


class TODO_SyncMetadata (Upstream):
	def __init__(self):
		Upstream.__init__(self, TODO, TODO_PATH + 'syncMetaData?', 'GET')

	def call(self, request, device):
		if device.is_provisional():
			return DummyResponse() # we need to wait for the client to do an UploadStanpshot

		response = self.call_upstream(request, device)
		if response.status != 200:
			return response

		with minidom.parseString(response.body) as doc:
			if self.process_xml(doc, device):
				xml = doc.toxml('UTF-8')
				response.update_body(xml)
			device.last_sync = request.started_at

		return response

	def process_xml(self, doc, device):
		x_response = qxml.get_child(doc, 'response')
		x_add_update_list = qxml.get_child(x_response, 'add_update_list')
		x_removal_list = qxml.get_child(x_response, 'removal_list')
		if not x_add_update_list or not x_removal_list:
			return False

		sync_type = x_response.getAttribute('syncType')
		logging.info("sync (%s) for device %s", sync_type, device)

		# a full sync is always done just after the proxy started
		# also, a full sync is usually done when the device just restarted
		last_sync = 0 if sync_type == 'full' else device.last_sync

		calibre_books = calibre.books(True) # since we're doing a sync, reload the library

		was_updated = False
		for book in calibre_books.values():
			if not book.file_path:
				continue
			if book.last_modified > last_sync or not book.is_known_to(device) or book.needs_update_on(device):
				logging.warn("book %s newer in library than on %s", book, device)
				book.mark_known_to(device)
				x_add_update_list.appendChild(_book_node(doc, book))
				was_updated = True

		for asin, last_downloaded in list(device.books.items()):
			book = calibre_books.get(asin)
			if not book or not book.file_path:
				logging.warn("%s has book %s, but it's not in the library", device, asin)
				calibre.missing_from_library(asin, device)
				x_removal_list.appendChild(_slim_book_node(doc, asin, 'EBOK')) # may have been PDOC, who knows? let's see how this works
				was_updated = True

		# we could parse the response's sync_time value, but the difference should be under a few seconds in the worst case scenario
		return was_updated
