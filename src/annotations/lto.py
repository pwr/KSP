import logging, time


def parse_timestamp(timestamp, lto = None):
	if not timestamp:
		logging.warn("can't parse timestamp from %s", timestamp)
		return 0
	try:
		t = time.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
	except:
		logging.warn("failed to parse timestamp %s", timestamp)
		return 0
	t = time.mktime(t)
	# the datetime has been parsed as beeing in the server's localtime, but it actually is in the device's lto
	if lto is not None:
		# if we know the device's lto, we apply it
		# otherwise the default will be the server's lto
		# so we undo the server's timezone...
		t -= time.altzone if time.daylight else time.timezone
		# and then apply the device's lto
		t -= lto * 60
	logging.debug("parse_timestamp %s, %d => %d => %s", timestamp, -1 if lto is None else lto , t, time.ctime(t))
	return int(t)

def device_lto(device = None):
	return device.lto if device and device.lto != -1 else ((time.altzone if time.daylight else time.timezone) / -60)
