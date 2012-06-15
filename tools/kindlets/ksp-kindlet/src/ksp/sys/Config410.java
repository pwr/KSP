package ksp.sys;

import com.amazon.ebook.framework.impl.Framework;
import com.amazon.ebook.util.file.p;

import java.util.Properties;

public class Config410 implements Configuration {
	public boolean loadInto(Properties _p) {
		p config = Framework.wDB().xG().getAmazonServices();

		for (int i = 0; i < ALL_KEYS.length; i++) {
			String key = ALL_KEYS[i];
			String value = config.UNA(key, null);
			if (value == null) {
				_p.remove(key);
			} else {
				_p.setProperty(key, value);
			}
		}

		return true;
	}

	public boolean save(Properties _p) {
		p config = Framework.wDB().xG().getAmazonServices();

		for (int i = 0; i < ALL_KEYS.length; i++) {
			String key = ALL_KEYS[i];
			String value = _p.getProperty(key);
			if (value == null) {
				config.remove(key);
			} else {
				config.setProperty(key, value);
			}
		}

		return true;
	}

	public boolean sync() {
		com.amazon.ebook.framework.impl.ws.y.getInstance().yPb(0, "Customer", null, true);
		return true;
	}
}
