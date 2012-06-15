package ksp;

import ksp.sys.ConfigImpl;
import ksp.sys.Configuration;

import java.util.Enumeration;
import java.util.Properties;

class ServiceConfig {
	static final String FIONA_TODO_LIST_PROXY = "/FionaTodoListProxy";

	private final Log LOG = new Log(ServiceConfig.class);
	private final Properties props = new Properties();

	private final ConfigImpl sys = new ConfigImpl();

	boolean load() {
		props.clear();
		return sys.loadInto(props);
	}

	boolean save() {
		return sys.save(props);
	}

	boolean triggerSync() {
		return sys.sync();
	}

	String getServiceUrl() {
		String url = props.getProperty(Configuration.KEY_URL_TODO);
		LOG.i("url.todo = [" + url + "]");

		if (url == null) {
			return null;
		}
		if (url.trim().length() == 0) {
			return null;
		}
		if (url.indexOf("-g7g.amazon.com/") > 0) {
			return null;
		}

		if (url.endsWith(FIONA_TODO_LIST_PROXY)) {
			url = url.substring(0, url.length() - FIONA_TODO_LIST_PROXY.length());
		}
		return url;
	}

	void setSCFG(Properties _scfg) {
		for (int i = 0; i < Configuration.ALL_KEYS.length; i++) {
			props.remove(Configuration.ALL_KEYS[i]);
		}

		if (_scfg != null) {
			for (Enumeration e = _scfg.keys(); e.hasMoreElements(); ) {
				String key = (String)e.nextElement();
				props.setProperty(key, _scfg.getProperty(key));

			}
		}
	}
}
