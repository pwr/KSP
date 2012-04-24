import logging

from handlers import TODO_PATH, CDE_PATH, FIRS_PATH, DET_PATH
from handlers.dummy import Dummy, DummyResponse
import devices
import config, features


SERVERS_CONFIG = (
		'url.todo=' + config.server_url + TODO_PATH.strip('/'),
		'url.cde=' + config.server_url + CDE_PATH.strip('/'),
		'url.firs=' + config.server_url + FIRS_PATH.strip('/'),
		'url.firs.unauth=' + config.server_url + FIRS_PATH.strip('/'),
		'cookie.store.domains=.amazon.com,' + config.server_hostname,
		# 'cmd.any_amazon.domains=.amazon.com,.images-amazon.com,.amazon.co.uk,.' + config.server_domain,
		# 'cmd.any_amazon.headers=Accept-Language,X-DSN',
	)
if not features.allow_logs_upload:
	SERVERS_CONFIG += (
		'url.messaging.post=' + config.server_url,
		'url.det=' + config.server_url + DET_PATH.strip('/'),
		'url.det.unauth=' + config.server_url + DET_PATH.strip('/'),
	)
SERVERS_CONFIG = '\n'.join(SERVERS_CONFIG)

FIRST_CONTACT = '''
	<?xml version="1.0" encoding="UTF-8"?>
	<response>
		<total_count>2</total_count>
		<next_pull_time/>
		<items>
			<item action="SND" type="KSP.upload.serial" priority="50" is_incremental="false" sequence="0"
				 key="FILE_/proc/usid" url="$SERVER_URL$ksp/serial"/>
			<item action="SET" type="SCFG" key="KSP.set.scfg" priority="60" is_incremental="false" sequence="0">$SERVERS_CONFIG$</item>
		</items>
	</response>
'''.replace('\t', '').replace('\n', ''). \
	replace('$SERVER_URL$', config.server_url). \
	replace('$SERVERS_CONFIG$', SERVERS_CONFIG)
FIRST_CONTACT = bytes(FIRST_CONTACT, 'UTF-8')


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
