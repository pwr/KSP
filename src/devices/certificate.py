import sys, os, os.path, tempfile
import logging, ssl, hashlib

import config


def _load_pkcs12_crypto(name, pkcs12_bytes):
	if not pkcs12_bytes: return None
	try:
		pkcs12 = crypto.load_pkcs12(pkcs12_bytes, 'pass') # funny, eh?
		logging.debug("loaded PKCS12 for %s", name)
	except:
		logging.exception("failed to load PKCS12 for %s from %d bytes", name, len(pkcs12_bytes))
		return None

	pkcs_name = str(pkcs12.get_friendlyname(), 'utf-8')
	p_number, _, p_serial, p_fiona, p_digest = pkcs_name.split(',')[:5]
	if p_serial[:16] == name:
		return pkcs12

	logging.warn("certificate is not for this device? mismatched friendly name %s", pkcs_name)

def _dump_pkcs12_crypto(pkcs12, out_file):
	with os.fdopen(out_file, 'wb') as tempf:
		pkey = pkcs12.get_privatekey()
		pkey_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey)
		tempf.write(pkey_pem)

		for cert in ( pkcs12.get_certificate(), ) + pkcs12.get_ca_certificates():
			if cert:
				cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
				tempf.write(cert_pem)

def _dump_pkcs12_openssl(pkcs12, out_file):
	with subprocess.Popen(['openssl', 'pkcs12', '-nodes', '-passin', 'pass:pass'],
			stdin = subprocess.PIPE, stdout = out_file, stderr = sys.stderr) as pop:
		pop.stdin.write(pkcs12)
		pop.stdin.close()
		pop.wait()
	try: os.close(out_file)
	except: pass


try:
	from OpenSSL import crypto
	load_pkcs12 = _load_pkcs12_crypto
	dump_pkcs12 = _dump_pkcs12_crypto
except ImportError:
	logging.critical("failed to import pyOpenSSL, falling back to openssl command line for PKCS12 handling")
	import subprocess
	load_pkcs12 = lambda name, pkcs12_bytes: pkcs12_bytes
	dump_pkcs12 = _dump_pkcs12_openssl


def load_p12bytes(name):
	path = os.path.join(config.database_path, name + '.p12')
	if not os.path.isfile(path):
		logging.warn("file not found: %s", path)
		return None
	try:
		with open(path, 'rb') as f:
			bytes = f.read()
	except:
		logging.exception("failed to read %s", path)
		return None
	os.remove(path)
	return bytes

def make_context(name, pkcs12_bytes):
	pkcs12 = load_pkcs12(name, pkcs12_bytes)
	if not pkcs12: return None

	temp_prefix = hashlib.md5(pkcs12_bytes).hexdigest()
	temp = tempfile.mkstemp(prefix = temp_prefix)
	# we need to dump the PKCS12 to a PEM file for SSLContext to read it
	dump_pkcs12(pkcs12, temp[0])

	try:
		ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
		ctx.verify_mode = ssl.CERT_NONE # the cert check does not pass
		ctx.load_cert_chain(temp[1])
		logging.debug("created SSL context for %s", name)
		return ctx
	except:
		logging.exception("failed to create SSL context for %s", name)
	finally:
		try: os.remove(temp[1])
		except: pass

DEFAULT_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLSv1)


logging.debug("certificates for new devices will be searched in %s", config.database_path)
