import java.io.File;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.util.Map;

public class CmdText extends Cmd {
	public CmdText() {
		super("-text", new String[]{"-alias"});
	}

	void run(File keystore, Map args) throws Exception {
		KeyStore ks = load(keystore);
		String alias = (String) args.get("-alias");
		Certificate cert = ks.getCertificate(alias);
		if (cert == null) {
			throw new IllegalArgumentException("alias not found");
		}
		print(cert);
	}
}
