import logging, binascii, json

import formats.mobi as mobi
from content import date_izo


def _record(annotation):
	record = None
	if hasattr(annotation, 'kind'):
		if annotation.kind == 'bookmark':
			record = { 'type': 'kindle.bookmark', 'startPosition': annotation.begin }
		elif annotation.kind == 'highlight':
			record = { 'type': 'kindle.highlight', 'startPosition': annotation.begin, 'endPosition': annotation.end }
		elif annotation.kind == 'note':
			record = { 'type': 'kindle.note', 'startPosition': annotation.begin, 'endPosition': annotation.end, 'text': annotation.text }
	else:
		record = { 'type': 'kindle.lpr', 'location': annotation.begin }
	record['lastModificationTime'] = date_izo(annotation.timestamp)
	logging.debug("record %s", record)
	return record


def assemble_sidecar(book, requested_guid, annotations_list):
	if not annotations_list:
		return None

	if requested_guid:
		guid = mobi.read_guid(book.file_path)
		if guid is None:
			logging.error("not a MOBI book? %s", book)
			return None

		rguid = requested_guid
		if ':' in rguid:
			_, _, rguid = rguid.partition(':')
		try:
			rguid = binascii.unhexlify(bytes(rguid, 'ascii'))
		except:
			logging.exception("failed to parse guid from %s, expected %s", requested_guid, guid)
			return None
		if guid != rguid:
			logging.error("requested guid %s does not match book guid %s", requested_guid, guid)
			return None

	sidecar_json = {
			'md5':'',
			'payload': {
				'acr': requested_guid or '',
				'guid': requested_guid or '',
				'key': book.asin,
				'type': 'EBOK',
				'records': [ _record(s) for s in annotations_list ]
			}
		}
	sidecar_json = json.dumps(sidecar_json, ensure_ascii=True, separators=(',', ':'))
	return ('application/json', bytes(sidecar_json, 'ascii'))
