package com.amazon.kindle.kindlet.internal;

import pwr.kindlet.k410.UnsignedClassLoader;
import pwr.kindlet.Whitelist;

import java.io.IOException;
import java.net.URL;
import java.security.PermissionCollection;

public class hb extends kb {
	public hb(com.amazon.kindle.kindlet.internal.install.p _app, PermissionCollection _permissions, com.amazon.ebook.framework.service.h _storage,
			  String _devicePid, com.amazon.kindle.kindlet.internal.security.h _certManager) throws KindletLoadException, KindletExecutionException {
		super(_app, _permissions, _storage, _devicePid, _certManager);
	}

	protected com.amazon.kindle.kindlet.internal.security.m BzA(URL[] _urls, PermissionCollection _permissions, String _devicePid,
																com.amazon.kindle.kindlet.internal.security.h _certManager,
																com.amazon.kindle.kindlet.internal.install.p _app) throws KindletLoadException, KindletExecutionException, IOException, ClassNotFoundException {
		if (Whitelist.allows(_app)) {
			System.out.println("allowing unrestricted access for whitelisted Kindlet " + _app.getId() + " from " + _app.we());
			return new UnsignedClassLoader(_urls, _certManager, _app);
		}

		return new com.amazon.kindle.kindlet.internal.security.s(_urls, getClass().getClassLoader(), nyA(), _permissions, _devicePid, _certManager, _app);
	}
}
