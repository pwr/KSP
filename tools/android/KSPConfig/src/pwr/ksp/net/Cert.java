package pwr.ksp.net;

import android.util.Log;

import javax.net.ssl.SSLHandshakeException;
import java.security.cert.CertPath;
import java.security.cert.CertPathValidatorException;
import java.security.cert.Certificate;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;

public class Cert {
	public static final String INSTALL = "android.credentials.INSTALL";
	public static final int INSTALL_REQUEST = 3;

	// if this is a certificate exception, extract the certificate, save it and return the File object
	// otherwise return null, can't handle the exception
	static byte[] handle(SSLHandshakeException _ex) {
		if (_ex.getCause() == null || _ex.getCause().getClass() != CertificateException.class) {
			return null;
		}

		CertificateException cex = (CertificateException) _ex.getCause();
		if (cex.getCause() == null || cex.getCause().getClass() != CertPathValidatorException.class) {
			return null;
		}

		CertPathValidatorException cpex = (CertPathValidatorException) cex.getCause();
		return getCAcertificate(cpex.getCertPath());
	}

	private static byte[] getCAcertificate(CertPath _cpath) {
		if (_cpath == null) {
			return null;
		}

		byte[] certBytes = null;
		for (Certificate c : _cpath.getCertificates()) {
			certBytes = getCAcertBytes(c);
		}

		return certBytes;
	}

	private static byte[] getCAcertBytes(Certificate _c) {
		if (!(_c instanceof X509Certificate)) {
			Log.w("CERT", _c.getType() + " : " + _c.getClass().getName());
			return null;
		}
		X509Certificate xc = (X509Certificate) _c;
		Log.i("CERT", xc.getSerialNumber().toString() + " issued by " + xc.getIssuerDN().getName() + " for " + xc.getSubjectDN().getName());
		if (xc.getBasicConstraints() < 0) { // not a CA cert
			return null;
		}
		Log.d("CERT", "appears to be a CA cert: " + xc.toString());
		try {
			return xc.getEncoded();
		} catch (Exception ex) {
			Log.e("CERT", "failed to get CA certificate in encoded form", ex);
		}
		return null;
	}

	static final class Ex extends Exception {
		final byte[] der;

		Ex(byte[] _cert) {
			der = _cert;
		}
	}
}
