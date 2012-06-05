package pwr.ksp.net;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.util.Log;
import pwr.ksp.KSPConfig;
import pwr.ksp.R;
import pwr.ksp.ui.Dialogs;

import java.util.Map;

public class PingResultHandler implements Ping.OnFinished {
	private final KSPConfig ksp;

	public PingResultHandler(KSPConfig _ksp) {
		ksp = _ksp;
	}

	@Override
	public void finished(String _url, Exception _status) {
		if (_url == null || _url.length() == 0) {
			Log.e("PING", "ping finished with no url");
			return;
		}

		if (_status == null) {
			ksp.getConfig().setServiceURL(_url);
			ksp.ui.configurationChanged(_url);
			return;
		}

		if (_status instanceof Ping.SCFG) {
			Ping.SCFG scfg = (Ping.SCFG)_status;
			ksp.getConfig().setSCFG(scfg.map);
			ksp.ui.configurationChanged(ksp.getConfig().getServiceURL());
			return;
		}

		if (_status instanceof Ping.Redirect) {
			ksp.ping(_status.getMessage());
			return;
		}

		if (_status instanceof Cert.Ex) {
			byte[] der = ((Cert.Ex)_status).der;
			Intent i = new Intent(Cert.INSTALL);
			i.putExtra("CERT", der);

			ksp.installing_certificate_for = _url;
			// well crap
			try {
				ksp.startActivityForResult(i, Cert.INSTALL_REQUEST);
			} catch (ActivityNotFoundException ex) {
				ksp.installing_certificate_for = null;
				Log.e("CERT", "failed to start certificate installation activity", ex);
				Dialogs.error(ksp, ksp.getString(R.string.install_certificate_failed));
			} catch (Exception ex) {
				ksp.installing_certificate_for = null;
				Log.e("CERT", "failed to install certificate", ex);
				Dialogs.error(ksp, ex.getMessage());
			}
			return;
		}

		Dialogs.error(ksp, _status.getMessage());
	}
}
