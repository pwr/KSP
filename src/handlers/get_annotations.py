import logging
import xml.dom.minidom as minidom

from handlers.upstream import Upstream
from handlers.dummy import DummyResponse, ExceptionResponse
from handlers import is_uuid, CDE, CDE_PATH
from content import decompress, compress, query_params
import postprocess, formats
import calibre.annotations as annotations
import calibre, qxml


def _annotations(query):
	logging.warn("get annotations %s", query)
	return None


# APNX requests for non-Calibre books should go directly to Amazon...
class CDE_GetAnnotations (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'getAnnotations', 'GET')

	def call(self, request, device):
		q = request.get_query_params()
		asin = q.get('key')

		if is_uuid(asin, q.get('type')):
			return _annotations(q)

		return self.call_upstream(request, device)
