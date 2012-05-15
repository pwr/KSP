import logging
import xml.dom.minidom as minidom

from handlers.upstream import Upstream
from handlers.dummy import DummyResponse
from handlers.ksp import _servers_config, _first_contact
from handlers import is_uuid, TODO, TODO_PATH
import devices, calibre, qxml
import config, features
import annotations
from annotations.lto import device_lto


def _rewrite_url(url):
	"""
	certain responses from the server contain urls pointing to amazon services
	we rewrite them to point to our proxy
	"""
	if url and config.rewrite_rules:
		for pattern, replacement in config.rewrite_rules.items():
			m = pattern.search(url)
			if m:
				url = url[:m.start()] + m.expand(replacement) + url[m.end():]
	return url

def _add_item(x_items, action, item_type, key = 'NONE', text = None, priority = 600, sequence = 0, url = None, body = None, **kwargs):
	item = qxml.add_child(x_items, 'item')
	item.setAttribute('action', str(action))
	item.setAttribute('is_incremental', 'false')
	item.setAttribute('key', str(key))
	item.setAttribute('priority', str(priority))
	item.setAttribute('sequence', str(sequence))
	item.setAttribute('type', str(item_type))
	if url:
		item.setAttribute('url', url)
	if body:
		qxml.set_text(item, body)
	else:
		for k, v in kwargs.items():
			qxml.add_child(item, k, str(v))
	return item

def _filter_item(x_items, x_item):
	action = x_item.getAttribute('action')
	item_type = x_item.getAttribute('type')

	if action == 'UPLOAD':
		if item_type in ['MESG', 'LOGS'] and not features.allow_logs_upload:
			x_items.removeChild(x_item)
			return True
		item_url = x_item.getAttribute('url')
		new_url = _rewrite_url(item_url)
		if new_url != item_url:
			logging.warn("rewrote url %s => %s", item_url, new_url)
			x_item.setAttribute('url', new_url)
			return True
		return False

	if action == 'DOWNLOAD':
		item_key = x_item.getAttribute('key')
		item_url = x_item.getAttribute('url')
		if item_url and (item_type == 'CRED' or is_uuid(item_key)):
			new_url = _rewrite_url(item_url)
			if new_url != item_url:
				logging.warn("rewrote url for %s: %s => %s", item_key, item_url, new_url)
				x_item.setAttribute('url', new_url)
				return True
		logging.warn("not rewriting url %s for %s", item_url, item_key)
		return False

	if action == 'GET':
		if item_type == 'FWUP' and not features.allow_firmware_updates:
			x_items.removeChild(x_items)
			return True

	if action == 'SND' and item_type == 'CMND':
		item_key = x_item.getAttribute('key')
		if item_key and item_key.endswith(':SYSLOG:UPLOAD') and not features.allow_logs_upload:
			# not sure if this is smart, ignoring these items appears to queue them up at amazon
			x_items.removeChild(x_item)
			return True

	return False

def _consume_action_queue(device, x_items):
	was_updated = False
	while device.actions_queue:
		action = device.actions_queue.pop()
		# logging.debug("checking action %s", action)
		if list(qxml.filter(x_items, 'item', action = action[0], type = action[1])):
			# logging.debug("action %s already found in %s, skipping", action, x_items)
			continue
		if action == 'SET_SCFG':
			_add_item(x_items, 'SET', 'SCFG', key = 'KSP.set.scfg', priority = 100, body = _servers_config(device))
			was_updated = True
		elif action == 'UPLOAD_SNAP':
			_add_item(x_items, 'UPLOAD', 'SNAP', key = 'KSP.upload.snap', priority = 1000, url = config.server_url + 'FionaCDEServiceEngine/UploadSnapshot')
			was_updated = True
		elif action == 'GET_NAMS':
			_add_item(x_items, 'GET', 'NAMS', key = 'NameChange' if device.is_kindle() else 'AliasChange')
			was_updated = True
		elif action == 'UPLOAD_SCFG':
			_add_item(x_items, 'UPLOAD', 'SCFG', key = 'KSP.upload.scfg', priority = 50, url = config.server_url + 'ksp/scfg')
			was_updated = True
		else:
			logging.warn("unknown action %s", action)
	return was_updated

def _update_annotations(device, x_items):
	was_updated = False

	for lr in annotations.get_last_read_updates(device):
		source_device = devices.get(lr.device)
		source_device_alias = (source_device.alias or source_device.serial) if source_device else lr.device
		_add_item(x_items, 'UPD_LPRD', 'EBOK', key = lr.asin, priority = 1100, sequence = lr.pos,
				source_device = source_device_alias, lto = device_lto(source_device), annotation_time_utc = lr.timestamp)
		was_updated = True

	for asin in annotations.get_annotation_updates(device):
		_add_item(x_items, 'UPD_ANOT', 'EBOK', key = asin, priority = 1100)
		was_updated = True

	return was_updated

def _process_xml(doc, device, reason):
	x_response = qxml.get_child(doc, 'response')
	x_items = qxml.get_child(x_response, 'items')
	if not x_items:
		return False

	was_updated = False

	# rewrite urls
	for x_item in qxml.list_children(x_items, 'item'):
		was_updated |= _filter_item(x_items, x_item)

	was_updated |= _consume_action_queue(device, x_items)
	was_updated |= _update_annotations(device, x_items)

	if features.download_updated_books:
		for book in calibre.books().values():
			if book.needs_update_on(device) and book.cde_content_type in ('EBOK', ): # PDOC updates are not supported ATM
				logging.warn("book %s updated in library, telling device %s to download it again", book, device)
				_add_item(x_items, 'GET', book.cde_content_type, key = book.asin, title = book.title, forced = True)
				was_updated = True

	if was_updated:
		x_total_count = qxml.get_child(x_response, 'total_count')
		qxml.set_text(x_total_count, len(x_items.childNodes))

	return was_updated


_POLL_RESPONSE = b'<?xml version="1.0" encoding="UTF-8"?><response><total_count>0</total_count><next_pull_time>0</next_pull_time></response>'

class TODO_GetItems (Upstream):
	def __init__(self):
		Upstream.__init__(self, TODO, TODO_PATH + 'getItems')

	def call(self, request, device):
		q = request.get_query_params()
		if q.get('reason') == 'Poll':
			return DummyResponse(data = _POLL_RESPONSE)

		if device.is_provisional():
			# tell the device to do a full snapshot upload, so that we can get the device serial and identify it
			return DummyResponse(headers = { 'Content-Type': 'text/xml;charset=UTF-8' }, data = _first_contact(device))

		lto = q.get('device_lto', -1)
		if lto != -1:
			try: device.lto = int(lto)
			except: pass

		response = self.call_upstream(request, device)
		if response.status == 200:
			# use default UTF-8 encoding
			with minidom.parseString(response.body_text()) as doc:
				if _process_xml(doc, device, q.get('reason')):
					xml = doc.toxml('UTF-8')
					response.update_body(xml)

		return response
