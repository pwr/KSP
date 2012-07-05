package pwr.ksp;

import android.app.Activity;
import android.util.Log;
import android.util.Xml;
import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;
import pwr.ksp.kindle.Obfuscator;
import pwr.ksp.kindle.ObfuscatorV1;
import pwr.ksp.kindle.ObfuscatorV2;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class Configuration {
	public static final String FILE_NAME = "AmazonSecureStorage.xml";
	private static final String SALT_KEY = "AmazonSaltKey";
	private static final String URL_TODO = "url.todo";
	private static final String URL_CDE = "url.cde";

	final File localConfiguration;
	private final HashMap<String, String> map = new HashMap<String, String>();
	private Obfuscator obfuscator = null;

	public Configuration(Activity _act) {
		File localTemp = _act.getDir("temp", Activity.MODE_PRIVATE);
		localConfiguration = new File(localTemp, FILE_NAME);
	}

	public String getServiceURL() {
		return map.get(URL_TODO);
	}

	public void setServiceURL(String _url) {
		ArrayList<String> keys = new ArrayList<String>(map.keySet());
		for (String k : keys) {
			if (k.startsWith("url.")) {
				map.remove(k);
			}
		}
		if (_url != null && _url.length() > 0) {
			map.put(URL_TODO, _url);
			map.put(URL_CDE, _url);
		}
	}

	public void setSCFG(Map<String, String> _map) {
		ArrayList<String> keys = new ArrayList<String>(map.keySet());
		for (String k : keys) {
			if (k.startsWith("url.")) {
				map.remove(k);
			}
		}
		map.putAll(_map);
	}

	boolean load() {
		if (!localConfiguration.exists() || !localConfiguration.isFile()) {
			Log.e("CONF", "local configuration file " + localConfiguration.getAbsolutePath() + " missing");
			return false;
		}

		FileReader reader = null;
		HashMap<String, String> obfuscated = null;
		try {
			reader = new FileReader(localConfiguration);
			obfuscated = new HashMap<String, String>();
			Xml.parse(reader, new XmlHandler(obfuscated));
			reader.close();
		} catch (Exception ex) {
			Log.e("CONF", "failed to load copy of configuration", ex);
			return false;
		} finally {
			if (reader != null) {
				try {
					reader.close();
				} catch (IOException ioex) {
					// whatever
				}
			}
		}

		String salt = obfuscated.get(SALT_KEY);
		if (salt == null) {
			obfuscator = new ObfuscatorV1();
		} else {
			try {
				obfuscator = new ObfuscatorV2(salt);
			} catch (Exception ex) {
				Log.e("CONF", "failed to initialize ObfuscatorV2 with " + salt, ex);
				return false;
			}
		}

		map.clear();
		for (Map.Entry<String, String> entry : obfuscated.entrySet()) {
			if (SALT_KEY.equals(entry.getKey())) {
				map.put(SALT_KEY, entry.getValue());
				continue;
			}

			String key = obfuscator.deobfuscate(entry.getKey());
			if (key != null) {
				String value = obfuscator.deobfuscate(entry.getValue());
				if (value == null) {
					Log.w("CONF", "failed to load value for key " + key);
				} else {
					map.put(key, value);
					if (key.startsWith("url.")) {
						Log.i("CONF", "  " + key + " = " + value);
					}
				}
			}
		}

		Log.i("CONF", "loaded configuration with url: " + getServiceURL());
		return true;
	}

	boolean save() {
		if (obfuscator == null) {
			Log.e("CONF", "no obfuscator set before saving configuration");
			return false;
		}

		try {
			FileWriter writer = new FileWriter(localConfiguration);

			writer.write("<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n");
			writer.write("<map>\n");
			for (Map.Entry<String, String> entry : map.entrySet()) {
				String k, v;

				if (SALT_KEY.equals(entry.getKey())) {
					k = SALT_KEY;
					v = entry.getValue();
				} else {
					k = obfuscator.obfuscate(entry.getKey());
					v = obfuscator.obfuscate(entry.getValue());
				}
				writer.write("<string name=\"");
				writer.write(k);
				writer.write("\">");
				writer.write(v);
				writer.write("</string>\n");
			}
			writer.write("</map>");
			writer.close();

			return true;
		} catch (IOException ioex) {
			Log.e("CONF", "saving", ioex);
		}
		return false;
	}

	private static final class XmlHandler extends DefaultHandler {
		private final Map<String, String> target;

		private String name;
		private final StringBuilder value = new StringBuilder();

		XmlHandler(Map<String, String> _target) {
			target = _target;
		}

		@Override
		public void startElement(String _namespace, String _localName, String _qname, Attributes attributes) throws SAXException {
			//Log.i("XML", "start element " + _namespace + "/" + _localName + "/" + _qname);
			name = null;
			value.setLength(0);

			if (_qname.equals("string")) {
				name = attributes.getValue("name");
				//Log.i("XML", "string name=" + name);
			}
		}

		@Override
		public void endElement(String _namespace, String _localName, String _qname) throws SAXException {
			//Log.i("XML", "end element " + _namespace + "/" + _localName + "/" + _qname);
			if (_qname.equals("string")) {
				//Log.i("XML", name + " = " + value);
				target.put(name, value.toString());
				name = null;
				value.setLength(0);
			}
		}

		@Override
		public void characters(char[] chars, int _startIndex, int _endIndex) throws SAXException {
			value.append(chars, _startIndex, _endIndex);
			//Log.i("XML", "characters " + value);
		}
	}
}
