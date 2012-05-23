package pwr.ksp;

import android.app.AlertDialog;
import android.app.Dialog;
import android.content.DialogInterface;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

public class Dialogs {
	public static final int RELOAD_CONFIG = 5;
	public static final int SHOW_CONFIG = 10;
	public static final int CLEAR_CONFIG = 15;
	public static final int APPLY_CONFIG = 20;
	public static final int EDIT_URL = 30;

	public static final int ROOT_FAILED = -1;
	public static final int LOAD_FAILED = -10;
	public static final int SAVE_FAILED = -20;

	public static final DialogInterface.OnClickListener DISMISS = new DialogInterface.OnClickListener() {
		@Override
		public void onClick(DialogInterface dialogInterface, int i) {
			dialogInterface.dismiss();
		}
	};

	static AlertDialog.Builder alert(AlertDialog.Builder _ab, String _title, String _message) {
		return alert(_ab, _title, _message, null);
	}

	static AlertDialog.Builder alert(AlertDialog.Builder _ab, String _title, String _message, String _cancel) {
		_ab.setTitle(_title);
		if (_message != null) {
			_ab.setMessage(_message);
		}
		if (_cancel != null) {
			_ab.setCancelable(true);
			_ab.setNegativeButton(_cancel, DISMISS);
		} else {
			_ab.setCancelable(false);
		}
		return _ab;
	}

	public static Dialog create(int _key, final KSPConfig _ksp) {
		if (_key == EDIT_URL) {
			return create_edit_url_dialog(_ksp);
		}

		AlertDialog.Builder ab = new AlertDialog.Builder(_ksp);
		switch (_key) {
			case ROOT_FAILED: {
				alert(ab, "Root command failed", "Failed to execute root command. Your Android device must be root-enabled for KSPConfig to work.");
				ab.setNeutralButton("Quit KSPConfig", new DialogInterface.OnClickListener() {
					@Override
					public void onClick(DialogInterface dialogInterface, int i) {
						_ksp.finish();
					}
				});
			}
			break;
			case LOAD_FAILED: {
				alert(ab, "Error", "Failed to load configuration from the Kindle application. " +
						"Do you have the Kindle for Android application installed?");
				ab.setNeutralButton("Quit KSPConfig", new DialogInterface.OnClickListener() {
					@Override
					public void onClick(DialogInterface dialogInterface, int i) {
						_ksp.finish();
					}
				});
			}
			break;
			case SAVE_FAILED: {
				alert(ab, "Save failed", "Failed to save the new configuration into the temporary file.", "Close");
			}
			break;
			case RELOAD_CONFIG:
				alert(ab, "Reload configuration", "Discard the currently loaded configuration and re-load it from the Kindle's application files?", "Cancel");
				ab.setPositiveButton("Reload", new DialogInterface.OnClickListener() {
					@Override
					public void onClick(DialogInterface dialogInterface, int i) {
						dialogInterface.dismiss();
						Configuration.clear();
						_ksp.reloadConfig();
					}
				});
				break;
			case SHOW_CONFIG: {
				Configuration showConfig = Configuration.get();
				alert(ab, "Loaded configuration", showConfig.toString(), "OK");
			}
			break;
			case CLEAR_CONFIG: {
				alert(ab, "Reset configuration?", "Clear all custom URLs from Kindle for Android's configuration, and revert to the defaults?", "Cancel");
				ab.setPositiveButton("Reset", new DialogInterface.OnClickListener() {
					@Override
					public void onClick(DialogInterface dialogInterface, int i) {
						_ksp.clearConfiguration();
					}
				});
			}
			break;
			case APPLY_CONFIG: {
				final Configuration applyConfig = Configuration.get();
				alert(ab, "Apply this configuration?", applyConfig.toString(), "Cancel");
				ab.setPositiveButton("Apply and Quit", new DialogInterface.OnClickListener() {
					@Override
					public void onClick(DialogInterface dialogInterface, int i) {
						_ksp.applyConfiguration(applyConfig);
					}
				});
			}
			break;
		}
		return ab.create();
	}

	private static Dialog create_edit_url_dialog(final KSPConfig _ksp) {
		final Dialog d = new Dialog(_ksp);
		d.setContentView(R.layout.edit_url);
		d.setTitle("Enter the new base URL:");

		final EditText editUrl = (EditText) d.findViewById(R.id.edit_url);

		d.setOnShowListener(new DialogInterface.OnShowListener() {
			@Override
			public void onShow(DialogInterface dialogInterface) {
				final Configuration c = Configuration.get();
				final String urlTodo = c.getBaseURL();
				if (urlTodo != null) {
					editUrl.setText(urlTodo);
				}
			}
		});

		final Button cancel = (Button) d.findViewById(R.id.cancel_edit_url);
		cancel.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				d.cancel();
			}
		});
		d.setOnCancelListener(new DialogInterface.OnCancelListener() {
			@Override
			public void onCancel(DialogInterface dialogInterface) {
				dialogInterface.dismiss();
			}
		});

		final Ping.OnFinished ping_finished = new Ping.OnFinished() {
			@Override
			public void finished(String _status) {
				if (_status == null) {
					d.dismiss();
					final Configuration c = Configuration.get();
					final String newUrl = editUrl.getText().toString();
					c.setBaseURL(newUrl);
					_ksp.updateNewConfigurationStatus(c);
				} else {
					alert(new AlertDialog.Builder(_ksp), "Error", _status, "Close").create().show();
				}
			}
		};

		final Button test = (Button) d.findViewById(R.id.test_new_url);
		test.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				final String newUrl = editUrl.getText().toString();
				new Ping(_ksp, ping_finished).execute(newUrl);
			}
		});

		return d;
	}
}
