import os, os.path, tempfile
import logging, ssl
from OpenSSL import crypto

import config


def load_p12(name):
	path = os.path.join(config.database_path, name + '.p12')
	if not os.path.isfile(path):
		logging.warn("certificate not found: %s", path)
		return None

	try:
		f = open(path, 'rb')
		bytes = f.read()
		f.close()
		os.remove(path)
		return bytes
	except:
		logging.exception("failed to read PKCS12 from %s", path)
	return None

def make_context(name, pkcs12_bytes):
	if not pkcs12_bytes:
		return None
	try:
		pkcs12 = crypto.load_pkcs12(pkcs12_bytes, 'pass') # funny, eh?
	except:
		logging.exception("failed to load PKCS12 %s from bytes", name)
		return None

	temp = tempfile.mkstemp(prefix = name)
	tempname = temp[1]

	with os.fdopen(temp[0], 'wb') as tempf:
		pkey = pkcs12.get_privatekey()
		pkey_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey)
		tempf.write(pkey_pem)

		for cert in ( pkcs12.get_certificate(), ) + pkcs12.get_ca_certificates():
			if cert:
				cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
				tempf.write(cert_pem)

	try:
		ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
		ctx.verify_mode = ssl.CERT_NONE # the cert check does not pass
		ctx.load_cert_chain(tempname)
		logging.info("created SSL context for %s", name)
		return ctx
	except:
		logging.exception("failed to create SSL context for %s", name)
	finally:
		try:
			os.remove(tempname)
		except:
			pass

	return None


logging.debug("certificates for new devices will be searched in %s", config.database_path)
