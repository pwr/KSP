import os.path, logging, pickle
from sqlite3 import connect as sqlite3, Row as sqlite3_Row

from devices.device import Device as _Device
import config


def _execute(query, parameters = ()):
	# logging.debug("execute %s %s", query, parameters)
	try:
		with sqlite3(_db_path) as db:
			if type(parameters) == tuple: # one query, simple parameters
				db.execute(query, parameters)
			elif type(parameters) == list: # multiple queries, assume the parameters contains a list of tuples
				db.executemany(query, parameters)
			else: # err...
				raise Exception("don't know how to use parameters", str(parameters))
			db.commit()
	except:
		logging.exception("query %s %s", query, parameters)

def insert(device):
	if device.is_provisional():
		raise Exception("may not save provisional device", str(device))
	books = None if not device.books else pickle.dumps(device.books)
	params = ( device.serial, device.alias, device.fiona_id, device.kind, device.lto, device.last_ip, device.last_cookie, device.p12, books )
	_execute('INSERT INTO devices (serial, alias, fiona_id, kind, lto, last_ip, last_cookie, p12, books) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', params)

def update(device):
	books = None if not device.books else pickle.dumps(device.books)
	params = ( device.alias, device.fiona_id, device.lto, device.last_ip, device.last_cookie, device.p12, books, device.serial )
	_execute('UPDATE devices SET alias = ?, fiona_id = ?, lto = ?, last_ip = ?, last_cookie = ?, p12 = ?, books = ? WHERE serial = ?', params)

def load_all():
	with sqlite3(_db_path) as db:
		db.row_factory = sqlite3_Row
		for row in db.execute('SELECT * FROM devices'):
			row = dict(row)
			yield _Device(**row)

def update_all(devices):
	params = [ ( d.alias, d.fiona_id, d.kind, d.lto, d.last_ip, d.last_cookie, d.p12, pickle.dumps(d.books) if d.books else None, d.serial )
					for d in devices if not d.is_provisional() ]
	_execute('UPDATE devices SET alias = ?, fiona_id = ?, kind = ?, lto = ?, last_ip = ?, last_cookie = ?, p12 = ?, books = ? WHERE serial = ?', params)
	logging.info("saved %d device(s) to %s", len(params), _db_path)


_db_path = os.path.join(config.database_path, 'devices.sqlite')

# we try to create the database schema every time the proxy starts, just in case
# hopefully won't have to do any stupid schema migration in the future... :P
_execute('''
CREATE TABLE IF NOT EXISTS devices (
	serial TEXT PRIMARY_KEY,
	alias TEXT,
	fiona_id TEXT,
	kind TEXT,
	lto INTEGER DEFAULT -1,
	last_ip TEXT,
	last_cookie TEXT,
	p12 BLOB,
	books BLOB
)''')
_execute('CREATE INDEX IF NOT EXISTS index_devices_serial ON devices ( serial )')

from devices.db_migration import migrate_3
migrate_3(_db_path)
del migrate_3
