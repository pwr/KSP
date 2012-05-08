import os.path, logging
import binascii, time

import calibre
import annotations.db as _db


def apnx_path(book):
	if book and book.file_path:
		a_path = os.path.splitext(book.file_path)[0] + '.apnx'
		# logging.debug("checking for apnx file %s", apnx_path)
		if os.path.isfile(a_path):
			return a_path

get_last_read = _db.get_last_read

def has(asin):
	return asin and _db.get_last_read(asin) is not None

def list(asin):
	return _db.list(asin)

def _bin(state):
	if state:
		state = bytes(state, 'ascii')
		return binascii.unhexlify(state)
	return None

def set_last_read(asin, timestamp, begin, position, state):
	begin = int(begin)
	position = int(position)
	state = _bin(state)
	db.set_last_read(asin, timestamp, begin, position, state)

def create(asin, kind, timestamp, begin, end, position, state, text):
	begin = int(begin)
	end = int(end)
	position = int(position)
	state = _bin(state)
	db.create(asin, kind, timestamp, begin, end, position, state, text)

def delete(asin, kind, timestamp, begin, end):
	begin = int(begin)
	end = int(end)
	db.delete(asin, kind, timestamp, begin, end)

def modify(asin, kind, timestamp, begin, end, text):
	begin = int(begin)
	end = int(end)
	db.modify(asin, kind, timestamp, begin, end, text)
