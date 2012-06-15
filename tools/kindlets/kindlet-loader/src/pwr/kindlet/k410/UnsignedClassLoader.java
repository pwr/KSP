package pwr.kindlet.k410;

import com.amazon.kindle.kindlet.internal.KindletExecutionException;
import com.amazon.kindle.kindlet.internal.KindletLoadException;
import sun.security.util.SecurityConstants;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.security.CodeSource;
import java.security.PermissionCollection;
import java.security.cert.Certificate;
import java.util.Iterator;
import java.util.Map;
import java.util.jar.JarFile;

public class UnsignedClassLoader extends com.amazon.kindle.kindlet.internal.security.m {
	public UnsignedClassLoader(URL[] _urls, com.amazon.kindle.kindlet.internal.security.h _certManager,
							   com.amazon.kindle.kindlet.internal.install.p _app) throws IOException, KindletLoadException, KindletExecutionException, ClassNotFoundException {
		super(_urls, UnsignedClassLoader.class.getClassLoader(), WHITELIST_ALLOW, null, null, _certManager, verifyMetadata(_app));
		this.a = false; // skip checking class signatures
	}

	protected JarFile StA(File _file, String _devicePid) throws IOException {
		//System.out.println("UnsignedClassLoader.StA " + _file + " pid " + _devicePid);
		return new JarFile(_file);
	}

	protected Certificate[] WSA(Certificate[] _certificates, Map _developerCertificates, Map _features) {
		//System.out.println("UnsignedClassLoader.WSA " + _features);
		Certificate[] result = new Certificate[_features.size()];
		int index = 0;
		for (Iterator itr = _features.values().iterator(); itr.hasNext(); ) {
			Object o = itr.next();
			com.amazon.kindle.kindlet.internal.security.i kcert = (com.amazon.kindle.kindlet.internal.security.i) o;
			result[index] = kcert.GUA();
			index++;
		}
		return result;
	}

	protected PermissionCollection getPermissions(CodeSource _cs) {
		//System.out.println("checking permissions for " + _cs);
		PermissionCollection pc = super.getPermissions(_cs);
		pc.add(SecurityConstants.ALL_PERMISSION);
		return pc;
	}

	// check certificates validity
	protected void EtA(java.util.Collection a) {
		//System.out.println("UnsignedClassLoader.EtA checking certificates in " + a);
	}

	//
	//
	//

	private static com.amazon.kindle.kindlet.internal.install.p verifyMetadata(com.amazon.kindle.kindlet.internal.install.p _app) {
		if (_app.getId() == null || _app.getId().length() == 0) {
			String fname = _app.we().getName().toLowerCase();
			if (fname.endsWith(".azw2")) {
				fname = fname.substring(0, fname.length() - 5);
			}
			_app.hzA(fname);
		}

		return _app;
	}

	// allow access to all classes
	private static final com.amazon.kindle.kindlet.internal.security.a.h WHITELIST_ALLOW = new com.amazon.kindle.kindlet.internal.security.a.h() {
		public boolean OE(String _action) {
			return true;
		}
	};
}
