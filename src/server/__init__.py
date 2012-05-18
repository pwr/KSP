import logging, os.path, re

import config


# need to process the configuration before importing the handlers,
# because many of them depend on these values
if not config.server_url:
	raise Exception("config.server_url must be set")
if config.server_url[-1] != '/':
	config.server_url += '/'

from urllib.parse import urlparse
__protocol, __host_and_port, __path, _, _, _ = urlparse(config.server_url)
config.server_path_prefix = __path
logging.info("server url [%s://%s%s]", __protocol, __host_and_port, __path )

config.server_hostname, _, _ = __host_and_port.partition(':')

__rewrite_rules = { "https://([-a-z7]*).amazon.com/" : config.server_url }
logging.info("rewrite rules: %s", __rewrite_rules)
config.rewrite_rules = { re.compile(k) : v for k, v in __rewrite_rules.items()  }

if config.server_certificate:
	if not os.path.isfile(config.server_certificate):
		raise Exception("server certificate not found at", config.server_certificate)
else:
	config.server_certificate = None


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
