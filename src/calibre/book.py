import os.path, logging

import config, formats, features


class Book:
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
		for format in features.supported_formats:
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

			content_type = formats.CONTENT_TYPES[format]
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

	def __str__(self):
		return '{%s (%s~%s) modified %d, %s %d}' % ( self.title, self.asin[:14], self.cde_content_type, self.last_modified, self.file_path, self.file_size )
