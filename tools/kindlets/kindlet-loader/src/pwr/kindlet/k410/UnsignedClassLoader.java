/**
 * Copyright (c) 2012, Daniel Pavel (pwr)
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * The views and conclusions contained in the software and documentation are those
 * of the authors and should not be interpreted as representing official policies,
 * either expressed or implied, of the FreeBSD Project.
 */

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
