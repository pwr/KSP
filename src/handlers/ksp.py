import logging

from handlers import TODO_PATH, CDE_PATH, FIRS_PATH
from handlers.dummy import Dummy, DummyResponse
import devices
import config, features


_FIRST_CONTACT = '''
	<?xml version="1.0" encoding="UTF-8"?>
	<response>
		<total_count>0</total_count>
		<next_pull_time/>
		<items>
			<item action="UPLOAD" type="SCFG" key="KSP.upload.scfg" priority="50" is_incremental="false" sequence="0" url="$_SERVER_URL_$ksp/scfg"/>
			<item action="UPLOAD" type="SNAP" key="KSP.upload.snap" priority="50" is_incremental="false" sequence="0" url="$_SERVER_URL_$FionaCDEServiceEngine/UploadSnapshot"/>
			<item action="SET" type="SCFG" key="KSP.set.scfg" priority="200" is_incremental="false" sequence="0">$_SERVERS_CONFIG_$</item>
		</items>
	</response>
'''.replace('\t', '').replace('\n', '').replace('$_SERVER_URL_$', config.server_url)

_UPLOAD_SERIAL = '''
	<item action="SND" type="KSP.upload.serial" priority="50" is_incremental="false" sequence="0"
		 key="FILE_/proc/usid" url="$_SERVER_URL_$ksp/serial"/>
'''.replace('\t', '').replace('\n', '').replace('$_SERVER_URL_$', config.server_url)


def _first_contact(device):
	# triggered actions:
	# - upload config, for debugging purposes (we can check the client config in the logs)
	# - upload snapshot -- it will include device serial and model for the kindles
	# - update client API urls -- this needs to happen later, after we've confirmed the client kind/model
	text = _FIRST_CONTACT # _FIRST_CONTACT.replace('$_UPLOAD_SERIAL_$', _UPLOAD_SERIAL if device.is_kindle() else '')
	text = text.replace('$_SERVERS_CONFIG_$', _servers_config(device))
	return bytes(text, 'UTF-8')

def _servers_config(device):
	is_kindle = device.is_kindle()
	def _url(x):
		# always drop the last / from the url
		# the kindle devices urls also need to include the service paths (FionaTodoListProxy, FionaCDEServiceEngine, etc)
		# the other clients seem to require urls without those paths
		return (config.server_url + x.strip('/')) if is_kindle else config.server_url[:-1]

	# we always need the todo and cde urls
	urls = [ '', 'url.todo=' + _url(TODO_PATH), 'url.cde=' + _url(CDE_PATH) ]

	if is_kindle:
		# cookie domains ensures we get the proper cookie and are able to identify the device
		urls.append('cookie.store.domains=.amazon.com,' + config.server_hostname)
		# we need these urls to intercept registration/deregistration calls,
		# so that we can update the client certificate
		urls.extend((
			'url.firs=' + _url(FIRS_PATH),
			'url.firs.unauth=' + _url(FIRS_PATH),
		))
	else:
		# not sure what this is for, but all non-kindle clients seem to have it
		urls.append('url.cde.nossl=' + _url(CDE_PATH))

	if not features.allow_logs_upload:
		ignore = config.server_url + 'ksp/ignore'
		urls.extend((
			'url.messaging.post=' + ignore,
			'url.det=' + ignore,
			'url.det.unauth=' + ignore,
		))

	urls.append('')
	return '\n'.join(urls)


class KSP_Handler (Dummy):
	def __init__(self):
		Dummy.__init__(self, 'ksp', '/ksp')

	def call(self, request, device):
		if request.path.startswith('/ksp/ignore'):
			return 200

		if request.command == 'PUT' and request.path == '/ksp/scfg':
			logging.debug("got client configuration:\n%s", request.body)
			return 200

		logging.warn("unknown /ksp call %s", request.path)
		return 200
