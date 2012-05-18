package test;

import org.w3c.dom.*;
import org.xml.sax.XMLReader;
import sun.security.jca.GetInstance;
import sun.security.jca.ProviderList;
import sun.security.jca.Providers;

import javax.xml.parsers.DocumentBuilderFactory;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.security.Provider;
import java.util.HashMap;

/**
 * Created with IntelliJ IDEA.
 * User: pwr
 * Date: 18.05.2012
 * Time: 00:43
 * To change this template use File | Settings | File Templates.
 */
public class Main {
	public static void main(String[] args) throws Exception {
		Harmony.init();

		File f = new File("AmazonSecureStorage.xml");
		DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
		Document d = dbf.newDocumentBuilder().parse(f);

		HashMap<String, String> map = new HashMap<String, String>();

		Element x_map = (Element) d.getElementsByTagName("map").item(0);
		NodeList x_strings = x_map.getElementsByTagName("string");
		for (int i = 0; i < x_strings.getLength(); i++) {
			Element x_string = (Element) x_strings.item(i);
			String key = x_string.getAttribute("name");

			String value;
			if (x_string.getFirstChild() != null) {
				value = x_string.getFirstChild().getNodeValue();
			} else {
				value = "";
			}
			map.put(key, value);
		}

		AndroidSecureStorage ass = new AndroidSecureStorage(map);
		System.out.println("\nMap:");
		for (String k : ass.getKeys()) {
			System.out.println("   " + k + " = " + ass.get(k));
		}

		System.out.println();
		String[] strings = { "url.todo" };
		for (String s : strings) {
			System.out.println(s + " -> " + AndroidObfuscation.obfuscate(s));
		}
	}
}
