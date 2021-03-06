import sys, logging
from socketserver import ThreadingMixIn
from http.server import HTTPServer
import socket, ssl

import config, features
import handlers


# _SERVICES = [ 'ksp', handlers.TODO, handlers.CDE, handlers.FIRS, handlers.FIRS_TA ]

class Server (ThreadingMixIn, HTTPServer):
	"""
	actual HTTP server, though is more set-up and configuration than anything else
	"""

	def __init__(self):
		if config.disconnected:
			self._handlers = []
		else:
			self._handlers = self._setup_handlers()
		from server.http_handler import Handler
		HTTPServer.__init__(self, (config.server_host, config.server_port), Handler, False)

	def _setup_handlers(self):
		# the order is important when paths might collide, e.g. for -ta- services
		hlist = [
				handlers.KSP_Handler(),

				handlers.TODO_SyncMetadata(),
				handlers.TODO_GetItems(),
				handlers.TODO_RemoveItems(),
				handlers.CDE_DownloadContent(),
				handlers.CDE_UploadSnapshot(),
				handlers.CDE_Sidecar(),
				handlers.CDE_GetPageNumbers(),
				handlers.CDE_GetAnnotations(),
				handlers.CDE_ShareAnnotations(),
				handlers.CDE_DevicesWithCollections(),
				handlers.CDE_GetCollections(),

				# catch-all for todo and cde services
				handlers.Upstream(handlers.TODO, handlers.TODO_PATH[:-1]), # all other todo calls
				handlers.Upstream(handlers.CDE, handlers.CDE_PATH[:-1]), # all other cde calls

				# device (de)registration
				handlers.FIRS_GetNamesForFiona(),
				handlers.FIRS_NewDevice(),
				handlers.FIRS_TA_NewDevice(),
				handlers.Upstream(handlers.FIRS, handlers.FIRS_PATH[:-1]),
				# handlers.Store(), # book infos?
				# handlers.Dummy(handlers.WWW, handlers.EMBER_PATH), # ads?

				handlers.ECX_Images(),
			]

		# for h in hlist:
		# 	if h.service not in _SERVICES:
		# 		raise Exception("tried to register handler %s for unknown service %s", h, h.service)
		return hlist

	def find_handler(self, request):
		for h in self._handlers: # first volunteer wins
			if h.accept(request):
				return h
		logging.warn("no handler found for %s", request.requestline)

	def run(self):
		self.server_bind()
		protocol = 'HTTP'
		if config.server_certificate:
		# 	self.socket = ssl.SSLSocket(self.socket, certfile = config.server_certificate, server_side = True)
			protocol = 'HTTP+HTTPS'
		self.server_activate()
		logging.info("started on %s:%s (%s)", self.server_name, self.server_port, protocol)
		import select
		try:
			self.serve_forever(1)
		except select.error as err:
			logging.critical("select.error %s", err)
		except KeyboardInterrupt: # ^C
			logging.warn("received ^C")
			pass
		logging.info("shutdown")
		self.server_close()


	def get_request(self):
		sock, client_address = HTTPServer.get_request(self)
		if sock and config.server_certificate:
			# this is this kind of smart shit that gets you in really deep trouble later
			peek = sock.recv(5, socket.MSG_PEEK)
			if peek and len(peek) == 5:
				if peek[0] == 0x16:
					logging.debug("socket %s from %s appears to start with a TSL handshake, version %d.%d", sock, client_address, peek[1], peek[2])
					try:
						sock = ssl.SSLSocket(sock=sock, certfile=config.server_certificate, server_side=True)
					except:
						logging.exception("failed to SSL wrap socket %s from %s", sock, client_address)
				elif peek[0] == 0x80 and peek[2] == 0x01:
					logging.debug("socket %s from %s appears to start with a SSLv2 handshake, supported version %d.%d", sock, client_address, peek[3], peek[4])
					try:
						sock = ssl.SSLSocket(sock=sock, certfile=config.server_certificate, server_side=True)
					except:
						logging.exception("failed to SSL wrap socket %s from %s", sock, client_address)
		return sock, client_address

	# def verify_request(self, request, client_address):
	# 	logging.debug("verify %s %s", request, client_address)
	# 	if type(request) == ssl.SSLSocket:
	# 		logging.debug("peer certificate %s", request.getpeercert(binary_form = False))
	# 	return True

	def handle_error(self, request, client_address):
		etype, evalue = sys.exc_info()[:2]
		logging.warn("exception %s %s", etype, evalue)
		if etype == socket.error and evalue.errno in (104, 10054):
			return
		logging.exception("request from %s : %s", client_address, request)
