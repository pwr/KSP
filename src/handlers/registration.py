import logging
from base64 import b64decode
import xml.dom.minidom as minidom

from handlers.upstream import Upstream
from handlers import FIRS, FIRS_TA, FIRS_PATH
import qxml, devices


def call_and_process(handler, request, device):
	response = handler.call_upstream(request, device)
	cookie = None
	pkcs12 = None
	with minidom.parseString(response.body) as doc:
		x_response = qxml.get_child(doc, 'response')
		x_cookie = qxml.get_child(x_response, 'store_authentication_cookie')
		cookie = qxml.get_text(x_cookie)
		x_key = qxml.get_child(x_response, 'device_private_key')
		pkcs12 = qxml.get_text(x_key)
	if pkcs12:
		try:
			pkcs12 = b64decode(bytes(pkcs12, 'ascii'))
		except:
			logging.exception("failed to decode incoming device key")
			pkcs12 = None
	devices.update(device, cookie = qxml.get_text(x_cookie), pkcs12_bytes = pkcs12)
	return response


class FIRS_TA_NewDevice (Upstream):
	def __init__(self):
		Upstream.__init__(self, FIRS_TA, (FIRS_PATH + 'getNewDeviceCredentials', FIRS_PATH + 'registerDevice'), 'POST')

	def call(self, request, device):
		return call_and_process(self, request, device)


class FIRS_NewDevice (Upstream):
	def __init__(self):
		Upstream.__init__(self, FIRS, FIRS_PATH + 'getDeviceCredentials', 'GET')

	def call(self, request, device):
		return call_and_process(self, request, device)
