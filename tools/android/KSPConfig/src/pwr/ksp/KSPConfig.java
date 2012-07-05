package pwr.ksp;

import android.app.Activity;
import android.app.Dialog;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import pwr.ksp.net.Cert;
import pwr.ksp.net.Ping;
import pwr.ksp.net.PingResultHandler;
import pwr.ksp.ui.Dialogs;

public class KSPConfig extends Activity {
	public KSPUI ui;
	private Configuration config;
	private boolean doReloadConfiguration = true;
	public String installing_certificate_for;

	/**
	 * Called when the activity is first created.
	 */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		setContentView(R.layout.main);
		ui = new KSPUI(this);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		MenuInflater mi = getMenuInflater();
		mi.inflate(R.menu.main_menu, menu);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		if (item.getItemId() == R.id.reload_configuration) {
			reloadConfig();
			return true;
		}
		return false;
	}

	@Override
	protected void onResume() {
		super.onResume();
		if (doReloadConfiguration) {
			reloadConfig();
		}
		doReloadConfiguration = true;
	}

	@Override
	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		doReloadConfiguration = false;
		super.onActivityResult(requestCode, resultCode, data);
		Log.d("KSP", "req " + requestCode + " res " + resultCode + " url " + installing_certificate_for);
		if (requestCode == Cert.INSTALL_REQUEST) {
			if (resultCode == RESULT_OK) {
				String url = installing_certificate_for;
				installing_certificate_for = null;
				ping(url);
			} else {
				Dialogs.error(this, getString(R.string.install_certificate_failed));
			}
			return;
		}

		Log.w("KSP", "Don't know how to handle activity result");
	}

	public void ping(String _url) {
		Ping p = new Ping(this, new PingResultHandler(this));
		p.execute(_url);
	}

	public Configuration getConfig() {
		return config;
	}

	void reloadConfig() {
		ui.reset();
		config = new Configuration(this);

		switch (K4A.getConfig(config.localConfiguration)) {
			case RootExec.OK:
				if (!config.load()) {
					ui.fatal(R.string.load_configuration_failed, true);
				} else {
					ui.configurationLoaded(config.getServiceURL());
				}
				break;
			case RootExec.NO_CONFIG:
				ui.fatal(R.string.load_configuration_failed, true);
				break;
			case RootExec.NO_ROOT:
				ui.fatal(R.string.root_command_failed, true);
				break;
			default:
				ui.fatal(R.string.unknown_error, true);
		}
	}

	public void clearConfiguration() {
		config.setServiceURL(null);
		ui.configurationChanged(null);
	}

	public void applyConfiguration() {
		if (!K4A.stop(this)) {
			ui.fatal(R.string.kill_failed, false);
			return;
		}

		if (config.save()) {
			switch (K4A.setConfig(config.localConfiguration)) {
				case RootExec.OK:
					ui.reset();
					K4A.start(this);
					break;
				default:
					ui.fatal(R.string.root_command_failed, false);
					break;
			}
		} else {
			ui.fatal(R.string.save_failed, false);
		}
	}
}
