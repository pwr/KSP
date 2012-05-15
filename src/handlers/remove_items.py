import logging
import xml.dom.minidom as minidom

from handlers.upstream import Upstream
from handlers.dummy import DummyResponse, ExceptionResponse
from handlers import is_uuid, TODO, TODO_PATH
import calibre, qxml
import features
import annotations


_DUMMY_BODY = b'<?xml version="1.0" encoding="UTF-8"?><response><status>SUCCESS</status></response>'

def _process_item(device, action = None, cde_type = None, key = None, complete_status = None, **extra):
	if key.startswith('KSP.') or cde_type.startswith('KSP.'):
		# KSP internal stuff, not relevant upstream
		return True

	if not features.allow_logs_upload and action == 'SND' and cde_type == 'CMND' and key.endswith(':SYSLOG:UPLOAD'):
		return True

	if action in ('GET', 'DOWNLOAD') and cde_type in ('EBOK', 'PDOC', 'APNX') and is_uuid(key, cde_type):
		book = calibre.book(key)
		if complete_status == 'COMPLETED':
			if book:
				book.mark_downloaded_by(device)
			else:
				logging.warn("%s successfully updated unknown book %s", device, key)
		elif complete_status == 'FAILED':
			logging.warn("%s failed to update book %s", device, book or key)
		else:
			logging.warn("%s: unknown downloaded status %s for %s", device, complete_status, book or key)
		return True

	if action == 'UPD_LPRD' and is_uuid(key, cde_type):
		if complete_status == 'COMPLETED':
			annotations.last_read_updated(device, key)
		elif complete_status == 'FAILED':
			logging.warn("%s failed to update last_read for book %s", device, key)
		else:
			logging.warn("%s: unknown UPD_LPRD status %s for book %s", device, complete_status, key)
		return True

	if action == 'UPD_ANOT' and is_uuid(key, cde_type):
		if complete_status == 'COMPLETED':
			annotations.annotations_updated(device, key)
		elif complete_status == 'FAILED':
			logging.warn("%s failed to update last_read for book %s", device, key)
		else:
			logging.warn("%s: unknown UPD_LPRD status %s for book %s", device, complete_status, key)
		return True

	return False

def _process_xml_response(doc, device):
	x_request = qxml.get_child(doc, 'request')
	x_items = qxml.get_child(x_request, 'items')
	was_updated = False

	for x_item in qxml.list_children(x_items, 'item'):
		action = x_item.getAttribute('action')
		cde_type = x_item.getAttribute('type')
		key = x_item.getAttribute('key')
		complete_status = x_item.getAttribute('complete_status')

		if _process_item(device, action, cde_type, key, complete_status):
			x_items.removeChild(x_item)
			was_updated = True
			continue

	if was_updated and not len(x_items.childNodes):
		raise ExceptionResponse(data = _DUMMY_BODY)

	return was_updated


class TODO_RemoveItems (Upstream):
	def __init__(self):
		Upstream.__init__(self, TODO, TODO_PATH + 'removeItems')

	def call(self, request, device):
		if device.is_provisional():
			return DummyResponse(data = _DUMMY_BODY)

		if not request.body:
			q = request.get_query_params()
			q['cde_type'] = q.get('type')
			if _process_item(device, **q):
				return DummyResponse(data = _DUMMY_BODY)
		else:
			with minidom.parseString(request.body_text()) as doc:
				if _process_xml_response(doc, device):
					xml = doc.toxml('UTF-8')
					request.update_body(xml)

		return self.call_upstream(request, device)
