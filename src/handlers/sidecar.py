import logging
import xml.dom.minidom as minidom

from handlers.upstream import Upstream
from handlers.dummy import DummyResponse, ExceptionResponse
from handlers import is_uuid, CDE, CDE_PATH
from content import decompress, compress, query_params
import postprocess, formats
import annotations
import calibre, qxml


def _process_sidecar_upload(device, book_ids, book_nodes):
	# book_ids is NOT a complete list of books on device
	for asin in book_ids:
		book = calibre.book(asin)
		if book:
			book.mark_on_device(device)

	for x_book in book_nodes:
		asin = x_book.getAttribute('key')
		book = calibre.book(asin)
		if not book:
			logging.warn("sidecar upload for unknown book %s", asin)
			continue

		for kind in ('last_read', 'bookmark', 'highlight', 'note'):
			for x_item in qxml.iter_children(x_book, kind):
				timestamp = x_item.getAttribute('timestamp') or None
				begin = x_item.getAttribute('begin') or None
				end = x_item.getAttribute('end') or begin
				pos = x_item.getAttribute('pos') or None
				state = x_item.getAttribute('state') or None
				text = qxml.get_text(x_item) if kind == 'note' else None

				if kind == 'last_read':
					annotations.set_last_read(asin, timestamp, begin, pos, state)
				else:
					action = x_item.getAttribute('action')
					if action == 'create':
						annotations.create(asin, kind, timestamp, begin, end, pos, state, text)
					elif action == 'delete':
						annotations.delete(asin, kind, timestamp, begin, end)
					elif action == 'modify':
						annotations.modify(asin, kind, timestamp, begin, end, text)
					else:
						logging.error("unknown sidecar action %s: %s", action, x_item)

def _process_xml(request, doc, device):
	books_on_device = set()
	book_nodes = []
	was_modified = False

	x_annotations = qxml.get_child(doc, 'annotations')

	for x_book in qxml.list_children(x_annotations, 'book'):
		asin = x_book.getAttribute('key')
		if is_uuid(asin, x_book.getAttribute('type')):
			books_on_device.add(asin)
			x_annotations.removeChild(x_book)
			book_nodes.append(x_book)
			was_modified = True

	for x_collection in qxml.iter_children(x_annotations, 'collection'):
		for x_book in qxml.iter_children(x_collection, 'book'):
			asin = x_book.getAttribute('id')
			if is_uuid(asin, x_book.getAttribute('type')) and 'add' == x_book.getAttribute('action'):
				books_on_device.add(asin)

	if books_on_device or book_nodes:
		postprocess.enqueue(_process_sidecar_upload, device, books_on_device, book_nodes)

	if was_modified:
		qxml.remove_whitespace(x_annotations)
		if not len(x_annotations.childNodes):
			doc.removeChild(x_annotations)
		if not len(doc.childNodes):
			# there's no more content relevant to Amazon, just reply with an empty 200
			raise ExceptionResponse()

	return was_modified


class CDE_Sidecar (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'sidecar')

	def call(self, request, device):
		if device.is_provisional():
			return None

		if request.command == 'GET':
			q = request.get_query_params()
			asin = q.get('key')
			if is_uuid(asin, q.get('type')):
				book = calibre.book(asin)
				if not book:
					logging.warn("tried to download sidecar for unknown book %s", asin)
					return None
				sidecar_data = formats.sidecar(book)
				if sidecar_data:
					content_type, data = sidecar_data
					return DummyResponse(headers = { 'Content-Type': content_type }, data = data)
				return None
		elif request.command == 'POST':
			q = request.get_query_params()
			lto = q.get('device_lto', -1)
			if lto != -1:
				try: device.lto = int(lto)
				except: pass

			with minidom.parseString(request.body_text()) as doc:
				if _process_xml(request, doc, device):
					if not request.is_signed():
						# drats
						xml = doc.toxml('UTF-8')
						request.update_body(xml)

		return self.call_upstream(request, device)


class CDE_ShareAnnotations (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'shareHighlightAndNote', 'POST')

	def call(self, request, device):
		q = query_params(request.body_text())
		if is_uuid(q.get('key'), q.get('type')):
			logging.warn("sharing annotations for Calibre books is not supported")
			return 200

		return self.call_upstream(request, device)
