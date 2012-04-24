import logging, pickle
from uuid import uuid4


class Device:
	"""
	keeps a device's serial, last known ip and cookie it connected with
	"""
	_PKCS12_FAILED = 'FAILED'

	def __init__(self, serial = None, fiona_id = None, last_ip = None, last_cookie = None, p12 = None, books = None):
		self.serial = serial or str(uuid4())[:8]
		self.fiona_id = fiona_id or None
		self.last_ip = last_ip
		self.last_cookie = last_cookie
		self.p12 = p12 or None
		self.books = {} if not books else pickle.loads(books)

		# the certificate is re-loaded each time the proxy is restarted
		self.context = None
		self.connections = {}

		# won't be saving the last_sync time to the db
		# so that each time the proxy is restarted, a full sync takes place for each device
		self.last_sync = 0

		# devices connecting for the first time after KSP boots up will:
		#	- update their configuration
		#	- do a snapshot upload
		self.actions_queue = [ ('SET', 'SCFG'), ('UPLOAD', 'SNAP') ]

		if self.p12:
			logging.info("loaded device %s", self)
		else:
			logging.warn("new device %s", self)

	def is_provisional(self): # do we know the device serial yet?
		return len(self.serial) == 8

	def mark_context_failed(self):
		logging.debug("%s context failed", self)
		self.context = self._PKCS12_FAILED

	def context_failed(self):
		return id(self.context) == id(self._PKCS12_FAILED)

	def __str__(self):
		if self.is_provisional():
			return "{%s/provisional %s cookie=%s}" % (
						self.serial, self.last_ip, None if not self.last_cookie else self.last_cookie[:12] + '...'
					)

		return "{%s/%s %s cookie=%s%s, sync=%s with %d books}" % (
					self.serial, self.fiona_id, self.last_ip,
					None if not self.last_cookie else self.last_cookie[:12] + '...',
					' no PKCS12' if self.context_failed() else '',
					self.last_sync, len(self.books),
				)
