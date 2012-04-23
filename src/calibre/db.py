import os.path, logging, time
import sqlite3

import config, features


def _clean_timeformat(text):
	"""returns an ISO date format from a funny calibre date format"""
	if text.endswith("+00:00"):
		text = text[:-6] + "+0000"
	if text[10] == " ":
		text = text.replace(" ", "T", 1)
	return text

def _parse_timestamp(text):
	"""converts calibre date time to a posix timestamp"""
	if text.endswith("+00:00"):
		text = text[:-6]
	if text.endswith("+0000"):
		text = text[:-5]
	if text[10] == " ":
		text = text.replace(" ", "T", 1)

	try:
		if len(text) == 19:
			t = time.strptime(text, "%Y-%m-%dT%H:%M:%S")
		else:
			t = time.strptime(text, "%Y-%m-%dT%H:%M:%S.%f")
	except:
		# failed to parse...
		logging.exception('parsing %s', text)
		return 0

	try:
		return time.mktime(t)
	except OverflowError:
		logging.exception('timestamp %s', t)
		# some funny dates like 1969-??-?? will throw this...
		return 0

def _book_dict(row):
	return None if row is None else {
			'id' : row['id'],
			'uuid' : row['uuid'],
			'title' : row['title'],
			'path' : row['path'],
			'publication_date' : _clean_timeformat(row['pubdate']),
			'added_to_library' : _parse_timestamp(row['timestamp']),
			'last_modified' : _parse_timestamp(row['last_modified']),
			'authors' : [],
			'publishers' : [],
			'languages' : [],
			'files' : {},
		}

def _update_book_list(cursor, books_map, field, query, params = ()):
	for row in cursor.execute(query, params):
		book = books_map[row[0]]
		book[field].append(row[1])

def _update_book_map(cursor, books_map, field, query, params = ()):
	# logging.debug('"%s", %s', query, params)
	for row in cursor.execute(query, params):
		book = books_map[row[0]]
		book[field][row[1]] = row[2] if len(row) == 3 else row[2:]

def _db_connect():
	return sqlite3.connect(_db_path, isolation_level = 'DEFERRED')

def reload_all():
	"""
	reload the books map from the calibre library, but only if the library db file has changed since the last load
	if no changes were detected, returns None
	"""
	global last_update
	db_last_modified = os.path.getmtime(_db_path)
	if db_last_modified <= last_update:
		return None

	# last_update_string = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(last_update))

	books = {}
	load_start = time.time()
	with _db_connect() as db:
		db.row_factory = sqlite3.Row
		c = db.cursor()
		for row in c.execute("select id, uuid, title, path, pubdate, timestamp, last_modified from books"):
			# logging.debug("  %s", row)
			books[row['id']] = _book_dict(row)

		_update_book_list(c, books, 'authors',
				"select books_authors_link.book, authors.name from books_authors_link, authors"
					" where books_authors_link.author = authors.id")
		_update_book_list(c, books, 'publishers',
				"select books_publishers_link.book, publishers.name from books_publishers_link, publishers"
					" where books_publishers_link.publisher = publishers.id")
		_update_book_list(c, books, 'languages',
				"select books_languages_link.book, languages.lang_code from books_languages_link, languages"
					" where books_languages_link.lang_code = languages.id")

		formats_q = ','.join( ['?'] * len(features.supported_formats) )
		_update_book_map(c, books, 'files',
				"select book, format, name from data where format in (%s)" % formats_q, tuple(features.supported_formats))

	last_update = db_last_modified

	load_duration = time.time() - load_start
	logging.info("loaded %d book records in %.3f seconds (%s updated %s)", len(books), load_duration, _db_path, time.ctime(db_last_modified))

	return books

def reload(uuid):
	"""reload a single book, unconditionally"""

	# logging.debug("reloading book %s", uuid)
	with _db_connect() as db:
		db.row_factory = sqlite3.Row
		c = db.cursor()
		c.execute("select id, uuid, title, path, pubdate, timestamp, last_modified from books where uuid = ?", ( uuid, ))
		row = c.fetchone()
		if not row:
			logging.warn("book %s missing", uuid)
			return None

		book_id = row['id']
		book_dict = _book_dict(row)
		books = { book_id: book_dict }

		_update_book_list(c, books, 'authors',
				"select books_authors_link.book, authors.name from books_authors_link, authors"
					" where books_authors_link.book = ? and books_authors_link.author = authors.id", ( book_id, ))
		_update_book_list(c, books, 'publishers',
				"select books_publishers_link.book, publishers.name from books_publishers_link, publishers"
					" where books_publishers_link.book = ? and books_publishers_link.publisher = publishers.id", ( book_id, ))
		_update_book_list(c, books, 'languages',
				"select books_languages_link.book, languages.lang_code from books_languages_link, languages"
					" where books_languages_link.book = ? and books_languages_link.lang_code = languages.id", ( book_id, ))

		formats_q = ','.join( ('?',) * len(features.supported_formats) )
		_update_book_map(c, books, 'files',
				"select book, format, name from data where book = ? and format in (%s)" % formats_q, ( book_id, ) + tuple(features.supported_formats))

		return book_dict

def load_series_collections():
	series = {}

	with _db_connect() as db:
		for row in db.execute("select books.uuid, series.name from books, books_series_link, series"
				" where books.id = books_series_link.book and books_series_link.series = series.id"):
			name = row[1]
			series.setdefault(name, [])
			series[name].append(row[0])

	return series

def load_tag_collections():
	tags = {}

	with _db_connect() as db:
		for row in db.execute("select books.uuid, tags.name from books, books_tags_link, tags"
				" where books.id = books_tags_link.book and books_tags_link.tag = tags.id"):
			tag_name = row[1]
			if tag_name in features.collection_tags:
				tags.setdefault(tag_name, [])
				tags[tag_name].append(row[0])

	return tags

def get_library_id():
	with _db_connect() as db:
		for row in db.execute('SELECT uuid FROM library_id'):
			return row[0]
	logging.error("failed to get library id")


# module initialization

_db_path = os.path.join(config.calibre_library, "metadata.db")
if not os.path.isfile(_db_path):
	raise Exception("Calibre database not found at %s", _db_path)
last_update = 0
