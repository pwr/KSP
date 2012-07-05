package pwr.ksp;

import android.util.Log;

import java.io.*;

final class RootExec {
	static final int OK = 0;
	static final int NO_ROOT = -10;
	static final int NO_CONFIG = -20;
	static final int SAVE_FAILED = -5;
	static final int BACKUP_FAILED = -6;

	static int copy(File _source, File _destination) {
		return suExec("cat " + _source.getAbsolutePath() + " > " + _destination.getAbsolutePath());
	}

	static int suExec(String _commands) {
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
