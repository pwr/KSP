import logging
import xml.dom.minidom as minidom

from content import read_chunked, query_params, compress, decompress
import qxml


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
	if req.length > 0:
		req.body = req.rfile.read(req.length)
	else:
		req.body = None

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

def is_signed(req):
	return 'X-ADP-Request-Digest' in req.headers

def client_ip(req):
	return req.headers.get('X-Forwarded-For') or req.client_address[0]

def get_query_params(req):
	_, _, query = req.path.partition('?')
	if query:
		return query_params(query)
	q = {}
	if is_signed(req) and req.command == 'POST' and req.body and req.headers['Content-Type'] == 'text/xml':
		with minidom.parseString(req.body) as doc:
			parameters = qxml.get_child(qxml.get_child(doc, 'request'), 'parameters')
			for p in qxml.list_children(parameters):
				q[p.nodeName] = qxml.get_text(p)
	return q

def body_text(req):
	return decompress(req.body, req.content_encoding)

def update_body(req, new_body = None):
	if is_signed(req):
		raise Exception("cannot update body of signed request", req, new_body)
	req.body = compress(new_body, req.content_encoding)
	req.length = len(req.body or b'')
	req.headers.replace_header('Content-Length', req.length)
