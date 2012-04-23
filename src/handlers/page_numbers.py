import logging, os.path

from handlers.dummy import Dummy, DummyResponse
from handlers import is_uuid, CDE, CDE_PATH
from content import query_params
import calibre


# APNX requests for non-Calibre books should go directly to Amazon...
class CDE_PageNumbers (Dummy):
	_HEADERS = { 'Content-Type': 'application/x-apnx-sidecar' }

	def __init__(self):
		Dummy.__init__(self, CDE, CDE_PATH + 'getPageNumbers?', 'GET')

	def call(self, request, device):
		q = request.get_query_params()
		asin = q.get('key')
		cde_type = q.get('type')

		book = calibre.book(asin) if is_uuid(asin, cde_type) else None
		apnx_path = book.apnx_path() if book else None
		logging.debug("looking for apnx of %s, found %s", book, apnx_path)

		if apnx_path is None:
			return None

		# APNX files are usually small (a few Ks at most),
		# so there's no need to do stream copying
		apnx_data = None
		with open(apnx_path, 'rb') as apnx:
			apnx_data = apnx.read()
		if not apnx_data:
			return None

		return DummyResponse(headers = self._HEADERS, data = apnx_data)
