from sqlite3 import connect as sqlite3


def migrate_3(db_path):
	with sqlite3(db_path) as db:
		try: db.execute('ALTER TABLE devices ADD COLUMN alias TEXT')
		except: pass
		try: db.execute('ALTER TABLE devices ADD COLUMN kind TEXT')
		except: pass
		try: db.execute('ALTER TABLE devices ADD COLUMN lto INTEGER DEFAULT -1')
		except: pass
		db.execute('VACUUM')
