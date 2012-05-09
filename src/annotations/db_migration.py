import logging
from sqlite3 import connect as sqlite3

from annotations.lto import parse_timestamp


def _migrate_2_last_read(db_path, row_factory):
	try:
		with sqlite3(db_path) as db:
			db.row_factory = row_factory
			for lr in db.execute('SELECT * FROM last_read'):
				# all the timestamp the device sent are local time
				timestamp = parse_timestamp(lr.timestamp)
				db.execute('INSERT INTO last_read2 VALUES (?, ?, ?, ?, ?, ?, ?)',
					(None, lr.asin, 'UNKNOWN', timestamp, lr.begin, lr.pos, lr.state))
	except:
		logging.exception("migrating to last_read2")
	finally:
		db.execute('DROP TABLE IF EXISTS last_read')

def _migrate_2_annotations(db_path, row_factory):
	try:
		with sqlite3(db_path) as db:
			db.row_factory = row_factory
			for anot in db.execute('SELECT * FROM annotations'):
				# all the timestamp the device sent are local time
				timestamp = parse_timestamp(anot.timestamp)
				db.execute('INSERT INTO annotations2 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
					(None, anot.asin, 'UNKNOWN', anot.kind, timestamp, anot.begin, anot.end, anot.pos, anot.state, anot.text, None))
	except:
		logging.exception("migrating to annotations2")
	finally:
		db.execute('DROP TABLE IF EXISTS annotations')

def migrate_2(db_path, row_factory):
	_migrate_2_last_read(db_path, row_factory)
	_migrate_2_annotations(db_path, row_factory)
	with sqlite3(db_path) as db:
		db.execute('VACUUM')
		db.commit()
