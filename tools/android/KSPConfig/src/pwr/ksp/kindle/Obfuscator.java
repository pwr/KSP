package pwr.ksp.kindle;

import android.util.Log;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.spec.SecretKeySpec;
import java.security.MessageDigest;
import java.security.SecureRandom;

public class Obfuscator {
	private final static SecretKeySpec spec = getSpec(getSeed());

	private static byte[] hexToBytes(String s) {
		int len = s.length();
		byte[] data = new byte[len / 2];
		for (int i = 0; i < len; i += 2) {
			data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4) + Character.digit(s.charAt(i + 1), 16));
		}
		return data;
	}

	private static String toHex(byte[] bytes) {
		StringBuilder sb = new StringBuilder(bytes.length * 2);
		for (byte b : bytes) {
			String s = Integer.toHexString(b);
			if (s.length() == 1) {
				sb.append('0');
			} else if (s.length() > 2) {
				s = s.substring(s.length() - 2);
			}
			sb.append(s);
		}
		return sb.toString();
	}

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

	private static byte[] getSeed() {
		String base = "Brian was here."; // hi Brian
		return getMessageDigest("SHA-256", getMessageDigest("MD5", base.getBytes()));
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
			Log.e("OBF", "getSpec", ex);
			return null;
		}
	}

	public static String deobfuscate(String _value)  {
		if (_value == null || _value.length() == 0) {
			return "";
		}
		try {
			byte[] arrayOfByte = hexToBytes(_value);
			Cipher cipher = Cipher.getInstance("AES");
			cipher.init(2, spec);
			byte[] bytes = cipher.doFinal(arrayOfByte);
			return new String(bytes, "UTF-8");
		} catch (Exception ex) {
			Log.e("OBF", _value, ex);
		}
		return null;
	}

	public static String obfuscate(String _value) {
		if (_value == null || _value.length() == 0) {
			return "";
		}
		try {
			Cipher cipher = Cipher.getInstance("AES");
			cipher.init(1, spec);
			byte[] bytes = cipher.doFinal(_value.getBytes("UTF-8"));
			return toHex(bytes);
		} catch (Exception ex) {
			Log.e("OBF", _value, ex);
		}
		return null;
	}
}
