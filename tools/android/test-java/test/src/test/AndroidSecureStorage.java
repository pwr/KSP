package test;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Created with IntelliJ IDEA.
 * User: pwr
 * Date: 18.05.2012
 * Time: 01:38
 * To change this template use File | Settings | File Templates.
 */
public class AndroidSecureStorage {
	Map<String, String> map;

	AndroidSecureStorage(Map<String, String> _map) {
		map = _map;
	}

	public String get(String key) throws Exception {
		String okey = AndroidObfuscation.obfuscate(key);
		String value = map.get(okey);
		if (value != null)
			value = AndroidObfuscation.deobfuscate(value);
		return value;
	}

	public List<String> getKeys() {
		ArrayList<String> keys = new ArrayList<String>();
		for (java.lang.String k : map.keySet()) {
			try {
				k = AndroidObfuscation.deobfuscate(k);
				keys.add(k);
			} catch (Exception ex) {
				ex.printStackTrace();
			}
		}

		return keys;
	}

	public void set(String key, String value) throws Exception {
		String okey = AndroidObfuscation.obfuscate(key);
		String ovalue = AndroidObfuscation.obfuscate(value);
		map.put(okey, ovalue);
	}
}
