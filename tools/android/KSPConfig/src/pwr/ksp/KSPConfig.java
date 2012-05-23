package pwr.ksp;

import android.app.Activity;
import android.app.ActivityManager;
import android.app.Dialog;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

public class KSPConfig extends Activity {
	Button reloadButton;
	Button editURLButton;
	Button clearButton;
	Button applyConfigButton;

	TextView currentConfigStatus;
	TextView newConfigStatus;

	/**
	 * Called when the activity is first created.
	 */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
	}

	@Override
	protected void onStart() {
		super.onStart();

		reloadButton = (Button) findViewById(R.id.reload_config);
		reloadButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				reloadConfig();
			}
		});

		editURLButton = (Button) findViewById(R.id.change_base_url);
		editURLButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				showDialog(Dialogs.EDIT_URL);
			}
		});

		clearButton = (Button) findViewById(R.id.clear_config);
		clearButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				showDialog(Dialogs.CLEAR_CONFIG);
			}
		});

		applyConfigButton = (Button) findViewById(R.id.apply_config);
		applyConfigButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				showDialog(Dialogs.APPLY_CONFIG);
			}
		});

		currentConfigStatus = (TextView) findViewById(R.id.current_config);
		newConfigStatus = (TextView) findViewById(R.id.new_config);
	}

	@Override
	protected void onResume() {
		super.onResume();

		ActivityManager am = (ActivityManager) getSystemService(ACTIVITY_SERVICE);
		if (!RootExec.stopKindle(am)) {
			showDialog(Dialogs.ROOT_FAILED);
			return;
		}

		Configuration.KSP_DATA = getDir("temp", MODE_PRIVATE).getAbsolutePath();
		Configuration.getConfigurationFile().delete();
		Configuration.clear();
		reloadConfig();
	}

	public Dialog onCreateDialog(int _key) {
		return Dialogs.create(_key, this);
	}

	public void reloadConfig() {
		if (Configuration.get() != null) {
			showDialog(Dialogs.RELOAD_CONFIG);
			return;
		}

		editURLButton.setEnabled(false);
		clearButton.setEnabled(false);
		applyConfigButton.setEnabled(false);

		currentConfigStatus.setText("");
		newConfigStatus.setText("");

		if (RootExec.getConfig()) {
			Configuration config = Configuration.get(true);
			if (config == null) {
				showDialog(Dialogs.LOAD_FAILED);
			} else {
				configurationLoaded(config);
			}
		} else {
			showDialog(Dialogs.ROOT_FAILED);
		}
	}

	private void configurationLoaded(Configuration _c) {
		showDialog(Dialogs.SHOW_CONFIG);
		editURLButton.setEnabled(true);
		clearButton.setEnabled(_c.hasBaseURL());
		applyConfigButton.setEnabled(false);

		if (_c.hasBaseURL()) {
			currentConfigStatus.setText("Current base URL:\n" + _c.getBaseURL());
		} else {
			currentConfigStatus.setText("The Kindle for Android application is using the default URLs.");
		}
	}

	public void updateNewConfigurationStatus(Configuration _c) {
		if (_c.hasBaseURL()) {
			newConfigStatus.setText("New base URL:\n" + _c.getBaseURL());
			clearButton.setEnabled(true);
		} else {
			newConfigStatus.setText("The Kindle for Android application will revert to its default URLs.");
			clearButton.setEnabled(false);
		}

		applyConfigButton.setEnabled(true);
	}

	public void clearConfiguration() {
		Configuration c = Configuration.get();
		assert c != null : "null configuration";
		c.setBaseURL(null);
		updateNewConfigurationStatus(c);
	}

	public void applyConfiguration(Configuration _c) {
		if (!_c.save()) {
			showDialog(Dialogs.SAVE_FAILED);
		} else {
			if (RootExec.setConfig()) {
				finish();
			} else {
				showDialog(Dialogs.ROOT_FAILED);
			}
		}
	}
}
