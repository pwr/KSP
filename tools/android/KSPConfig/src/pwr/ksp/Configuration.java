package pwr.ksp;

import android.util.Log;
import android.util.Xml;
import org.xml.sax.Attributes;
import org.xml.sax.Locator;
import org.xml.sax.SAXException;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class Configuration {
	static String KSP_DATA = null;
	static final String CONFIG_FILE_NAME = "AmazonSecureStorage.xml";

	private static Configuration INSTANCE = null;

	public static Configuration get() {
		return get(false);
	}

	public static Configuration get(boolean _load) {
		if (_load) {
			try {
				INSTANCE = new Configuration();
			} catch (Exception ex) {
				Log.e("CONF", "new instance", ex);
				INSTANCE = null;
			}
		}

		return INSTANCE;
	}

	public static void clear() {
		INSTANCE = null;
	}

	static File getConfigurationFile() {
		return new File(KSP_DATA, CONFIG_FILE_NAME);
	}

	public HashMap<String, String> map = new HashMap<String, String>();

	private Configuration() throws IOException, SAXException {
		FileReader reader = new FileReader(getConfigurationFile());

		HashMap<String, String> obfuscated = new HashMap<String, String>();
		Xml.parse(reader, new XmlHandler(obfuscated));
		reader.close();

		for (Map.Entry<String, String> entry : obfuscated.entrySet()) {
			String key = Obfuscator.deobfuscate(entry.getKey());
			if (key != null) {
				String value = Obfuscator.deobfuscate(entry.getValue());
				if (value == null) {
					Log.w("CONF", "failed to load value for key " + key);
				} else {
					map.put(key, value);
//					Log.i("CONF", key + " = " + value);
				}
			}
		}
	}

	public boolean hasBaseURL() {
		return map.containsKey("url.todo");
	}

	public String getBaseURL() {
		return map.get("url.todo");
	}

	public void setBaseURL(String _url) {
		ArrayList<String> keys = new ArrayList<String>(map.keySet());
		for (String k : keys) {
			if (k.startsWith("url.")) {
				map.remove(k);
			}
		}
		if (_url != null && _url.length() > 0) {
			map.put("url.todo", _url);
		}
	}

	public boolean save() {
		if (map.isEmpty()) {
			throw new IllegalStateException("no configuration to save");
		}

		try {
			FileWriter writer = new FileWriter(getConfigurationFile());

			writer.write("<?xml version='1.0' encoding='utf-8' standalone='yes' ?>");
			writer.write("<map>");
			for (Map.Entry<String, String> entry : map.entrySet()) {
				String k = Obfuscator.obfuscate(entry.getKey());
				String v = Obfuscator.obfuscate(entry.getValue());
				writer.write("<string name=\"");
				writer.write(k);
				writer.write("\">");
				writer.write(v);
				writer.write("</string>");
			}
			writer.write("</map>");
			writer.close();

			return true;
		} catch (IOException ioex) {
			Log.e("CONF", "saving", ioex);
		}
		return false;
	}

	public String toString() {
		if (map.isEmpty()) {
			return "";
		}

		StringBuffer sb = new StringBuffer();

		String urlTodo = map.get("url.todo");
		if (urlTodo == null) {
			sb.append("No base URL (url.todo) defined.\n");
		} else {
			sb.append("Base URL (url.todo):\n");
			sb.append(urlTodo);
			sb.append("\n");
		}

		ArrayList<String> other = new ArrayList<String>();
		for (String k : map.keySet()) {
			if (k.startsWith("url.") && !k.equals("url.todo")) {
				other.add(k);
			}
		}

		if (other.isEmpty()) {
			sb.append("\nNo other urls defined.");
		} else {
			sb.append("\nOther urls defined:");
			for (String k : other) {
				sb.append("\n   - ");
				sb.append(k);
			}
		}

		return sb.toString();
	}

	private static class XmlHandler implements org.xml.sax.ContentHandler {
		private final Map<String, String> target;

		private String name;
		private StringBuffer value = new StringBuffer();

		XmlHandler(Map<String, String> _target) {
			target = _target;
		}

		@Override
		public void setDocumentLocator(Locator locator) {
			// whatever
		}

		@Override
		public void startDocument() throws SAXException {
			// whatever
		}

		@Override
		public void endDocument() throws SAXException {
			// whatever
		}

		@Override
		public void startPrefixMapping(String s, String s1) throws SAXException {
			// whatever
		}

		@Override
		public void endPrefixMapping(String s) throws SAXException {
			// whatever
		}

		@Override
		public void startElement(String _namespace, String _localName, String _qname, Attributes attributes) throws SAXException {
//			Log.i("XML", "start element " + _namespace + "/" + _localName + "/" + _qname);
			name = null;
			value.setLength(0);

			if (_qname.equals("string")) {
				name = attributes.getValue("name");
//				Log.i("XML", "string name=" + name);
			}
		}

		@Override
		public void endElement(String _namespace, String _localName, String _qname) throws SAXException {
//			Log.i("XML", "end element " + _namespace + "/" + _localName + "/" + _qname);
			if (_qname.equals("string")) {
//				Log.i("XML", name + " = " + value);
				target.put(name, value == null ? "" : value.toString());

				name = null;
				value.setLength(0);
			}
		}

		@Override
		public void characters(char[] chars, int _startIndex, int _endIndex) throws SAXException {
			value.append(chars, _startIndex, _endIndex);
//			Log.i("XML", "characters " + value);
		}

		@Override
		public void ignorableWhitespace(char[] chars, int i, int i1) throws SAXException {
			// whatever
		}

		@Override
		public void processingInstruction(String s, String s1) throws SAXException {
			// whatever
		}

		@Override
		public void skippedEntity(String s) throws SAXException {
			// whatever
		}
	}
}
