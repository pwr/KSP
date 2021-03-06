import logging
import xml.dom.minidom as minidom
import hashlib, binascii

from content import read_chunked, query_params, compress, decompress
import qxml


def is_signed(req):
	return 'X-ADP-Request-Digest' in req.headers

def get_query_params(req):
	_, _, query = req.path.partition('?')
	if query:
		return query_params(query)
	q = {}
	if is_signed(req) and req.command == 'POST' and req.body and req.headers['Content-Type'] == 'text/xml':
		try:
			with minidom.parseString(req.body) as doc:
				x_request = qxml.get_child(doc, 'request')
				x_parameters = qxml.get_child(x_request, 'parameters')
				for p in qxml.list_children(x_parameters):
					q[p.nodeName] = qxml.get_text(p)
		except: pass
	return q

def read_body_and_length(req):
	"""
	fully reads the request body, also handles chunked content
	gzipped content is read as-is
	sets req.body, req.length and req.content_encoding
	"""
	req.content_encoding = req.headers.get('Content-Encoding')
	if req.content_encoding:
		logging.warn("request (%s) has Content-Encoding %s", req.requestline, req.content_encoding)

	transfer_encoding = req.headers['Transfer-Encoding']
	if transfer_encoding:
		if 'chunked' != transfer_encoding:
			raise Exception("Transfer-Encoding not supported", transfer_encoding)
		logging.warn("request (%s) has chunked body", req.requestline)
		req.body = read_chunked(req.rfile)
		req.length = len(req.body or b'')
		del req.headers['Content-Length']
		req.headers['Content-Length'] = req.length
		del req.headers['Transfer-Encoding']
		return

	req.length = int(req.headers.get('Content-Length', 0))
	req.body = req.rfile.read(req.length) if req.length else None

def body_text(req):
	return decompress(req.body, req.content_encoding)

def update_body(req, new_body = None):
	if is_signed(req):
		raise Exception("cannot update body of signed request", str(req), new_body)
	req.body = compress(new_body, req.content_encoding)
	req.length = len(req.body or b'')
	del req.headers['Content-Length']
	req.headers['Content-Length'] = req.length

#
#
#

def xfsn(req):
	xfsn = req.headers['X-fsn']
	if xfsn:
		return xfsn
	xadp = req.headers['X-ADP-Authentication-Token']
	if xadp:
		return xadp
	cookie = req.headers['Cookie']
	if cookie and cookie.startswith('x-fsn='):
		return cookie[6:]

def get_device_serial(req):
	xdsn = req.headers['X-DSN']
	if xdsn:
		return xdsn
	xadp = req.headers['X-ADP-Authentication-Token']
	if xadp:
		# crap, there's no real way to identify the device besides the IP
		ua = req.headers.get('User-Agent', 'no-user-agent')
		client_address = req.headers['X-Forwarded-For'] or req.client_address[0]
		md5 = hashlib.md5()
		md5.update(bytes(ua, 'ascii'))
		md5.update(bytes(client_address, 'ascii'))
		return str(binascii.hexlify(md5.digest()), 'ascii')
	# if req.command == 'GET':
	# 	q = get_query_params(req)
	# 	if 'serialNumber' in q:
	# 		return q['serialNumber']
	# if req.command == 'POST' and req.headers['Content-Type'] == 'application/x-www-form-urlencoded':
	# 	q = query_params(body_text(req))
	# 	if 'deviceSerialNumber' in q:
	# 		return q['deviceSerialNumber']

_DEVICE_FAMILIES = {
		'A2XIMM7ACS4GUS' : 'desktop-pc',
		'A3BHV8OQ3W90PJ' : 'desktop-mac',
		'A2DRYVRL4HBK7V' : 'android', # beaver ?
		'A3VNNDO1I14V03' : 'android', # redding
		'A2Y8LFC259B97P' : 'android', # tablet (whiskeytown)
		'ATVPDKIKX0DER'  : 'kindle-1',			# 0x01
		'A3UN6WX5RRO2AG' : 'kindle-2us',		# 0x02
		'A1F83G8C2ARO7P' : 'kindle-2intl',		# 0x03
		'A1PA6795UKMFR9' : 'kindle-DXus',		# 0x04
		'A13V1IB3VIYZZH' : 'kindle-DXintl',		# 0x05
		'A1VC38T7YXB528' : 'kindle-3wifi3g',	# 0x06
		'A2EUQ1WTGCTBG2' : 'kindle',			# 0x07 3?
		'A3AEGXETSR30VB' : 'kindle-3wifi',		# 0x08
		'A3P5ROKL5A1OLE' : 'kindle-DXgraphite',	# 0x09
		'A3JWKAKR8XB7XF' : 'kindle-3wifi3geu',	# 0x0A
		'A1X6FK5RDHNB96' : 'kindle',			# 0x0B 4?
		'AN1VRQENFRJN5'  : 'kindle',			# 0x0C 4?
		'A3DWYIK6Y9EEQB' : 'kindle',			# 0x0D 4?
		'A3R76HOPU0Z2CB' : 'kindle-4intl',		# 0x0E
		'?1' : 'kindle-5wifi3g', # 0x0F
		'?2' : 'kindle-5wifi', # 0x11
	}

def guess_client(req):
	xdfv = req.headers['X-DeviceFirmwareVersion']
	if xdfv and xdfv.startswith('Kindle '):
		return 'kindle-' + xdfv[7]
	xdevtype = req.headers['X-DeviceType']
	if xdevtype and xdevtype in _DEVICE_FAMILIES:
		return _DEVICE_FAMILIES[xdevtype]
	ua = req.headers['User-Agent']
	if ua == 'Java/phoneme_advanced-Core-1.3-b03 A2Z-SOW2-CR2-20100225-b01':
		# this could be kindle-4 or kindle-3, I think
		return 'kindle'
	if ua and ' Android ' in ua:
		for a in ua.split(';'):
			if a.strip().startswith('Android '):
				return 'android-' + a[9:]
		return 'android'
	xadptoken = req.headers['X-ADP-Authentication-Token']
	if xadptoken and xadptoken.startswith('{enc:') and ua == 'Mozilla/5.0':
		return 'desktop-pc' # or 'desktop-mac'?
	if '?currentTransportMethod=' in req.path or '&currentTransportMethod=' in req.path:
		return 'kindle'

def client_ip(req):
	return req.headers['X-Forwarded-For'] or req.client_address[0]
