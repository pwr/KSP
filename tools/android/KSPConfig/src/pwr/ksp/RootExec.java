package pwr.ksp;

import android.app.ActivityManager;
import android.util.Log;

import java.io.*;
import java.text.SimpleDateFormat;
import java.util.Date;

final class RootExec {
	private static final String KINDLE_PATH = "/data/data/com.amazon.kindle";
	private static final File KINDLE_CONFIGURATION = new File(new File(KINDLE_PATH, "shared_prefs"), Configuration.CONFIG_FILE_NAME);
	private static final File KINDLE_METADATA_CACHE = new File(new File(KINDLE_PATH, "files"), "KindleSyncMetadataCache.xml");
	private static final File KINDLE_DATABASE = new File(new File(KINDLE_PATH, "databases"), "kindle_content.db");

	static final int OK = 0;
	private static final int NO_ROOT = -10;
	static final int NO_CONFIG = -20;

	static int getKindleConfig(File _target) {
		return copy(KINDLE_CONFIGURATION, _target);
	}

	static int setKindleConfig(File _source) {
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH-mm-ss");
		String now = sdf.format(new Date());
		String kc_backup = KINDLE_CONFIGURATION + "_" + now;
		Log.i("ROOT", "will backup to " + kc_backup);

		if (copy(KINDLE_CONFIGURATION, new File(kc_backup)) < 0) {
			Log.w("ROOT", "configuration backup failed");
			return -1;
		}

		String clearCaches = "rm " + KINDLE_METADATA_CACHE.getAbsolutePath() + "\n" +
				"sqlite3 " + KINDLE_DATABASE.getAbsolutePath() + " 'DELETE FROM KindleContent WHERE downloadState = \"REMOTE\"'";
		if (suExec(clearCaches) < 0) {
			Log.w("ROOT", "failed to clear Kindle caches");
		}

		return copy(_source, KINDLE_CONFIGURATION);
	}

	static void stopKindle(ActivityManager _am) {
		for (ActivityManager.RunningAppProcessInfo pi : _am.getRunningAppProcesses()) {
			if (pi.processName.equals("com.amazon.kindle")) {
				Log.d("ROOT", "found Kindle running with pid " + pi.pid);
				_am.killBackgroundProcesses(pi.processName);
				android.os.Process.sendSignal(pi.pid, android.os.Process.SIGNAL_KILL);
				break;
			}
		}
	}

	private static int copy(File _source, File _destination) {
		return suExec("cat " + _source.getAbsolutePath() + " > " + _destination.getAbsolutePath());
	}

	private static int suExec(String _commands) {
		try {
			Process su = Runtime.getRuntime().exec("su");
			Writer w = new OutputStreamWriter(su.getOutputStream());
			w.write(_commands);
			w.write("\nexit\n");
			w.flush();

			try {
				su.waitFor();
				String stderr = read(su.getErrorStream());
				if (stderr.length() == 0 && su.exitValue() == 0) {
					Log.i("ROOT", "su success: " + _commands);
					return 0;
				}

				Log.i("ROOT", "su fail: " + _commands);
				Log.i("ROOT", "stderr: [" + stderr + "]");
				if (stderr.indexOf("No such file or directory") > 0) {
					return NO_CONFIG;
				}
				return NO_ROOT;
			} catch (InterruptedException iex) {
				Log.e("ROOT", _commands, iex);
				return NO_ROOT;
			}
		} catch (IOException ex) {
			Log.e("ROOT", _commands, ex);
			return NO_ROOT;
		}
	}

	private static String read(InputStream s) {
		StringBuilder sb = new StringBuilder();
		try {
			BufferedReader r = new BufferedReader(new InputStreamReader(s));
			while (true) {
				String line = r.readLine();
				if (line == null) {
					break;
				}
				sb.append(line);
				sb.append("\n");
			}
		} catch (Exception ex) {
			Log.e("ROOT", "read stream", ex);
		}
		return sb.toString().trim();
	}
}
