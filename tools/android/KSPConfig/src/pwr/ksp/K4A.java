package pwr.ksp;

import android.app.Activity;
import android.app.ActivityManager;
import android.content.Intent;
import android.util.Log;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

public class K4A {
	private static final String DATA_PATH = "/data/data/com.amazon.kindle";
	private static final File CONFIGURATION_FILE = new File(new File(DATA_PATH, "shared_prefs"), Configuration.FILE_NAME);
	private static final File METADATA_CACHE = new File(new File(DATA_PATH, "files"), "KindleSyncMetadataCache.xml");
	private static final File BOOK_DATABASE = new File(new File(DATA_PATH, "databases"), "kindle_content.db");

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

		String clearCaches = "ls " + METADATA_CACHE.getAbsolutePath() + " >/dev/null 2>/dev/null &&" +
							 	"rm -f " + METADATA_CACHE.getAbsolutePath() + "\n" +
							 "ls " + BOOK_DATABASE.getAbsolutePath() + " >/dev/null 2>/dev/null &&" +
							 	"sqlite3 " + BOOK_DATABASE.getAbsolutePath() + " 'DELETE FROM KindleContent WHERE downloadState = \"REMOTE\"'";
		if (RootExec.suExec(clearCaches) < 0) {
			Log.w("ROOT", "failed to clear Kindle caches");
		}

		return RootExec.copy(_source, CONFIGURATION_FILE);
	}
}
