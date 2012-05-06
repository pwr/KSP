import logging, uuid

from devices.device import Device as _Device
import devices.db as _db
import devices.certificate as _certificate


def _update(device, ip = None, cookie = None, kind = None):
	cookie_matches = cookie == device.last_cookie
	if not cookie_matches and cookie and device.last_cookie:
		cookie_matches = cookie.startswith(device.last_cookie)
	kind_matches = kind == device.kind
	if not kind_matches and kind and device.kind:
		kind_matches = device.kind.startswith(kind)
	if ip == device.last_ip and cookie_matches and kind_matches:
		# only bother writing to the db if any of them changed
		return device
	logging.debug("updating device %s with ip %s and cookie %s", device, ip, cookie[:12] if cookie else None)
	device.last_ip = ip
	if cookie:
		device.last_cookie = cookie[:64]
	if not kind_matches:
		# only update the device kind when it's more specific than the one we knew
		device.kind = kind
	_db.update(device)
	return device

def get(serial):
	"""gets a device by serial"""
	return _devices.get(serial)

def update_pkcs12(device, cookie = None, fiona_id = None, pkcs12_bytes = None):
	if cookie:
		device.last_cookie = cookie[:64]
	if fiona_id:
		device.fiona_id = fiona_id
	if pkcs12_bytes:
		test_context = _certificate.make_context(device.serial, pkcs12_bytes)
		if not test_context:
			logging.error("%s tried to update PKCS12 key with invalid data -- ignored")
		else:
			logging.warn("%s updated its PKCS12 client key", device)
			device.p12 = pkcs12_bytes
			# Even though we're updating the client certificate, active connections will still work with the old one.
			# Actually, the old certificate will still be able to open new connections for an unknown amount of time.
			# So there's no point in destroying the current SSL context and creating a new one.
	_db.update(device)

def detect(ip, cookie = None, kind = None, serial = None):
	"""
	guess the device that made a request
	if no matching device exists in our database, one may be created on the spot
	"""
	found = None
	for d in _devices.values():
		if serial:
			if serial == d.serial:
				found = d
				break
			if not d.is_provisional():
				continue
		if cookie and d.last_cookie:
			if cookie[:64] == d.last_cookie:
				found = d
				break
		if kind and d.kind:
			if kind.partition('-')[0] != d.kind.partition('-')[0]:
				continue
		# very flimsy, especially when the request is port-forwarded through a router
		if ip == d.last_ip:
			logging.warn("matched device by ip: %s => %s", ip, d)
			found = d
			break

	if found:
		_update(found, ip = ip, cookie = cookie, kind = kind)
		if found.is_provisional() and serial:
			if found.load_context(serial):
				if found.serial in _devices:
					del _devices[found.serial]
				found.serial = serial
				_devices[serial] = found
				_db.insert(found)
				logging.warn("registered device %s", found)
		return found

	# create new device, may be provisional
	device = _Device(serial = serial, kind = kind, last_ip = ip, last_cookie = cookie)
	_devices[device.serial] = device
	if not device.is_provisional():
		_db.insert(device)
	return device

def save_all():
	_db.update_all(_devices.values())


### module initialization
_devices = { d.serial: d for d in _db.load_all() }
