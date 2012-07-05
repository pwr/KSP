package pwr.ksp.kindle;

import android.util.Log;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.spec.SecretKeySpec;
import java.security.MessageDigest;
import java.security.SecureRandom;

public class ObfuscatorV1 implements Obfuscator {
	private static final String BASE = "Brian was here."; // hi Brian
	private final SecretKeySpec spec;

	public ObfuscatorV1() {
		byte[] seed = getMessageDigest("SHA-256", getMessageDigest("MD5", BASE.getBytes()));
		spec = getSpec(seed);
	}

	public String deobfuscate(String _value) {
		if (_value == null || _value.length() == 0) {
			return "";
		}
		try {
			byte[] arrayOfByte = Hex.toBytes(_value);
			Cipher cipher = Cipher.getInstance("AES");
			cipher.init(2, spec);
			byte[] bytes = cipher.doFinal(arrayOfByte);
			return new String(bytes, "UTF-8");
		} catch (Exception ex) {
			Log.e("OBFv1", _value, ex);
		}
		return null;
	}

	public String obfuscate(String _value) {
		if (_value == null || _value.length() == 0) {
			return "";
		}
		try {
			Cipher cipher = Cipher.getInstance("AES");
			cipher.init(1, spec);
			byte[] bytes = cipher.doFinal(_value.getBytes("UTF-8"));
			return Hex.toHex(bytes);
		} catch (Exception ex) {
			Log.e("OBFv1", _value, ex);
		}
		return null;
	}

	//
	//
	//

	private static byte[] getMessageDigest(String _kind, byte[] _bytes) {
		try {
			MessageDigest digest = MessageDigest.getInstance(_kind);
			digest.update(_bytes);
			return digest.digest();
		} catch (Exception ex) {
			Log.e("OBF", _kind, ex);
		}
		return new byte[]{};
	}

	private static SecretKeySpec getSpec(byte[] _seed) {
		try {
			KeyGenerator keyGen = KeyGenerator.getInstance("AES");
			SecureRandom random = SecureRandom.getInstance("SHA1PRNG");
			random.setSeed(_seed);
			keyGen.init(128, random);
			byte[] generatedKey = keyGen.generateKey().getEncoded();
			return new SecretKeySpec(generatedKey, "AES");
		} catch (Exception ex) {
			Log.e("OBFv1", "getSpec", ex);
			return null;
		}
	}
}
