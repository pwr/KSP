package ksp.sys;

import ksp.Log;

import java.util.Properties;

public class ConfigImpl implements Configuration {
	private final Log LOG = new Log(ConfigImpl.class);

	private static final String[] IMPLEMENTATIONS = {"ksp.sys.Config410"};

	private final Configuration implementation;

	public ConfigImpl() {
		Configuration found = null;
		for (int i = 0; i < IMPLEMENTATIONS.length && found == null; i++) {
			try {
				Class c = Class.forName(IMPLEMENTATIONS[i]);
				found = (Configuration) c.newInstance();
			} catch (Exception ex) {
				LOG.w("failed to load configuration implementation " + IMPLEMENTATIONS[i], ex);
			}
		}

		implementation = found;
		if (implementation == null) {
			LOG.e("failed to load any configuration implementation, the kindlet will not work", null);
		}
	}

	public boolean loadInto(Properties _p) {
		LOG.i("loading system configuration");
		return implementation != null && implementation.loadInto(_p);
	}

	public boolean save(Properties _p) {
		LOG.i("updating system configuration");
		return implementation != null && implementation.save(_p);
	}

	public boolean sync() {
		return implementation != null && implementation.sync();
	}
}
