import os.path, logging, time

import calibre_db
LIBRARY_ID = calibre_db.get_library_id()
import sidecar_db, formats
import config, features


class _Book:
	def __init__(self, book_dict, timestamp):
		self.asin = book_dict['uuid']
		self.uuid = self.asin
		self.added_to_library = book_dict['added_to_library']
		self.last_modified = -1
		self.file_path = None
		self.update(book_dict, timestamp)
		logging.debug("book loaded %s", self)

	def update(self, book_dict, timestamp = 0):
		"""
		updates the book info from the dict
		also checks each file for existance, size and last time of modification
		"""
		previously_modified = self.last_modified
		self._timestamp = timestamp
		self.title = book_dict['title']
		self.last_modified = book_dict["last_modified"]
		self.publication_date = book_dict["publication_date"]
		self.authors = book_dict["authors"]
		self.publishers = book_dict["publishers"]
		self.languages = [ v[:2] for v in book_dict["languages"] ]

		self._ebook_file(book_dict['path'], book_dict["files"])

		if self.cde_content_type == 'PDOC':
			if len(self.asin) == 36:
				self.asin = self.asin.replace('-', '')
		elif self.cde_content_type == 'EBOK' and len(self.asin) == 32:
			raise Exception("book %s had type PDOC, can't switch to EBOK")

		if previously_modified > 0 and self.last_modified != previously_modified:
			logging.debug("book updated %s", self)

	def _ebook_file(self, book_path, files_dict):
		for format, content_type in formats.CONTENT_TYPES.items():
			name = files_dict.get(format)
			if not name:
				continue

			filename = name + '.' + format.lower()
			path = os.path.join(config.calibre_library, book_path, filename)
			if not os.path.isfile(path):
				continue

			file_last_modified = os.path.getmtime(path)
			if path == self.file_path and file_last_modified <= self.last_modified:
				# we're doing an update of an already-loaded book, and the file did not change
				return

			if formats.handles(content_type):
				cde_type = formats.read_cde_type(path, content_type, self.asin)
				if not cde_type:
					continue
				self.cde_content_type = cde_type
			else:
				self.cde_content_type = formats.CDE_TYPES[format]

			self.file_path = path
			self.file_size = os.path.getsize(path)
			self.content_type = content_type
			if self.last_modified < file_last_modified:
				self.last_modified = file_last_modified
			return

		self.file_path = None
		self.file_size = 0
		self.content_type = None
		self.cde_content_type = None

	def mark_on_device(self, device):
		if self.asin not in device.books or device.books[self.asin] == 0:
			logging.debug("%s has book %s", device, self)
		last_downloaded = device.books.get(self.asin)
		if not last_downloaded:
			# we don't really know when it was downloaded, let's fudge it...
			device.books[self.asin] = device.last_sync

	def mark_downloaded_by(self, device):
		logging.debug("%s downloaded %s", device, self)
		device.books[self.asin] = self.last_modified

	def is_known_to(self, device):
		return self.file_path is not None and self.asin in device.books

	def mark_known_to(self, device):
		if self.asin not in device.books:
			logging.debug("%s knows about %s", device, self)
		device.books.setdefault(self.asin, 0)

	def needs_update_on(self, device):
		if not self.file_path:
			return False
		last_downloaded = device.books.get(self.asin)
		return last_downloaded and self.last_modified > last_downloaded

	def has_sidecar(self):
		return sidecar_db.has(self.asin)

	def sidecar(self):
		return sidecar_db.list(self.asin)

	def apnx_path(self):
		apnx_path = os.path.splitext(self.file_path)[0] + '.apnx' if self.file_path else None
		# logging.debug("checking for apnx file %s", apnx_path)
		if os.path.isfile(apnx_path):
			return apnx_path

	def __str__(self):
		return '{%s (%s~%s) modified %d, %s %d}' % ( self.title, self.asin[:14], self.cde_content_type, self.last_modified, self.file_path, self.file_size )


def missing_from_library(asin, device):
	last_downloaded = device.books.get(asin)
	if last_downloaded == 0:
		logging.debug("%s forgetting about %s", device, asin)
		device.books.pop(asin, None)

def _book_refresh(uuid, asin, book, book_dict, timestamp):
	if not book_dict:
		book_dict = calibre_db.reload(uuid)
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
		book_dicts = calibre_db.reload_all()
		if book_dicts:
			# we use the timestamp to mark which books we've updated this round
			# so that we know which book have disappeared from the library since the last update
			timestamp = calibre_db.last_update

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

def _collections(asin_mappings):
	collections = {}
	for name, asin_list in asin_mappings.items():
		books_list = [ book(asin) for asin in asin_list ]
		books_list = [ b for b in books_list if b ]
		books_with_files = [ b for b in books_list if b.file_path ]
		if books_with_files: # if at least _some_ books in the collection has files
			collections[name] = books_list
	return collections

def series_collections():
	return _collections(calibre_db.load_series_collections())

def tag_collections():
	return _collections(calibre_db.load_tag_collections())


# module initialization
_books = {}
books(True) # force load all the books
