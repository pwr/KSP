package test;

import sun.security.jca.ProviderList;
import sun.security.jca.Providers;

import java.security.Provider;
import java.security.SecureRandom;
import java.security.SecureRandomSpi;

/**
 * Created with IntelliJ IDEA.
 * User: pwr
 * Date: 18.05.2012
 * Time: 02:59
 * To change this template use File | Settings | File Templates.
 */
public class Harmony extends Provider {
	static final String NAME = "Harmony_Dalvik";
	static final String SHA1PRNG_NAME = "SHA1PRNG_Harmony";

	static final SecureRandomSpi SHA1PRNG_SPI = new SHA1PRNG_SecureRandomImpl();

	static void init() {
		ProviderList pl = Providers.getProviderList();
		pl = ProviderList.insertAt(pl, new Harmony(), 0);
		Providers.setProviderList(pl);
		pl = Providers.getProviderList();

		try {
			SecureRandom sr = SecureRandom.getInstance(SHA1PRNG_NAME);
		} catch (Exception ex) {
			ex.printStackTrace();
			throw new RuntimeException("Harmony", ex);
		}
	}

	protected Harmony() {
		super(NAME, 1.0, "Apache Harmony for Dalvik");
		putService(new Service(this, "SecureRandom", SHA1PRNG_NAME, SHA1PRNG_SPI.getClass().getName(), null, null));
	}
}
