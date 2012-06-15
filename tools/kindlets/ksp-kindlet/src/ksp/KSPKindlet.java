package ksp;

import com.amazon.kindle.kindlet.Kindlet;
import com.amazon.kindle.kindlet.KindletContext;

import java.awt.EventQueue;

public class KSPKindlet implements Kindlet {
	private Log log = null;

	private KindletContext context;
	private ServiceConfig conf = null;

	UI ui = null;
	Actions act = null;
	private Pinger pinger = null;

	public void create(KindletContext _context) {
		context = _context;

		log = new Log(KSPKindlet.class);
		log.i("create()");

		conf = new ServiceConfig();
		act = new Actions(this, conf);
		ui = new UI(context.getRootContainer(), act);
	}

	public void start() {
		log.i("start()");
		EventQueue.invokeLater(act.reloadAction);
	}

	public void stop() {
		log.i("stop()");

		if (pinger != null) {
			pinger.interrupt();
			pinger = null;
		}
	}

	public void destroy() {
		ui = null;
		log = null;
		conf = null;
		act = null;
	}

	boolean checkConnected() {
		try {
			context.getConnectivity().requestConnectivity(true);
			return true;
		} catch (Exception ex) {
			log.e("network not available", ex);
			return false;
		}
	}

	void progress(String _message) {
		context.getProgressIndicator().setString(_message);
	}

	void ping(String _url) {
		if (pinger != null) {
			pinger.interrupt();
		}

		pinger = new Pinger(this, _url);
		pinger.start();
	}
}
