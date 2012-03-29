import os, os.path, tempfile
import logging, ssl, hashlib
from OpenSSL import crypto

import config


def load_p12bytes(name):
	path = os.path.join(config.database_path, name + '.p12')
	if not os.path.isfile(path):
		logging.warn("file not found: %s", path)
		return None

	try:
		f = open(path, 'rb')
		bytes = f.read()
		f.close()
		os.remove(path)
		return bytes
	except:
		logging.exception("failed to read %s", path)
	return None

def load_pkcs12(name, pkcs12_bytes):
	if not pkcs12_bytes:
		return None
	try:
		pkcs12 = crypto.load_pkcs12(pkcs12_bytes, 'pass') # funny, eh?
		logging.debug("loaded PKCS12 for %s", name)
	except:
		logging.exception("failed to load PKCS12 for %s from %d bytes", name, len(pkcs12_bytes))
		return None

	pkcs_name = str(pkcs12.get_friendlyname(), 'utf-8')
	p_number, p_foo1, p_serial, p_fiona, p_digest = pkcs_name.split(',')
	if p_serial != name:
		logging.warn("certificate is not for this device? mismatched friendly name %s", pkcs_name)
		return None

	return pkcs12

def make_context(name, pkcs12_bytes):
	pkcs12 = load_pkcs12(name, pkcs12_bytes)
	if not pkcs12:
		return None

	temp_prefix = hashlib.md5(pkcs12_bytes).hexdigest()
	temp = tempfile.mkstemp(prefix = temp_prefix)
	tempname = temp[1]

	# we need to dump the PKCS12 to a PEM file for SSLContext to read it
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
		logging.debug("created SSL context for %s", name)
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
