import logging, pickle
from uuid import uuid4

import devices.certificate as _certificate

_PKCS12_FAILED = 'FAILED'

class Device:
	"""
	keeps a device's serial, last known ip and cookie it connected with
	"""

	def __init__(self, serial = None, fiona_id = None, kind = None, last_ip = None, last_cookie = None, p12 = None, books = None):
		self.serial = serial or str(uuid4())
		self.fiona_id = fiona_id or None
		self.last_ip = last_ip
		self.last_cookie = last_cookie
		self.kind = kind
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
		# self.actions_queue = [ ('UPLOAD', 'SCFG'), ('SET', 'SCFG'), ('UPLOAD', 'SNAP') ]
		self.actions_queue = [ ('SET', 'SCFG'), ('UPLOAD', 'SNAP') ]

		if self.p12:
			logging.info("loaded device %s", self)
		else:
			logging.warn("new device %s", self)

	def load_context(self, new_serial = None):
		if new_serial is None and self.context_failed():
			logging.warn("no SSL context available for %s, PKCS12 failed", self)
			raise Exception("no SSL context available, PKCS12 failed", self)
		serial = new_serial or self.serial
		self.p12 = self.p12 or _certificate.load_p12bytes(serial)
		self.context = _certificate.make_context(serial, self.p12) or _PKCS12_FAILED
		if self.context_failed():
			# so we don't try this more than once
			logging.warn("%s context failed", self)
			raise Exception("cannot connect to upstream, failed to create context", self, host)

	def ssl_context(self, host):
		if host.endswith('-ta-g7g.amazon.com'):
			return _certificate.DEFAULT_CONTEXT
		if host.endswith('-g7g.amazon.com'): # client certificate required
			if self.is_provisional():
				logging.warn("%s: no SSL context available for %s", host, self)
				return None
			if not self.context:
				self.load_context()
			return self.context
		return _certificate.DEFAULT_CONTEXT

	def is_provisional(self): # do we know the device serial yet?
		return ((self.kind is None and len(self.serial) == 36) or
				(self.kind and self.kind.startswith('kindle') and not self.p12))

	def is_kindle(self):
		return self.kind and self.kind.startswith('kindle')

	def supports_pdoc(self):
		return self.kind and not self.kind.startswith('desktop')

	def context_failed(self):
		return id(self.context) == id(_PKCS12_FAILED)

	def __str__(self):
		if self.is_provisional():
			return "{%s/provisional %s %s cookie=%s}" % (
						self.serial, self.kind, self.last_ip, None if not self.last_cookie else self.last_cookie[:12]
					)

		return "{%s/%s %s %s cookie=%s%s, sync=%s with %d books}" % (
					self.serial, self.fiona_id, self.kind, self.last_ip,
					None if not self.last_cookie else self.last_cookie[:12],
					' no PKCS12' if self.context_failed() else '',
					self.last_sync, len(self.books),
				)
