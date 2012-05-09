import os.path, logging
import binascii, time

import calibre
import annotations.db as _db
from annotations.lto import parse_timestamp as _parse_timestamp


def apnx_path(book):
	if book and book.file_path:
		a_path = os.path.splitext(book.file_path)[0] + '.apnx'
		# logging.debug("checking for apnx file %s", apnx_path)
		if os.path.isfile(a_path):
			return a_path

def get_last_read(asin, device = None):
	llr = _db.list_last_read(asin, 1, device)
	return llr[0] if llr else None


def has(asin):
	return asin and _db.list_last_read(asin, 1)

list_last_read = _db.list_last_read
get_all = _db.get_all

def _bin(state):
	if state:
		state = bytes(state, 'ascii')
		return binascii.unhexlify(state)
	return None

def set_last_read(device, asin, timestamp, begin, position, state):
	timestamp = _parse_timestamp(timestamp, device.lto)
	begin = int(begin)
	position = int(position)
	state = _bin(state)
	db.set_last_read(device.serial, asin, timestamp, begin, position, state)

def create(device, asin, kind, timestamp, begin, end, position, state, text = None):
	timestamp = _parse_timestamp(timestamp, device.lto)
	begin = int(begin)
	end = int(end)
	position = int(position)
	state = _bin(state)
	db.create(device.serial, asin, kind, timestamp, begin, end, position, state, text)

def delete(device, asin, kind, timestamp, begin, end):
	timestamp = _parse_timestamp(timestamp, device.lto)
	begin = int(begin)
	end = int(end)
	db.delete(device.serial, asin, kind, timestamp, begin, end)

def modify(device, asin, kind, timestamp, begin, end, text = None):
	timestamp = _parse_timestamp(timestamp, device.lto)
	begin = int(begin)
	end = int(end)
	db.modify(device.serial, asin, kind, timestamp, begin, end, text)
