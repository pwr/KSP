import os.path
import binascii, time

import calibre
import annotations.db as _db
from annotations.lto import parse_timestamp as _parse_timestamp


def apnx_path(book):
	if book and book.file_path:
		a_path = os.path.splitext(book.file_path)[0] + '.apnx'
		if os.path.isfile(a_path):
			return a_path

def get_last_read(asin):
	llr = _db.list_last_read(asin, 1)
	return llr[0] if llr else None

def has(asin):
	return asin and _db.list_last_read(asin, 1)

get_all = _db.get_all
list_last_read = _db.list_last_read

def get_last_read_updates(device, furthest = True):
	"""
	get last_read records from other devices that this device should be notified about
	if 'furthest' is True, records are picked by the furthest location in the book
	otherwise, the latest records are picked
	"""
	lru = _db.get_last_read_updates(device.serial, furthest)
	# only return last_read updates for the books we know to be on the device
	return [ lr for lr in lru if device.books.get(lr.asin) > 0 ]

def last_read_updated(device, asin):
	# a device has applied last_read updates for a book, so we can delete its entry
	# this way the next time the device asks for last_read updates, this book will be skipped
	_db.delete_last_read(device.serial, asin)

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
