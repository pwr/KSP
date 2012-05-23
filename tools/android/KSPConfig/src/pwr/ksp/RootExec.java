package pwr.ksp;

import android.app.ActivityManager;
import android.os.*;
import android.util.Log;

import java.io.*;
import java.lang.Process;
import java.text.SimpleDateFormat;
import java.util.Date;

public final class RootExec {
	private static final String KINDLE_PATH = "/data/data/com.amazon.kindle/shared_prefs/";
	private static final String KINDLE_CONFIGURATION = new File(KINDLE_PATH, Configuration.CONFIG_FILE_NAME).getAbsolutePath();

	static boolean getConfig() {
		return copy(KINDLE_CONFIGURATION, Configuration.getConfigurationFile().getAbsolutePath());
	}

	static boolean setConfig() {
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH-mm-ss");
		String now = sdf.format(new Date());
		String kc_backup = KINDLE_CONFIGURATION + "_" + now;
		Log.i("ROOT", "will backup to " + kc_backup);

		if (copy(KINDLE_CONFIGURATION, kc_backup)) {
			return copy(Configuration.getConfigurationFile().getAbsolutePath(), KINDLE_CONFIGURATION);
		}
		Log.w("ROOT", "configuration backup failed");
		return false;
	}

	static boolean stopKindle(ActivityManager _am) {
		for (ActivityManager.RunningAppProcessInfo pi : _am.getRunningAppProcesses()) {
			if (pi.processName.equals("com.amazon.kindle")) {
				Log.d("ROOT", "found Kindle running with pid " + pi.pid);
				_am.killBackgroundProcesses(pi.processName);
				android.os.Process.sendSignal(pi.pid, android.os.Process.SIGNAL_KILL);
				break;
			}
		}

		return true;
	}

	private static boolean copy(String _source, String _destination) {
		try {
			Process su = Runtime.getRuntime().exec("/system/bin/su");
			Writer w = new OutputStreamWriter(su.getOutputStream());
			w.write("cat ");
			w.write(_source);
			w.write(" > ");
			w.write(_destination);
			w.write("\nexit\n");
			w.flush();

			try {
				su.waitFor();
				String stderr = read(su.getErrorStream());
				if (stderr.isEmpty() && su.exitValue() == 0) {
					Log.i("ROOT", "copy success: " + _source + " -> " + _destination);
					return true;
				} else {
					Log.i("ROOT", "copy fail: " + _source + " -> " + _destination);
					Log.i("ROOT", "stderr: [" + stderr + "]");
				}
			} catch (InterruptedException iex) {
				Log.e("ROOT", _source, iex);
			}
		} catch (IOException ex) {
			Log.e("ROOT", _source, ex);
		}

		return false;
	}

	private static String read(InputStream s) {
		StringBuffer sb = new StringBuffer();
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
