import sys, os.path, logging, re
from socketserver import ThreadingMixIn
from http.server import HTTPServer
import socket, ssl

import config, features


# need to process the configuration before importing the handlers,
# because many of them depend on these values
if not config.server_url:
	raise Exception("config.server_url must be set")
if not config.server_url.endswith('/'):
	config.server_url += '/'

from urllib.parse import urlparse
protocol, hostname, path, params, query, fragment = urlparse(config.server_url)
config.server_website = '%s://%s' % (protocol, hostname)
config.server_hostname = hostname
config.server_path_prefix = path
logging.debug("server url [%s://%s%s]", protocol, hostname, path )

rewrite_rules = { "https://([-a-z7]*).amazon.com/" : config.server_url }
logging.debug("rewrite rules: %s", rewrite_rules)
config.rewrite_rules = { re.compile(k) : v for k, v in rewrite_rules.items()  }

if config.server_certificate:
	if not os.path.isfile(config.server_certificate):
		raise Exception("server certificate not found at", config.server_certificate)
else:
	config.server_certificate = None

import handlers


class Server (ThreadingMixIn, HTTPServer):
	"""
	actual HTTP server, though is more set-up and configuration than anything else
	"""

	SERVICES = [ handlers.TODO, handlers.CDE, handlers.FIRS, handlers.FIRS_TA, handlers.DET, handlers.DET_TA, handlers.DM, handlers.WWW ]

	def __init__(self, access_log = None, stop_code = None):
		self.access_log = access_log
		self.stop_code = stop_code

		if hasattr(config, 'disconnected') and config.disconnected:
			self._handlers = []
		else:
			self._handlers = self._setup_handlers()
		from http_handler import Handler
		HTTPServer.__init__(self, (config.server_host, config.server_port), Handler, False)

	def _setup_handlers(self):
		# the order is important when paths might collide, e.g. for -ta- services
		hlist = [
				handlers.TODO_SyncMetadata(),
				handlers.TODO_GetItems(),
				handlers.TODO_RemoveItems(),
				handlers.CDE_DownloadContent(),
				handlers.CDE_UploadSnapshot(),
				handlers.CDE_Sidecar(),
				handlers.CDE_DevicesWithCollections(),
				handlers.CDE_GetCollections(),

				# catch-all for todo and cde services
				handlers.Upstream(handlers.TODO, handlers.TODO_PATH), # all other todo calls
				handlers.Upstream(handlers.CDE, handlers.CDE_PATH), # all other cde calls

				# device (de)registration
				handlers.FIRS_TA_NewDevice(),
				handlers.FIRS_NewDevice(),
				handlers.Upstream(handlers.FIRS, handlers.FIRS_PATH),
				# handlers.Store(), # book infos?
				# handlers.Dummy(handlers.WWW, handlers.EMBER_PATH), # ads?
			]

		if features.scrub_uploads:
			hlist.extend([
					handlers.Dummy(handlers.DM, handlers.DM_PATH),
					handlers.Dummy(handlers.DET, handlers.DET_PATH + 'MessageLogServlet'),
					handlers.Dummy(handlers.DET_TA, handlers.DET_PATH),
				])
		else:
			hlist.extend([
					handlers.Upstream(handlers.DM, handlers.DM_PATH),
					handlers.Upstream(handlers.DET, handlers.DET_PATH + 'MessageLogServlet'),
					handlers.Upstream(handlers.DET_TA, handlers.DET_PATH),
				])

		for h in hlist:
			if h.service not in self.SERVICES:
				raise Exception("tried to register handler %s for unknown service %s", h, h.service)
		return hlist

	def find_handler(self, request):
		for h in self._handlers:
			# first volunteer wins
			if h.accept(request):
				return h
		return None

	def run(self):
		self.server_bind()
		if config.server_certificate:
			self.socket = ssl.wrap_socket(self.socket, certfile = config.server_certificate, server_side = True)
		logging.info("started on %s:%s (%s)", self.server_name, self.server_port, self.stop_code)
		self.server_activate()
		try:
			self.serve_forever(1)
		except KeyboardInterrupt: # ^C
			logging.warn("received ^C")
			pass
		logging.info("shutdown")
		self.server_close()

	def handle_error(self, request, client_address):
		etype, evalue = sys.exc_info()[:2]
		logging.warn("exception %s %s", etype, evalue)
		if etype == socket.error and evalue == 10054:
			return
		logging.exception("request from %s : %s", client_address, request)
