import logging
import xml.dom.minidom as minidom
import time

from handlers.upstream import Upstream
from handlers.dummy import DummyResponse
from handlers import is_uuid, CDE, CDE_PATH
import annotations
from annotations.lto import device_lto
import calibre, devices


_LAST_READ = '<last_read annotation_time_utc="%d" lto="%d" pos="%d" source_device="%s" method="FRL" version="0"/>'

def _last_read(book, exclude_device = None):
	lr_list = []
	for lr in annotations.list_last_read(book.asin):
		if lr.device == exclude_device:
			continue
		device = devices.get(lr.device)
		alias = device.alias if device else lr.device
		alias = lr.device if alias is None \
					else alias.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace('\'', '&apos;')
		lr_list.append(_LAST_READ % (lr.timestamp * 1000, device_lto(device), lr.pos, alias))
	if lr_list:
		xml = '<?xml version="1.0" encoding="UTF-8"?><book>' + ''.join(lr_list) + '</book>'
	else:
		xml = '<?xml version="1.0" encoding="UTF-8"?><book/>'
	return DummyResponse(headers = { 'Content-Type': 'text/xml;charset=UTF-8' }, data = bytes(xml, 'UTF-8'))


# APNX requests for non-Calibre books should go directly to Amazon...
class CDE_GetAnnotations (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'getAnnotations', 'GET')

	def call(self, request, device):
		q = request.get_query_params()
		asin = q.get('key')

		if is_uuid(asin, q.get('type')):
			kind = q.get('filter')
			book = calibre.book(asin)
			if not book:
				logging.warn("book not found %s", asin)
				return None
			if kind == 'last_read':
				return _last_read(book, device.serial)
			logging.warn("don't know how to filter annotations of kind %s", kind)
			return None

		return self.call_upstream(request, device)
