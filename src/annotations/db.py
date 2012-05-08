from sqlite3 import connect as sqlite3
from collections import namedtuple
import os.path

import config


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

def list(asin):
	if not asin:
		return None
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

def get_last_read(asin):
	if asin:
		with sqlite3(_db_path) as db:
			db.row_factory = _namedtuple_row_factory
			# it's enough to check the last_read table
			# if there are no entries there, quite unlikely to have bookmarks/notes/etc
			c = db.execute('SELECT * FROM last_read WHERE asin = ?', (asin, ))
			return c.fetchone() if c else None

def set_last_read(asin, timestamp, begin, position, state):
	_execute('INSERT OR IGNORE INTO last_read VALUES (?, ?, ?, ?, ?, ?)', (None, asin, '', 0, 0, b''))
	_execute('UPDATE last_read SET timestamp = ?, begin = ?, pos = ?, state = ? WHERE asin = ?',
			(timestamp, begin, position, state, asin))

def create(asin, kind, timestamp, begin, end, position, state, text):
	_execute('INSERT INTO annotations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
			(None, asin, kind, timestamp, begin, end, position, state, text))

def delete(asin, kind, timestamp, begin, end):
	_execute('DELETE FROM annotations WHERE asin = ? AND kind = ? AND begin = ? and end = ?',
			(asin, kind, begin, end))

def modify(asin, kind, timestamp, begin, end, text):
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
