package pwr.ksp;

import android.app.Activity;
import android.app.ActivityManager;
import android.content.Intent;
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

	static void start(Activity _activity) {
		Intent k4a = _activity.getPackageManager().getLaunchIntentForPackage("com.amazon.kindle");
		_activity.startActivity(k4a);
		_activity.finish();
	}

	static int getConfig(File _target) {
		if (!_target.exists()) {
			try {
				if (!_target.createNewFile()) {
					Log.w("CONF", "failed to touch target file");
				}
			} catch (IOException ioex) {
				Log.e("CONF", "creating target file " + _target, ioex);
				return RootExec.NO_CONFIG;
			}
		}
		return RootExec.copy(CONFIGURATION_FILE, _target);
	}

	static int setConfig(File _source) {
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH-mm-ss");
		String now = sdf.format(new Date());
		String kc_backup = CONFIGURATION_FILE + "_" + now;
		Log.i("ROOT", "will backup to " + kc_backup);

		if (RootExec.copy(CONFIGURATION_FILE, new File(kc_backup)) < 0) {
			Log.w("ROOT", "configuration backup failed");
			return -1;
		}

		String removeMetadataCache = "rm " + METADATA_CACHE.getAbsolutePath();
		if (RootExec.suExec(removeMetadataCache) < 0) {
			Log.w("ROOT", "failed to clear metadata cache " + METADATA_CACHE);
		}

		String clearBookDB = "sqlite3 " + KINDLE_CONTENT.getAbsolutePath() + " 'DELETE FROM KindleContent WHERE downloadState = \"REMOTE\"'";
		if (RootExec.suExec(clearBookDB) < 0) {
			Log.w("ROOT", "failed to clear content db " + KINDLE_CONTENT);
		}

		String clearLocalBookDB = "sqlite3 " + KINDLE_LIBRARY.getAbsolutePath() + " 'DELETE FROM KindleContent WHERE STATE = \"REMOTE\"'";
		if (RootExec.suExec(clearLocalBookDB) < 0) {
			Log.w("ROOT", "failed to clear library db " + KINDLE_LIBRARY);
		}

		return RootExec.copy(_source, CONFIGURATION_FILE);
	}
}
