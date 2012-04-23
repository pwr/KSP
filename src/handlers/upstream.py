import logging, socket
from http.client import HTTPSConnection, HTTPException, _CS_IDLE
from threading import RLock

from handlers.dummy import Dummy
from wrappers import wrap_response


class Upstream (Dummy):
	"""
	simple pass-through handler
	"""
	def __init__(self, service, path, command = None, idle = 57):
		Dummy.__init__(self, service, path, command)
		# the default http keep-alive set-up on kindle is 60 seconds
		self.connection_idle = idle

	def _call_upstream(self, conn, request, first_attempt = True):
		try:
			logging.debug("calling upstream %s", request)
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

	def call_upstream(self, request, device):
		"""proxy a request to the originally intended server, returns a http response"""
		if device.is_provisional(): # not yet allowed access upstream
			return None

		conn = device.connections.get(self.service)
		if not conn:
			# it's very unlikely a device will shoot two requests to the same service at the same time, just after KSP started
			# so we should be reasonable safe creating the connection without locking
			conn = HTTPSConnection(self.service + '.amazon.com', context = device.context)
			conn.last_call = 0
			conn._lock = RLock()
			logging.info("created upstream connection to service %s for %s", self.service, device)
			conn = device.connections.setdefault(self.service, conn) # just in case...
		with conn._lock:
			# uuuuugly... but this way we make sure device requests don't step on each other's toes too much
			del request.headers['Host']
			request.headers['Host'] = self.service + '.amazon.com'

			# yeah, let's not leave these around
			del request.headers['X-Forwarded-For']
			del request.headers['X-Forwarded-Host']
			del request.headers['X-Forwarded-Server']

			# we check the connection state because otherwise we might mess up another request in process
			if conn.sock:
				if conn._HTTPConnection__state != _CS_IDLE:
					raise Exception("acquired connection but it's not idle!", self.service, device)
				if request.started_at - conn.last_call > self.connection_idle: # avoid socket timeouts
					conn.close()

			# finally, actually call upstream
			response = self._call_upstream(conn, request)
			response = wrap_response(response)

		logging.debug("got response %s", response)
		return response

	call = call_upstream
