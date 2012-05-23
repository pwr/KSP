package pwr.ksp;

import android.app.ProgressDialog;
import android.content.Context;
import android.net.http.AndroidHttpClient;
import android.os.AsyncTask;
import android.util.Log;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpUriRequest;

public class Ping extends AsyncTask<String, String, String> {
	private final Context ctx;
	private final OnFinished callback;

	public Ping(Context _ctx, OnFinished _callback) {
		ctx = _ctx;
		callback = _callback;
	}

	@Override
	protected String doInBackground(String... strings) {
		if (strings == null || strings.length == 0) {
			return null;
		}

		String url = strings[0];
		onProgressUpdate(url);

		AndroidHttpClient hc = AndroidHttpClient.newInstance("KSPConfig");
		try {
			HttpUriRequest req = new HttpGet(url + "/poll");
			HttpResponse res = hc.execute(req);
			StatusLine status = res.getStatusLine();
			Log.i("PING", status.getStatusCode() + " " + status.getReasonPhrase());
			if (status.getStatusCode() == 418) {
				return null;
			}
			return "Received invalid status code, are you sure the URL is pointing to a KSP installation?";
		} catch (Exception ex) {
			Log.w("PING", ex.getClass() + ":" + ex.getMessage());
			Log.e("PING", url, ex);
			return ex.getMessage();
		} finally {
			hc.close();
		}
	}

	private ProgressDialog ping_dialog;

	@Override
	protected void onPreExecute() {
		super.onPreExecute();
		ping_dialog = ProgressDialog.show(ctx, "Checking URL...", "");
	}

	@Override
	protected void onProgressUpdate(String... values) {
		super.onProgressUpdate(values);
		ping_dialog.setMessage(values[0]);
	}

	@Override
	protected void onPostExecute(String s) {
		super.onPostExecute(s);
		ping_dialog.dismiss();
		callback.finished(s);
	}

	public interface OnFinished {
		void finished(String _status);
	}
}
