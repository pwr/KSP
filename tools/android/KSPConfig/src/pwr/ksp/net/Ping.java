package pwr.ksp.net;

import android.app.ProgressDialog;
import android.content.Context;
import android.net.http.AndroidHttpClient;
import android.os.AsyncTask;
import android.os.Build;
import android.util.Log;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.protocol.HTTP;

import javax.net.ssl.SSLHandshakeException;
import java.io.IOException;
import java.io.StringWriter;
import java.io.UnsupportedEncodingException;
import java.util.HashMap;

public class Ping extends AsyncTask<String, String, Exception> {
	private static final Exception SSL = new Exception("SSL handshake failed, are you sure it is an HTTPS server?");
	private static final Exception INVALID_RESPONSE = new Exception("Received invalid response, are you sure the URL is pointing to a KSP installation?");
	private static final String PING_PATH = "/FionaTodoListProxy/getItems?reason=ServiceRefresh";
	private static final String USER_AGENT = "Dalvik/KSPConfig Android ";

	private final Context ctx;
	private final OnFinished callback;
	private String url = null;

	public Ping(Context _ctx, OnFinished _callback) {
		ctx = _ctx;
		callback = _callback;
	}

	@Override
	protected Exception doInBackground(String... strings) {
		if (strings == null || strings.length == 0) {
			return null;
		}

		url = strings[0];
		publishProgress(url);

		AndroidHttpClient hc = AndroidHttpClient.newInstance(ctx.getApplicationInfo().processName);
		hc.enableCurlLogging("PING", android.util.Log.INFO);
		try {
			HttpUriRequest req = new HttpGet(url + PING_PATH);
			req.setHeader(HTTP.USER_AGENT, USER_AGENT + Build.VERSION.RELEASE);
			String body = readBody(hc.execute(req));
			return body == null ? INVALID_RESPONSE : checkRedirect(url, body);
		} catch (SSLHandshakeException ex) {
			Log.e("PING", url, ex);
			byte[] certificate = Cert.handle(ex);
			if (certificate != null) {
				return new Cert.Ex(certificate);
			}
			return SSL;
		} catch (Exception ex) {
			Log.w("PING", ex.getClass() + ":" + ex.getMessage());
			Log.e("PING", url, ex);
			return ex;
		} finally {
			hc.close();
		}
	}

	private String readBody(HttpResponse _res) {
		StatusLine status = _res.getStatusLine();
		Log.i("PING", status.getStatusCode() + " " + status.getReasonPhrase());
		if (status.getStatusCode() != 200) {
			return null;
		}

		HttpEntity he = _res.getEntity();
		int length = (int) he.getContentLength();
		if (length < 1) {
			return null;
		}

		byte[] buffer = new byte[length];
		try {
			length = he.getContent().read(buffer);
		} catch (IOException ioex) {
			Log.e("PING", "reading ping response", ioex);
			return null;
		}

		StringWriter sw = new StringWriter(length);
		try {
			sw.write(new String(buffer, 0, length, "UTF-8"));
		} catch (UnsupportedEncodingException ueex) {
			// wtf?
			Log.e("PING", "reading ping response", ueex);
			return null;
		}

		return sw.toString();
	}

	private Exception checkRedirect(String _url, String _body) {
		if (!_body.startsWith("<?xml version=\"1.0\" encoding=\"UTF-8\"?><response>")) {
			return INVALID_RESPONSE;
		}
		if (!_body.contains("<items><item action=\"SET\"") || !_body.contains(" type=\"SCFG\"")) {
			return INVALID_RESPONSE;
		}

		SCFG ex = new SCFG();
		String[] lines = _body.split("\n");
		for (String l : lines) {
			if (l.startsWith("url.")) {
				String[] kv = l.split("=");
				if (kv.length != 2) {
					Log.w("PING", "bad SCFG line " + l);
					continue;
				}
				if (kv[0].equals(SCFG.URL_TODO)) {
					if (!kv[1].equals(_url)) {
						return new Redirect(kv[1]);
					}
				}
				ex.map.put(kv[0], kv[1]);
			}
		}

		return ex.isValid() ? ex : INVALID_RESPONSE;
	}

	private ProgressDialog ping_dialog = null;

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
	protected void onPostExecute(Exception ex) {
		super.onPostExecute(ex);
		ping_dialog.dismiss();
		ping_dialog = null;
		callback.finished(url, ex);
		url = null;
	}

	public interface OnFinished {
		void finished(String _url, Exception _status);
	}

	static final class Redirect extends Exception {
		Redirect(String _newUrl) {
			super(_newUrl);
		}
	}

	static final class SCFG extends Exception {
		static final String URL_TODO = "url.todo";

		final HashMap<String, String> map = new HashMap<String, String>();

		boolean isValid() {
			return map.containsKey(URL_TODO);
		}
	}
}
