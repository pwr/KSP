import logging, os.path

from handlers.dummy import Dummy, DummyResponse
from handlers import is_uuid, CDE, CDE_PATH
import annotations
import calibre


_HEADERS = { 'Content-Type': 'application/x-apnx-sidecar' }

# APNX requests for non-Calibre books should go directly to Amazon...
class CDE_GetPageNumbers (Dummy):
	def __init__(self):
		Dummy.__init__(self, CDE, CDE_PATH + 'getPageNumbers', 'GET')

	def call(self, request, device):
		q = request.get_query_params()
		asin = q.get('key')
		if q.get('type') == 'EBOK' and is_uuid(asin, 'EBOK'):
			book = calibre.book(asin)
			apnx_path = annotations.apnx_path(book)
			# logging.debug("looking for apnx of %s, found %s", book, apnx_path)
			if apnx_path:
				# APNX files are usually small (a few Ks at most),
				# so there's no need to do stream copying
				apnx_data = None
				with open(apnx_path, 'rb') as apnx:
					apnx_data = apnx.read()
				if apnx_data:
					return DummyResponse(headers = _HEADERS, data = apnx_data)
