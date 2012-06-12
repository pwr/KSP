package pwr.ksp.ui;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.res.Resources;

public class Dialogs {
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
}
