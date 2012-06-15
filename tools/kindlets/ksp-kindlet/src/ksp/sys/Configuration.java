package ksp.sys;

import java.util.Properties;

public interface Configuration {
	final String KEY_URL_TODO = "url.todo";
	final String KEY_URL_CDE = "url.cde";
	final String KEY_COOKIE_STORE_DOMAINS = "cookie.store.domains";

	final String KEY_URL_FIRS = "url.firs";
	final String KEY_URL_FIRS_UNAUTH = "url.firs.unauth";
	final String KEY_URL_DET = "url.det";
	final String KEY_URL_DET_UNAUTH = "url.det.unauth";
	final String KEY_URL_MESSAGING_POST = "url.messaging.post";

	final String[] ALL_KEYS = { //
											   KEY_URL_TODO, KEY_URL_CDE, //
											   KEY_COOKIE_STORE_DOMAINS, //
											   KEY_URL_FIRS, KEY_URL_FIRS_UNAUTH,  //
											   KEY_URL_DET, KEY_URL_DET_UNAUTH, //
											   KEY_URL_MESSAGING_POST //
	};



	boolean loadInto(Properties _p);
	boolean save(Properties _p);
	boolean sync();
}
