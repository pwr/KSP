import sun.security.x509.X509CertImpl;

import java.io.File;
import java.io.FileInputStream;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.security.cert.X509Certificate;
import java.util.Map;

public class CmdImport extends Cmd {
	public CmdImport() {
		super("-importcert", new String[]{"-alias", "-file"});
	}

	public void run(File keystore, Map args) throws Exception {
		KeyStore ks = load(keystore);

		String alias = (String) args.get("-alias");
		String keyfile = (String) args.get("-file");
		if (alias.length() < 1) {
			throw new IllegalArgumentException("no alias given");
		}

		Certificate c = ks.getCertificate(alias);
		if (c != null) {
			System.out.print("alias already in keystore: ");
			print(c);
			return;
		}

		FileInputStream fis = new FileInputStream(keyfile);
		X509Certificate cert = new X509CertImpl(fis);
		fis.close();

		System.out.print("imported '" + alias + "' ");
		print(cert);

		ks.setCertificateEntry(alias, cert);
		store(ks, keystore);
	}
}
