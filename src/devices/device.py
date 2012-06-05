import logging, pickle
from uuid import uuid4

import devices.certificate as cert

_PKCS12_FAILED = 'FAILED'

class Device:
	"""
	keeps a device's serial, last known ip and cookie it connected with
	"""

	def __init__(self, serial = None, alias = None, fiona_id = None, kind = None, lto = -1, last_ip = None, last_cookie = None, p12 = None, books = None):
		self.serial = serial or str(uuid4())
		self.alias = alias or None
		self.fiona_id = fiona_id or None
		self.last_ip = last_ip
		self.last_cookie = last_cookie
		self.kind = kind
		self.lto = lto
		self.p12 = p12 or None
		self.books = {} if not books else pickle.loads(books)

		# the certificate is re-loaded each time the proxy is restarted
		self.context = None
		self.connections = {}

		# won't be saving the last_sync time to the db
		# so that each time the proxy is restarted, a full sync takes place for each device
		self.last_sync = 0

		# devices connecting for the first time after KSP boots up will:
		#	- update their configuration with our server urls
		#	- do a snapshot upload, so we can get up-to-date with the list of books on the device
		self.actions_queue = [ 'SET_SCFG', 'UPLOAD_SNAP' ]
		if self.is_kindle(): # for debugging purposes
			self.actions_queue.append('UPLOAD_SCFG')
		# if self.alias is None:
		# 	self.actions_queue.append('GET_NAMS')

		logging.debug("new device %s", self)

	def load_context(self, new_serial = None):
		if new_serial is None and self.context_failed():
			logging.warn("no SSL context available for %s, PKCS12 failed", self)
			return False
		serial = new_serial or self.serial
		self.p12 = cert.load_p12bytes(serial) or self.p12
		self.context = cert.make_context(serial, self.p12) or _PKCS12_FAILED
		if self.context_failed():
			# so we don't try this more than once
			logging.warn("%s context failed", self)
			return False
		return True

	def ssl_context(self, host):
		if host.endswith('-ta-g7g.amazon.com'):
			return cert.DEFAULT_CONTEXT
		if host.endswith('-g7g.amazon.com'): # client certificate required
			if self.is_provisional():
				# logging.warn("%s: no SSL context available for %s", host, self)
				raise Exception("no SSL context available", host, str(self))
			if not self.context:
				if not self.load_context():
					raise Exception("failed to create SSL context", str(self))
			return self.context
		return cert.DEFAULT_CONTEXT

	def is_provisional(self): # do we know the device serial yet?
		return (len(self.serial) == 36
				or (len(self.serial) == 16
					and self.serial.startswith('B0')
					and (self.kind is None or self.kind.startswith('kindle'))
					and not self.p12
					)
				)

	def is_kindle(self):
		return self.kind and self.kind.startswith('kindle')

	def supports_pdoc(self):
		return self.kind and not self.kind.startswith('desktop')

	def context_failed(self):
		return id(self.context) == id(_PKCS12_FAILED)

	def __str__(self):
		if self.is_provisional():
			return "{%s/provisional %s ip=%s cookie=%s}" % (
						self.serial, self.kind, self.last_ip, None if not self.last_cookie else self.last_cookie[:12]
					)

		return "{%s/%s %s ip=%s cookie=%s%s, sync=%s with %d books}" % (
					self.serial, self.alias, self.kind, self.last_ip,
					None if not self.last_cookie else self.last_cookie[:12],
					' no PKCS12' if self.context_failed() else '',
					self.last_sync, len(self.books),
				)
