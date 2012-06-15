package ksp;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Properties;

class Actions {
	private final Log LOG = new Log(Actions.class);

	private final KSPKindlet ksp;
	private final ServiceConfig conf;

	final Runnable reloadAction = new Runnable() {
		public void run() {
			LOG.i("load configuration");
			if (conf.load()) {
				ksp.ui.configurationLoaded(conf);
			} else {
				ksp.ui.alert(UI.CONFIG_LOAD_FAILED);
			}
		}
	};

	final ActionListener applyAction = new ActionListener() {
		public void actionPerformed(ActionEvent e) {
			LOG.i("save configuration");
			if (conf.save()) {
				conf.triggerSync();
				ksp.ui.alert(UI.CONFIG_SAVED);
				reloadAction.run();
			} else {
				ksp.ui.alert(UI.CONFIG_SAVE_FAILED);
			}
		}
	};

	final ActionListener editUrlAction = new ActionListener() {
		public void actionPerformed(ActionEvent e) {
			String url = conf.getServiceUrl();
			if (url == null) {
				url = "https://";
			}

			ksp.ui.openChangeUrlPanel(url);
		}
	};

	final ActionListener useDefaults = new ActionListener() {
		public void actionPerformed(ActionEvent e) {
			conf.setSCFG(null);
			ksp.ui.newConfiguration(conf);
		}
	};

	Actions(KSPKindlet _ksp, ServiceConfig _conf) {
		ksp = _ksp;
		conf = _conf;
	}

	void checkAndChangeUrl(final String _url) {
		if (_url != null) {
			ksp.ping(_url);
		}
	}

	void changeUrl(Properties _scfg) {
		conf.setSCFG(_scfg);
		ksp.ui.newConfiguration(conf);
	}
}
