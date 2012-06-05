package pwr.ksp.ui;

import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.res.Resources;
import pwr.ksp.KSPConfig;
import pwr.ksp.R;

public class Dialogs {
	public static final int EDIT_URL = 30;

	public static final int ROOT_FAILED = -1;
	public static final int LOAD_FAILED = -10;

	private static final DialogInterface.OnClickListener DISMISS = new DialogInterface.OnClickListener() {
		@Override
		public void onClick(DialogInterface dialogInterface, int i) {
			dialogInterface.dismiss();
		}
	};

	public static void error(Context _context, String _message) {
		AlertDialog.Builder adb = new AlertDialog.Builder(_context);
		_alert(adb, Resources.getSystem().getString(android.R.string.dialog_alert_title), _message);
		adb.setNegativeButton(android.R.string.ok, DISMISS);
		adb.create().show();
	}

	private static void _alert(AlertDialog.Builder _ab, String _title, String _message) {
		_ab.setTitle(_title);
		_ab.setCancelable(true);
		if (_message != null) {
			_ab.setMessage(_message);
		}
	}

	public static Dialog create(int _key, final KSPConfig _ksp) {
		if (_key == EDIT_URL) {
			return new EditUrl(_ksp);
		}

		AlertDialog.Builder ab = new AlertDialog.Builder(_ksp);
		switch (_key) {
			case ROOT_FAILED: {
				_alert(ab, _ksp.getString(R.string.root_command_failed), _ksp.getString(R.string.root_command_failed_message));
				ab.setNeutralButton(_ksp.getString(R.string.quit_button), new DialogInterface.OnClickListener() {
					@Override
					public void onClick(DialogInterface dialogInterface, int i) {
						_ksp.finish();
					}
				});
			}
			break;
			case LOAD_FAILED: {
				_alert(ab, "Error", "Failed to load configuration from the Kindle application. Do you have the Kindle for Android application installed?");
				ab.setNeutralButton(_ksp.getString(R.string.quit_button), new DialogInterface.OnClickListener() {
					@Override
					public void onClick(DialogInterface dialogInterface, int i) {
						_ksp.finish();
					}
				});
			}
			break;
		}
		return ab.create();
	}
}
