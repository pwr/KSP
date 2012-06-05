import logging, socket
from http.client import HTTPSConnection, HTTPException, _CS_IDLE
from threading import RLock

from handlers.dummy import Dummy
from server.response import wrap as wrap_response


from server import logger
http_debug = logger('http_debug').debug
del logger

_IDLE = 4 * 60 + 57 # seconds

class Upstream (Dummy):
	"""
	simple pass-through handler
	"""
	def _call_upstream(self, conn, request, first_attempt = True):
		try:
			http_debug("calling upstream (%s) %s", conn.host, request)
			conn.request(request.command, request.path, request.body, dict(request.headers))
			return conn.getresponse()
		except (socket.error, HTTPException) as ex:
			logging.warn("[%s:%s] (%s) %s %s", type(ex), ex, conn.host, request.command, request.path)
			conn.close()
			if first_attempt:
				return self._call_upstream(conn, request, False)
			raise Exception(conn.host, request.command, request.path, ex)
		finally:
			conn.last_call = request.started_at

	def _upstream_host(self, request, device):
		if request.is_signed() and self.service.endswith('-g7g') and not self.service.endswith('-ta-g7g'):
			return self.service.partition('-')[0] + '-ta-g7g.amazon.com'
		return self.service + '.amazon.com'

	def call_upstream(self, request, device):
		"""proxy a request to the originally intended server, returns a http response"""
		if device.is_provisional(): # not yet allowed access upstream
			logging.warn("device %s may not connect to upstream (provisional)")
			return None

		upstream_host = self._upstream_host(request, device)
		conn = device.connections.get(upstream_host)
		if not conn:
			# it's very unlikely a device will shoot two requests to the same service at the same time, just after KSP started
			# so we should be reasonable safe creating the connection without locking
			conn = HTTPSConnection(upstream_host, context = device.ssl_context(upstream_host))
			conn.last_call = 0
			conn._lock = RLock()
			logging.info("created upstream connection to %s for %s", upstream_host, device)
			conn = device.connections.setdefault(upstream_host, conn) # just in case...
		with conn._lock:
			# uuuuugly... but this way we make sure device requests don't step on each other's toes too much
			del request.headers['Host']
			request.headers['Host'] = conn.host

			# yeah, let's not leave these around
			del request.headers['X-Forwarded-For']
			del request.headers['X-Forwarded-Host']
			del request.headers['X-Forwarded-Server']

			# we check the connection state because otherwise we might mess up another request in process
			if conn.sock:
				if conn._HTTPConnection__state != _CS_IDLE:
					raise Exception("acquired connection but it's not idle!", upstream_host, str(device))
				if request.started_at - conn.last_call > _IDLE: # avoid socket timeouts
					conn.close()

			# finally, actually call upstream
			response = self._call_upstream(conn, request)
			response = wrap_response(response)

		http_debug("got response %s", response)
		return response

	call = call_upstream
