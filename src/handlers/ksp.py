import logging

from handlers import TODO_PATH, CDE_PATH, FIRS_PATH, DET_PATH
from handlers.dummy import Dummy, DummyResponse
import devices
import config, features


_FIRST_CONTACT = '''
	<?xml version="1.0" encoding="UTF-8"?>
	<response>
		<total_count>0</total_count>
		<next_pull_time/>
		<items>
			$UPLOAD_SERIAL$
			<item action="SET" type="SCFG" key="KSP.set.scfg" priority="60" is_incremental="false" sequence="0">$SERVERS_CONFIG$</item>
		</items>
	</response>
'''.replace('\t', '').replace('\n', '')

_UPLOAD_SERIAL = '''
	<item action="SND" type="KSP.upload.serial" priority="50" is_incremental="false" sequence="0"
		 key="FILE_/proc/usid" url="$SERVER_URL$ksp/serial"/>
'''.replace('\t', '').replace('\n', '').replace('$SERVER_URL$', config.server_url)

def _first_contact(device):
	text = _FIRST_CONTACT.replace('$UPLOAD_SERIAL$', '' if device.is_anonymous() else _UPLOAD_SERIAL)
	text = text.replace('$SERVERS_CONFIG$', _servers_config(device))
	return bytes(text, 'UTF-8')

def _servers_config(device):
	anon = device.is_anonymous()
	def _url(x):
		# always drop the last / from the url
		return config.server_url[:-1] if anon else config.server_url + x.strip('/')

	urls = [ 'url.todo=' + _url(TODO_PATH), 'url.cde=' + _url(CDE_PATH) ]

	if anon:
		urls.append('url.cde.nossl=' + _url(CDE_PATH))
	else:
		urls.extend((
			'url.firs=' + _url(FIRS_PATH),
			'url.firs.unauth=' + _url(FIRS_PATH),
			'cookie.store.domains=.amazon.com,' + config.server_hostname,
		))

	if not features.allow_logs_upload:
		urls.extend((
			'url.messaging.post=' + config.server_url,
			'url.det=' + _url(DET_PATH),
		))
		if not anon:
			urls.append('url.det.unauth=' + _url(DET_PATH))

	return '\n'.join(urls)


class KSP_Handler (Dummy):
	def __init__(self):
		Dummy.__init__(self, 'ksp', '/ksp')

	def call(self, request, device):
		if request.command == 'PUT' and request.path.endswith('/ksp/serial'):
			# logging.debug("got a serial %s", request.body)
			if device.is_provisional():
				xdsn = str(request.body, 'latin1')
				d = devices.confirm_device(device, xdsn)
				if not d:
					logging.critical("failed to confirm serial %s for %s", xdsn, device)

		# elif request.command == 'PUT' and request.path.endswith('/ksp/certificate'):
		# 	logging.debug("got a certificate %s", request.body)
		# 	# if device.is_provisional():
		# 	# 	xdsn = request.headers.get('X-DSN')
		# 	# 	devices.confirm_device(device, xdsn, request.body)

		return DummyResponse()
