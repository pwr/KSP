/**
 * Copyright (c) 2012, Daniel Pavel (pwr)
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * The views and conclusions contained in the software and documentation are those
 * of the authors and should not be interpreted as representing official policies,
 * either expressed or implied, of the FreeBSD Project.
 */

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
