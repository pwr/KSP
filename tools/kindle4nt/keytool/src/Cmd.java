import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.security.cert.X509Certificate;
import java.util.Map;

public abstract class Cmd {
	public static final char[] PW = "changeit".toCharArray();

	public final String name;
	public final String[] requiredArgs;

	protected Cmd(String _name, String[] _requiredArgs) {
		name = _name;
		requiredArgs = _requiredArgs;
	}

	public KeyStore load(File f) throws Exception {
		System.out.println("loading keystore from " + f);
		KeyStore ks = KeyStore.getInstance(KeyStore.getDefaultType());
		FileInputStream fis = new FileInputStream(f);
		ks.load(fis, PW);
		fis.close();
		return ks;
	}

	public void store(KeyStore ks, File f) throws Exception {
		System.out.println("wrinting keystore " + ks + " to " + f);
		FileOutputStream fos = new FileOutputStream(f);
		ks.store(fos, PW);
		fos.close();
	}

	public void list(String alias, Certificate cert) {
		if (cert instanceof X509Certificate) {
			X509Certificate x509 = (X509Certificate) cert;
			System.out.println(" " + alias + " (" + x509.getType() + ")\n" +
					"  valid from " + x509.getNotBefore() + " to " + x509.getNotAfter() + "\n" +
					"  for        " + x509.getSubjectDN().getName() + "\n" +
					"  issued by  " + x509.getIssuerDN().getName());
		} else {
			System.out.println(" " + alias + " (" + cert.getType() + ")");
		}
	}

	public void print(Certificate c) {
		System.out.println(c.getType() + " " + c);
	}

	abstract void run(File keystore, Map args) throws Exception;
}
