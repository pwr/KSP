import os.path, logging, pickle
from sqlite3 import connect as sqlite3
from uuid import uuid4

import config


class DeviceInfo:
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
		self.configuration_updated = False

		if self.p12:
			logging.info("loaded device %s", self)
		else:
			logging.warn("new device %s", self)

	def is_provisional(self): # do we know the device serial yet?
		return len(self.serial) == 8

	def mark_context_failed(self):
		self.context = self._PKCS12_FAILED

	def context_failed(self):
		return id(self.context) == id(self._PKCS12_FAILED)

	def __str__(self):
		return "{%s/%s %s cookie=%s%s, sync=%s with %d books}" % (
					self.serial, self.fiona_id, self.last_ip,
					None if not self.last_cookie else self.last_cookie[:12] + '...',
					' no PKCS12' if self.context_failed() else '',
					self.last_sync, len(self.books),
				)


# devices_db module functions

def _execute(query, parameters = ()):
	# logging.debug("execute %s %s", query, parameters)
	with sqlite3(config.db_path_devices) as db:
		if type(parameters) == tuple: # one query, simple parameters
			db.execute(query, parameters)
		elif type(parameters) == list: # multiple queries, assume the parameters contains a list of tuples
			db.executemany(query, parameters)
		else: # err...
			raise Exception("don't know how to use parameters", parameters)
		db.commit()

def find(serial):
	with sqlite3(config.db_path_devices) as db:
		# db.row_factory = sqlite3.Row
		for row in db.execute('SELECT * FROM devices WHERE serial = ?', (serial, )):
			return DeviceInfo(*row)
	return None

def insert(device):
	if device.is_provisional():
		raise Exception("may not save provisional device", device)
	books = None if not device.books else pickle.dumps(device.books)
	params = ( device.serial, device.fiona_id, device.last_ip, device.last_cookie, device.p12, books )
	_execute('INSERT INTO devices VALUES (?, ?, ?, ?, ?, ?)', params)

def update(device):
	books = None if not device.books else pickle.dumps(device.books)
	params = ( device.fiona_id, device.last_ip, device.last_cookie, device.p12, books, device.serial )
	_execute('UPDATE devices SET fiona_id = ?, last_ip = ?, last_cookie = ?, p12 = ?, books = ? WHERE serial = ?', params)

def load_all():
	with sqlite3(config.db_path_devices) as db:
		# db.row_factory = sqlite3.Row
		for row in db.execute('SELECT * FROM devices'):
			yield DeviceInfo(*row)

def update_all(devices):
	params = [ ( d.fiona_id, d.last_ip, d.last_cookie, d.p12, None if not d.books else pickle.dumps(d.books), d.serial ) for d in devices if d.context ]
	# OR IGNORE is necessary because there may be un-registered devices in the list
	_execute('UPDATE devices SET fiona_id = ?, last_ip = ?, last_cookie = ?, p12 = ?, books = ? WHERE serial = ?', params)
	logging.info("saved %d device(s) to %s", len(params), config.db_path_devices)


config.db_path_devices = os.path.join(config.database_path, 'devices.sqlite')

# we try to create the database schema every time the proxy starts, just in case
# hopefully won't have to do any stupid schema migration in the future... :P
_execute('''
CREATE TABLE IF NOT EXISTS devices (
	serial TEXT PRIMARY_KEY,
	fiona_id TEXT,
	last_ip TEXT,
	last_cookie TEXT,
	p12 BLOB,
	books BLOB
)''')
