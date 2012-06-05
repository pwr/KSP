import logging
import xml.dom.minidom as minidom

from handlers.upstream import Upstream
from handlers.dummy import DummyResponse
from handlers import TODO, TODO_PATH
from content import date_iso
import calibre, qxml
import features


class TODO_GetMetadata (Upstream):
	def __init__(self):
		Upstream.__init__(self, TODO, TODO_PATH + 'getMetaData', 'GET')

	def call(self, request, device):
		if device.is_provisional():
			return 200 # we need to wait for the client to do an UploadStanpshot

		q = request.get_query_params()
		cde_type = q.get('type')
		if 'key' in q and cde_type in ('EBOK', 'PDOC'):
			key = q['key']
			if is_uuid(key, cde_type): # very likely comes from our library
				return self.metadata(key)

		return self.call_upstream(request, device)

	def metadata(self, key):
		# no implementation yet
		pass
