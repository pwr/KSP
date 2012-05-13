import logging, os.path
from sqlite3 import connect as sqlite3
from collections import namedtuple

import config


def _namedtuple_row_factory(cursor, row):
	fields = [ col[0] for col in cursor.description ]
	Row = namedtuple('Row', fields)
	return Row(*row)

def _execute(query, parameters = ()):
	try:
		with sqlite3(_db_path) as db:
			if query.startswith('INSERT INTO '):
				qmarks = ('?', ) * len(parameters)
				query = query.replace('*', ','.join(qmarks))
			db.execute(query, parameters)
			db.commit()
			logging.debug("execute %s %s", query, parameters)
	except:
		logging.exception("execute %s %s", query, parameters)

def get_all(asin):
	with sqlite3(_db_path) as db:
		db.row_factory = _namedtuple_row_factory
		# pick the latest last_read
		result = [ lr for lr in db.execute('SELECT * FROM last_read2 WHERE asin = ? ORDER BY timestamp DESC LIMIT 1', (asin, )) ]
		result.extend(db.execute('SELECT * FROM annotations2 WHERE asin = ? AND pos > 0 ORDER BY timestamp', (asin, )))
		return result

def list_last_read(asin, count = -1):
	# lists all last_reads, in reverse timestamp order
	with sqlite3(_db_path) as db:
		db.row_factory = _namedtuple_row_factory
		return [ lr for lr in db.execute('SELECT * FROM last_read2 WHERE asin = ? ORDER BY timestamp DESC LIMIT ' + str(count), (asin, )) ]

def set_last_read(device_serial, asin, timestamp, begin, position, state):
	# only replace this device's last_read, so the other ones may know if they need updates
	_execute('DELETE FROM last_read2 WHERE asin = ? AND device = ?', (asin, device_serial))
	_execute('INSERT INTO last_read2 (id, asin, device, timestamp, begin, pos, state) VALUES (*)',
			(None, asin, device_serial, timestamp, begin, position, state))

def delete_last_read(device_serial, asin):
	_execute('DELETE FROM last_read2 WHERE asin = ? AND device = ?', (asin, device_serial))

def get_last_read_updates(device_serial, furthest = True):
	with sqlite3(_db_path) as db:
		db.row_factory = _namedtuple_row_factory
		# get all book ids for which this device has last_read entries
		device_books = [ r[0] for r in db.execute('SELECT asin FROM last_read2 WHERE device = ?', (device_serial, )) ]
		# logging.debug("%s has last_read for %s", device_serial, device_books)
		# get all entries where the latest read was done by some other device
		if furthest:
			last_read_query = 'SELECT * FROM last_read2 GROUP BY asin HAVING pos = MAX(pos) AND device != ?'
		else:
			last_read_query = 'SELECT * FROM last_read2 GROUP BY asin HAVING timestamp = MAX(timestamp) AND device != ?'
		latest_lr = [ lr for lr in db.execute(last_read_query, (device_serial, )) ]
		# only pick the latest entries done by other devices, when this device also has an entry
		latest_lr = [ lr for lr in latest_lr if lr.asin in device_books ]
		if latest_lr:
			logging.debug("%s needs to update last_read from %s", device_serial, [ (lr.asin, lr.device, lr.pos) for lr in latest_lr ])
		return latest_lr

def create(device_serial, asin, kind, timestamp, begin, end, position, state, text):
	_execute('INSERT INTO annotations2 VALUES (*)',
			(None, asin, device_serial, kind, timestamp, begin, end, position, state, text, None))

def delete(device_serial, asin, kind, timestamp, begin, end):
	# only mark it as deleted, so other devices can be notified of it
	_execute('''UPDATE annotations2 SET device = ?, timestamp = ?, pos = ?, state = ?, text = ?, other_devices = ?
				WHERE asin = ? AND kind = ? AND begin = ? AND end = ?''',
			(device_serial, timestamp, -1, None, None, None, asin, kind, begin, end))

def modify(device_serial, asin, kind, timestamp, begin, end, text):
	_execute('''UPDATE annotations2 SET device = ?, timestamp = ?, text = ?, other_devices = ?
				WHERE asin = ? AND kind = ? AND begin = ? AND end = ?''',
			(device_serial, timestamp, text, None, asin, kind, begin, end))


_db_path = os.path.join(config.database_path, 'sidecar.sqlite')

# we try to create the database schema every time the proxy starts, just in case
# hopefully won't have to do any stupid schema migration in the future... :P
_execute('''
CREATE TABLE IF NOT EXISTS last_read2 (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	asin TEXT NOT NULL,
	device TEXT NOT NULL,
	timestamp INTEGER NOT NULL,
	begin INTEGER NOT NULL,
	pos INTEGER NOT NULL,
	state BLOB NOT NULL
)''')
_execute('CREATE INDEX IF NOT EXISTS index_last_read2_asin_timestamp_desc ON last_read2 (asin, timestamp DESC)')
_execute('CREATE INDEX IF NOT EXISTS index_last_read2_asin_device ON last_read2 (asin, device)')
_execute('CREATE INDEX IF NOT EXISTS index_last_read2_device ON last_read2 (device)')

_execute('''
CREATE TABLE IF NOT EXISTS annotations2 (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	asin TEXT NOT NULL,
	device TEXT NOT NULL,
	kind TEXT NOT NULL,
	timestamp INTEGER NOT NULL,
	begin INTEGER NOT NULL,
	end INTEGER NOT NULL,
	pos INTEGER NOT NULL,
	state BLOB,
	text TEXT,
	other_devices BLOB
)''')
_execute('CREATE INDEX IF NOT EXISTS index_annotations2_apt ON annotations2 (asin, pos, timestamp)')
_execute('CREATE INDEX IF NOT EXISTS index_annotations2_akbe ON annotations2 (asin, kind, begin, end)')

from annotations.db_migration import migrate_2
migrate_2(_db_path, _namedtuple_row_factory)
del migrate_2
