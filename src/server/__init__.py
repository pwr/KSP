import logging, os.path, re

import config


if config.server_certificate:
	if not os.path.isfile(config.server_certificate):
		raise Exception("server certificate not found at", config.server_certificate)
	# TODO check that the file actually contains a propert key and certificate chain
else:
	config.server_certificate = None

# need to process the configuration before importing the handlers,
# because many of them depend on these values
if not config.server_url or '<your_ssl_server>' in config.server_url:
	raise Exception("config.server_url must be set")
__server_url = config.server_url
if __server_url[-1] != '/':
	__server_url += '/'
if '://' not in __server_url:
	__server_url = ('https://' if config.server_certificate else 'http://') + __server_url

from urllib.parse import urlparse
__protocol, __host_and_port, __path, _, _, _ = urlparse(__server_url)
config.server_path_prefix = __path
__server_url_without_protocol = __host_and_port + __path
config.server_hostname, _, _ = __host_and_port.partition(':')

__disable_procotol_matching = hasattr(config, 'disable_protocol_matching') and config.disable_protocol_matching
if __disable_procotol_matching:
	logging.warn("disabling protocol matching")
	__server_url_log = __server_url
else:
	__server_url_log = ('http(s)://' if config.server_certificate else 'http://') + __server_url_without_protocol

logging.info("server url [%s]", __server_url_log )

__amazon_hosts = "https://([-a-z7]*).amazon.com/"
logging.info("rewrite rule: %s => %s", __amazon_hosts, __server_url_log)
__amazon_hosts_re = re.compile(__amazon_hosts)
del __amazon_hosts

if config.server_certificate and not __disable_procotol_matching:
	config.server_url = lambda request: ('https://' if request.is_secure() else 'http://') + __server_url_without_protocol
	config.rewrite_rules = lambda request: { __amazon_hosts_re : config.server_url(request) }
else:
	config.server_url = lambda request: __server_url
	config.rewrite_rules = lambda request: { __amazon_hosts_re : __server_url }

del __protocol, __host_and_port, __path, __server_url_log


_loggers = {}
def logger(name, formatted = True, level = logging.NOTSET):
	log = _loggers.get(name)
	if not log:
		log = logging.getLogger(name)
		log.setLevel(level)
		_loggers[name] = log

		if config.logs_path:
			filename =	os.path.join(config.logs_path, name + '.log')
			handler = logging.FileHandler(filename, 'a')
			formatter = None
			if formatted:
				for h in logging.getLogger().handlers:
					if h.formatter:
						formatter = h.formatter
						break
			handler.setFormatter(formatter)
			log.addHandler(handler)
	return log


from server.http import Server as HTTP
