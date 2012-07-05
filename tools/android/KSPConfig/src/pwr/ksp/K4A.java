package pwr.ksp;

import android.app.Activity;
import android.app.ActivityManager;
import android.app.ProgressDialog;
import android.os.AsyncTask;
import android.util.Log;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

class K4A {
	private static final String DATA_PATH = "/data/data/com.amazon.kindle";
	private static final File CONFIGURATION_FILE = new File(new File(DATA_PATH, "shared_prefs"), Configuration.FILE_NAME);
	private static final File METADATA_CACHE = new File(new File(DATA_PATH, "files"), "KindleSyncMetadataCache.xml");
	private static final File KINDLE_CONTENT = new File(new File(DATA_PATH, "databases"), "kindle_content.db");
	private static final File KINDLE_LIBRARY = new File(new File(DATA_PATH, "databases"), "kindle_library.db");

	static boolean isRunning(Activity _activity) {
		ActivityManager am = (ActivityManager) _activity.getSystemService(Activity.ACTIVITY_SERVICE);
		List<ActivityManager.RunningAppProcessInfo> apps = am.getRunningAppProcesses();
		if (apps != null) {
			for (ActivityManager.RunningAppProcessInfo pi : apps) {
				if (pi.processName.equals("com.amazon.kindle")) {
					return true;
				}
			}
		}
		return false;
	}

	static boolean stop(Activity _activity) {
		ActivityManager am = (ActivityManager) _activity.getSystemService(Activity.ACTIVITY_SERVICE);
		for (ActivityManager.RunningAppProcessInfo pi : am.getRunningAppProcesses()) {
			if (pi.processName.equals("com.amazon.kindle")) {
				Log.d("ROOT", "found Kindle running with pid " + pi.pid);
				am.killBackgroundProcesses(pi.processName);
				break;
			}
		}

		return !isRunning(_activity);
	}

	//static void start(Activity _activity) {
	//	Intent k4a = _activity.getPackageManager().getLaunchIntentForPackage("com.amazon.kindle");
	//	_activity.startActivity(k4a);
	//	_activity.finish();
	//}

	static void getConfig(final Configuration _config, final KSPUI _ui) {
		_ui.disable("Loading configuration...");

		new AsyncTask<Void, Void, Integer>() {
			@Override
			protected Integer doInBackground(Void... _void) {
				File target = _config.localConfiguration;
				if (!target.exists()) {
					try {
						if (!target.createNewFile()) {
							Log.w("CONF", "failed to touch target file");
						}
					} catch (IOException ioex) {
						Log.e("CONF", "creating target file " + target, ioex);
						return RootExec.NO_CONFIG;
					}
				}
				int result = RootExec.copy(CONFIGURATION_FILE, target);
				if (result == RootExec.OK) {
					if (!_config.load()) {
						result = RootExec.NO_CONFIG;
					}
				}
				return Integer.valueOf(result);
			}

			@Override
			protected void onPostExecute(Integer _result) {
				_ui.enable();

				switch (_result) {
					case RootExec.OK:
						_ui.configurationLoaded(_config.getServiceURL());
						break;
					case RootExec.NO_ROOT:
						_ui.fatal(R.string.root_command_failed, true);
						break;
					case RootExec.NO_CONFIG:
						_ui.fatal(R.string.load_configuration_failed, true);
						break;
					default:
						_ui.fatal(R.string.unknown_error, true);
				}
			}
		}.execute();
	}

	static void setConfig(final Configuration _config, final KSPUI _ui, final KSPConfig _ksp) {
		_ui.disable("Applying configuration...");

		new AsyncTask<Void, Void, Integer>() {
			@Override
			protected Integer doInBackground(Void... _void) {
				if (!_config.save()) {
					return RootExec.SAVE_FAILED;
				}

				return applyConfig(_config.localConfiguration);
			}

			@Override
			protected void onPostExecute(Integer _result) {
				switch (_result) {
					case RootExec.OK:
						_ksp.finish();
						break;
					case RootExec.NO_ROOT:
						_ui.fatal(R.string.root_command_failed, false);
						break;
					case RootExec.SAVE_FAILED:
						_ui.fatal(R.string.save_failed, false);
						break;
					default:
						_ui.fatal(R.string.unknown_error, true);
				}

				_ui.enable();
			}
		}.execute();
	}

	private static int applyConfig(File _source) {
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH-mm-ss");
		String now = sdf.format(new Date());
		String kc_backup = CONFIGURATION_FILE + "_" + now;
		Log.i("ROOT", "will backup to " + kc_backup);

		if (RootExec.copy(CONFIGURATION_FILE, new File(kc_backup)) < 0) {
			Log.w("ROOT", "configuration backup failed");
			return RootExec.BACKUP_FAILED;
		}

		String clearCache =
				"ls " + METADATA_CACHE + " >/dev/null 2>/dev/null && rm " + METADATA_CACHE + "\n" +
				"ls " + KINDLE_CONTENT + " >/dev/null 2>/dev/null && " +
				"sqlite3 " + KINDLE_CONTENT + " 'DELETE FROM KindleContent WHERE downloadState = \"REMOTE\"'\n" +
				"ls " + KINDLE_LIBRARY + " >/dev/null 2>/dev/null && " +
				"sqlite3 " + KINDLE_LIBRARY + " 'DELETE FROM KindleContent WHERE STATE = \"REMOTE\"'\n";
		if (RootExec.suExec(clearCache) < 0) {
			Log.w("ROOT", "failed to clear Kindle caches");
		}

		return RootExec.copy(_source, CONFIGURATION_FILE);
	}
}
