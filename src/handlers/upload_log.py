import logging

from handlers.upstream import Upstream
from handlers.dummy import DummyResponse
from handlers import CDE, CDE_PATH
import devices
import features


class CDE_UploadLog (Upstream):
	def __init__(self):
		Upstream.__init__(self, CDE, CDE_PATH + 'log', 'PUT')

	def call(self, request, device):
		logging.debug("got a log upload with %s", request.body)
		if device.is_provisional():
			q = request.get_query_params()
			if q.get('KSP.upload.serial') == 'true':
				xdsn = str(request.body, 'latin1')
				devices.confirm_device(device, xdsn)
				return DummyResponse()

		if features.scrub_uploads:
			return DummyResponse()

		return self.call_upstream(request, device)
