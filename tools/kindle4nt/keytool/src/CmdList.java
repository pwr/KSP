import java.io.File;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.util.Enumeration;
import java.util.Map;

public class CmdList extends Cmd {
	public CmdList() {
		super("-list", new String[]{});
	}

	public void run(File keystore, Map args) throws Exception {
		KeyStore ks = load(keystore);
		for (Enumeration e = ks.aliases(); e.hasMoreElements(); ) {
			String alias = (String) e.nextElement();
			Certificate cert = ks.getCertificate(alias);
			list(alias, cert);
		}
	}
}
