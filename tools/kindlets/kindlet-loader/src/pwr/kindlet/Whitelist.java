package pwr.kindlet;

import com.amazon.ebook.framework.impl.Framework;

import java.io.File;

public class Whitelist {
	private static final String WHITELIST_FILE = "/mnt/us/system/kindlets-whitelist.txt";
	private static final String DENIED_MESSAGE_1 = "Kindlet «";
	private static final String DENIED_MESSAGE_2 = "» not registered in the permissions whitelist.";
	private static final String BUTTON_ALLOW = "Allow full permissions";
	private static final String BUTTON_DENY = "Load normally";

	private static final StringSetFile whitelist = new StringSetFile(WHITELIST_FILE);

	private static void register(String _appId, boolean _allow) {
		System.out.println("adding " + _appId + " to kindlets whitelist: allow=" + _allow);
		whitelist.add((_allow ? "+" : "-") + _appId);
	}

	public static boolean allows(com.amazon.kindle.kindlet.internal.install.p _app) {
		File azwFile = _app.we();
		String filename = azwFile.getName().trim().toLowerCase();
		if (!filename.endsWith(".azw2")) {
			return false;
		}

		filename = filename.substring(0, filename.length() - 5);
		String appName = _app.UyA().getName();
		String appId = filename + ":" + _app.UyA().TzA();

		if (whitelist.contains("+" + appId)) {
			System.out.println(appId + " previously allowed");
			return true;
		}
		if (whitelist.contains("-" + appId)) {
			System.out.println(appId + " previously denied");
			return false;
		}

		com.amazon.ebook.framework.gui.foundation.vb alert = //
				new com.amazon.ebook.framework.gui.foundation.vb( //
																  DENIED_MESSAGE_1 + appName + DENIED_MESSAGE_2, //
																  BUTTON_ALLOW, 1, new Handler(appId), BUTTON_DENY);
		Framework.wDB().getUIManager().KVb(alert);
		System.out.println("temporarily denying " + appId);
		return false;
	}

	private static final class Handler implements com.amazon.ebook.framework.gui.event.h {
		private final String appId;

		private Handler(String _appId) {
			appId = _appId;
		}

		public void xf(Object _alert) {
			com.amazon.ebook.framework.gui.foundation.vb alert = (com.amazon.ebook.framework.gui.foundation.vb) _alert;
			register(appId, alert.cpb());
		}
	}
}
