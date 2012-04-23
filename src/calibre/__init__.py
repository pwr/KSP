import logging, time

import formats # this is necessary to compute features.supported_formats

import calibre.db as _db
LIBRARY_ID = _db.get_library_id()

from calibre.book import Book as _Book


def missing_from_library(asin, device):
	last_downloaded = device.books.get(asin)
	if last_downloaded == 0:
		logging.debug("%s forgetting about %s", device, asin)
		device.books.pop(asin, None)

def _book_refresh(uuid, asin, book, book_dict, timestamp):
	if not book_dict:
		book_dict = _db.reload(uuid)
	if not book_dict:
		logging.debug("book %s not in library", uuid)
		# no book_dict, means it's not even in the calibre database, so we can forget about it
		_books.pop(uuid, None) # this should be an exception-free 'del'
		_books.pop(asin, None)
		return None
	if book:
		book.update(book_dict, timestamp)
	else:
		book = _Book(book_dict, timestamp)
		_books[book.asin] = book
	return book

def books(refresh = False):
	"""
	gets the current books map, optionally updating it from the calibre db first
	"""
	if refresh:
		started_at = time.time()
		book_dicts = _db.reload_all()
		if book_dicts:
			# we use the timestamp to mark which books we've updated this round
			# so that we know which book have disappeared from the library since the last update
			timestamp = _db.last_update

			while book_dicts:
				book_id, book_dict = book_dicts.popitem()
				uuid = book_dict['uuid']
				asin = uuid
				book = _books.get(asin)
				if not book:
					asin2 = asin.replace('-', '')
					book = _books.get(asin2)
					if book:
						asin = book.asin
				_book_refresh(uuid, asin, book, book_dict, timestamp) # adds it to _books as well

			for book in list(_books.values()):
				if book._timestamp != timestamp: # removed from the library
					logging.warn("book was in library but missing after refresh: %s", book)
					_books.pop(book.asin, None)

			load_duration = time.time() - started_at
			logging.info("Calibre Library loaded and processed in %d:%02.3f minutes, at an average %.3f seconds/book",
					load_duration // 60, load_duration % 60, load_duration / len(_books))

	return _books

def book(asin, refresh = False):
	"""
	gets the Book for a given asin, optionally updating it from the calibre db first
	"""
	if not asin:
		logging.warn("tried to find book with no asin")
		return None
	uuid = asin
	book = _books.get(asin)
	if book:
		uuid = book.uuid
		asin = book.asin
	if refresh or not book:
		book = _book_refresh(uuid, asin, book, None, 0)
	return book


# module initialization
_books = {}
books(True) # force load all the books
