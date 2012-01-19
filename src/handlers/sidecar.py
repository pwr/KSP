import logging
import xml.dom.minidom as minidom

from handlers import Upstream, ExceptionResponse, is_uuid
from handlers import CDE, CDE_PATH
from content import decompress, compress
import postprocess, format_mbp
import calibre, qxml


def process_sidecar_upload(device, book_ids, book_nodes):
	# books_on_device is NOT a complete list
	for asin in book_ids:
		book = calibre.book(asin)
		if book:
			book.mark_on_device(device)

	for x_book in book_nodes:
		format_mbp.process_xbook(x_book)


class CDE_Sidecar (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'sidecar?')

	def call(self, request, device):
		if device.is_provisional():
			return None

		if request.command == 'GET':
			q = request.get_query_params()
			key = q.get('key')
			if q.get('type') == 'EBOK' and is_uuid(key):
				# MBP download
				return format_mbp.response(key)
		elif request.command == 'POST':
			body = decompress(request.body, request.content_encoding)

			with minidom.parseString(body) as doc:
				if self.process_xml(request, doc, device):
					xml = doc.toxml('UTF-8')
					request.update_body(xml)

		return self.call_upstream(request, device)

	def process_xml(self, request, doc, device):
		books_on_device = set()
		book_nodes = []
		was_modified = False

		x_annotations = qxml.get_child(doc, 'annotations')
		for x_book in qxml.list_children(x_annotations, 'book'):
			asin = x_book.getAttribute('key')
			if is_uuid(asin):
				books_on_device.add(asin)
				x_annotations.removeChild(x_book)
				book_nodes.append(x_book)
				was_modified = True
		for x_collection in qxml.list_children(x_annotations, 'collection'):
			for x_book in qxml.list_children(x_collection, 'book'):
				asin = x_book.getAttribute('id')
				if is_uuid(asin) and 'add' == x_book.getAttribute('action'):
					books_on_device.add(asin)

		if books_on_device or book_nodes:
			postprocess.enqueue(process_sidecar_upload, device, books_on_device, book_nodes)

		if was_modified:
			qxml.remove_whitespace(x_annotations)
			if not len(x_annotations.childNodes):
				doc.removeChild(x_annotations)
			if not len(doc.childNodes):
				# there's no more content relevant to Amazon, just reply with an empty 200
				raise ExceptionResponse()

		return was_modified
