import logging

from handlers.upstream import Upstream
from handlers.dummy import DummyResponse
from handlers import CDE, CDE_PATH
from calibre import LIBRARY_ID
import calibre.collections as collections


_CALIBRE_DEVICE_ID = 'CalibreLibrary'
_DEVICE_NODE = bytes('<device devicetype="%s" name="Calibre Library" serialnumber="%s"/>' % (_CALIBRE_DEVICE_ID, LIBRARY_ID), 'UTF-8')


class CDE_DevicesWithCollections (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'getAllDevicesWithCollections', 'GET')

	def call(self, request, device):
		response = self.call_upstream(request, device)
		if response.status != 200:
			return response

		text = response.body_text()
		devices_tag = text.find(b'<devices>')
		if devices_tag < 0:
			logging.warn("did not find <devices> in (%s) %s", type(text), str(text, 'utf-8'))
			return response

		response.update_body(text[:devices_tag + 9] + _DEVICE_NODE + text[devices_tag + 9:])
		return response


def _collection_node(name, items):
	yield '<collection name="%s">' % name
	for book in items:
		yield '<item id="%s" type="%s"/>' % (book.asin, book.cde_content_type)
	yield '</collection>'


class CDE_GetCollections (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'getCollections', 'GET')

	def call(self, request, device):
		q = request.get_query_params()
		if _CALIBRE_DEVICE_ID == q.get('deviceType') and LIBRARY_ID == q.get('serialNumber'):
			return self.calibre_collections()
		return self.call_upstream(request, device)

	def calibre_collections(self):
		lines = [ '<?xml version="1.0" encoding="utf-8"?><collections>' ]
		for series_name, books_list in collections.series().items():
			if books_list:
				lines += _collection_node(series_name, books_list)
		for tag_name, books_list in collections.tags().items():
			if books_list:
				lines += _collection_node("{" + tag_name + "}", books_list)
		lines.append('</collections>')
		return DummyResponse(data = bytes(''.join(lines), 'utf-8'))
