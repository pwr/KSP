import os.path, logging
from sqlite3 import connect as sqlite3
from collections import namedtuple
import binascii, time

import config, calibre


def _namedtuple_row_factory(cursor, row):
    fields = [ col[0] for col in cursor.description ]
    Row = namedtuple('Row', fields)
    return Row(*row)

def _execute(query, parameters = ()):
	# logging.debug("execute %s %s", query, parameters)
	with sqlite3(_db_path) as db:
		db.execute(query, parameters)
		db.commit()
		return db.total_changes > 0
	return False

def apnx_path(asin):
	if not asin:
		return None
	if type(asin) == str:
		book = calibre.book(asin)
	else:
		book = asin
	apnx_path = os.path.splitext(book.file_path)[0] + '.apnx' if book.file_path else None
	# logging.debug("checking for apnx file %s", apnx_path)
	if os.path.isfile(apnx_path):
		return apnx_path

def has(asin):
	if not asin:
		return None
	if type(asin) != str:
		asin = asin.asin
	with sqlite3(_db_path) as db:
		# it's enough to check the last_read table
		# if there are no entries there, quite unlikely to have bookmarks/notes/etc
		c = db.execute('SELECT COUNT(asin) FROM last_read WHERE asin = ?', (asin, ))
		row = c.fetchone() if c else None
		if row is None:
			return False
		if row[0] > 1:
			logging.error("found multiple last_read entries for %s: %d", asin, row[0])
		return row[0] > 0
	return False

def list(asin):
	if not asin:
		return None
	if type(asin) != str:
		asin = asin.asin
	result = []
	with sqlite3(_db_path) as db:
		db.row_factory = _namedtuple_row_factory
		result = [ lr for lr in db.execute('SELECT * FROM last_read WHERE asin = ?', (asin, )) ]
		if len(result) > 1:
			logging.error("found multiple last_read entries for %s: %s", asin, result)
			result = [ result[0] ] # erm...
		for item in db.execute('SELECT * FROM annotations WHERE asin = ? ORDER BY timestamp', (asin, )):
			result.append(item)
	return result

def _bin(state):
	if state:
		state = bytes(state, 'ascii')
		return binascii.unhexlify(state)
	return None

def last_read(asin, timestamp, begin, position, state):
	begin = int(begin)
	position = int(position)
	state = _bin(state)
	_execute('INSERT OR IGNORE INTO last_read VALUES (?, ?, ?, ?, ?, ?)', (None, asin, '', 0, 0, b''))
	_execute('UPDATE last_read SET timestamp = ?, begin = ?, pos = ?, state = ? WHERE asin = ?',
			(timestamp, begin, position, state, asin))

def create(asin, kind, timestamp, begin, end, position, state, text):
	begin = int(begin)
	end = int(end)
	position = int(position)
	state = _bin(state)
	_execute('INSERT INTO annotations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
			(None, asin, kind, timestamp, begin, end, position, state, text))

def delete(asin, kind, timestamp, begin, end):
	begin = int(begin)
	end = int(end)
	_execute('DELETE FROM annotations WHERE asin = ? AND kind = ? AND begin = ? and end = ?',
			(asin, kind, begin, end))

def modify(asin, kind, timestamp, begin, end, text):
	begin = int(begin)
	end = int(end)
	_execute('UPDATE annotations SET timestamp = ?, text = ? WHERE asin = ? AND kind = ? AND begin = ? AND end = ?',
			(timestamp, text, asin, kind, begin, end))


_db_path = os.path.join(config.database_path, 'sidecar.sqlite')

# we try to create the database schema every time the proxy starts, just in case
# hopefully won't have to do any stupid schema migration in the future... :P
_execute('''
CREATE TABLE IF NOT EXISTS last_read (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	asin TEXT NOT NULL UNIQUE,
	timestamp TEXT NOT NULL,
	begin INTEGER NOT NULL,
	pos INTEGER NOT NULL,
	state BLOB NOT NULL
)''')
_execute('''
CREATE TABLE IF NOT EXISTS annotations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	asin TEXT NOT NULL,
	kind TEXT NOT NULL,
	timestamp TEXT NOT NULL,
	begin INTEGER NOT NULL,
	end INTEGER NOT NULL,
	pos INTEGER NOT NULL,
	state BLOB NOT NULL,
	text TEXT
)''')
