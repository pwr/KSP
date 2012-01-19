import logging

from handlers import Upstream, DummyResponse
from handlers import CDE, CDE_PATH
import calibre


_CALIBRE_DEVICE_ID = 'CalibreLibrary'
_DEVICE_NODE_TEMPLATE = '<device devicetype="%s" name="Calibre Library" serialnumber="%s"/>'


class CDE_DevicesWithCollections (Upstream):
	_DEVICE_NODE = bytes(_DEVICE_NODE_TEMPLATE % (_CALIBRE_DEVICE_ID, calibre.LIBRARY_ID), 'UTF-8')

	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'getAllDevicesWithCollections?', 'GET')

	def call(self, request, device):
		response = self.call_upstream(request, device)
		if response.status != 200:
			return response

		text = response.body
		devices_tag = text.find(b'<devices>')
		if devices_tag < 0:
			logging.warn("did not find <devices> in (%s) %s", type(text), str(text, 'utf-8'))
			return response

		response.update_body(text[:devices_tag] + self._DEVICE_NODE + text[devices_tag:])
		return response


def _collection_node(name, items):
	yield '<collection name="%s">' % name
	for book in items:
		yield '<item id="%s" type="%s"/>' % (book.asin, book.cde_content_type)
	yield '</collection>'


class CDE_GetCollections (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'getCollections?', 'GET')

	def call(self, request, device):
		global _CALIBRE_DEVICE_ID
		q = request.get_query_params()
		if _CALIBRE_DEVICE_ID == q.get('deviceType') and calibre.LIBRARY_ID == q.get('serialNumber'):
			return self.calibre_collections()
		return self.call_upstream(request, device)

	def calibre_collections(self):
		lines = [ '<?xml version="1.0" encoding="utf-8"?><collections>' ]
		for series_name, books_list in calibre.series_collections().items():
			if books_list:
				lines += _collection_node(series_name, books_list)
		for tag_name, books_list in calibre.tag_collections().items():
			if books_list:
				lines += _collection_node("{" + tag_name + "}", books_list)
		lines.append('</collections>')
		return DummyResponse(data = bytes(''.join(lines), 'utf-8'))
