package test;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class AndroidObfuscation {
	static SecretKeySpec spec = new SecretKeySpec(hexToBytes("0176e04c9408b1702d90be333fd53523"), "AES");

	//	static SecretKeySpec spec = getSpec(getSeed());
	//	static {
	//		System.out.println("seed = " + toHex(getSeed()));
	//		System.out.println("spec " + spec.getAlgorithm() + " / " + spec.getFormat());
	//		System.out.println("encoded spec = " + toHex(spec.getEncoded()));
	//	}

	public static byte[] hexToBytes(String s) {
		int len = s.length();
		byte[] data = new byte[len / 2];
		for (int i = 0; i < len; i += 2) {
			data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4) + Character.digit(s.charAt(i + 1), 16));
		}
		return data;
	}

	public static String toHex(byte[] bytes) {
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

	//	static byte[] getMessageDigest(String paramString, byte[] paramArrayOfByte) {
	//		try {
	//			MessageDigest localMessageDigest = MessageDigest.getInstance(paramString);
	//			localMessageDigest.update(paramArrayOfByte);
	//			return localMessageDigest.digest();
	//		} catch (Exception ex) {
	//			return null;
	//		}
	//	}
	//
	//	static byte[] getSeed() {
	//		return getMessageDigest("SHA-256", getMessageDigest("MD5", "Brian was here.".getBytes()));
	//	}
	//
	//	static SecretKeySpec getSpec(byte[] paramArrayOfByte) {
	//		try {
	//			KeyGenerator localKeyGenerator = KeyGenerator.getInstance("AES");
	//			SecureRandom localSecureRandom = SecureRandom.getInstance(Harmony.SHA1PRNG_NAME);
	//			localSecureRandom.setSeed(paramArrayOfByte);
	//			localKeyGenerator.init(128, localSecureRandom);
	//			SecretKeySpec localSecretKeySpec = new SecretKeySpec(localKeyGenerator.generateKey().getEncoded(), "AES");
	//			return localSecretKeySpec;
	//		} catch (Exception ex) {
	//			ex.printStackTrace();
	//			return null;
	//		}
	//	}

	public static String obfuscate(String paramString) throws Exception {
		if (paramString == null) {
			throw new IllegalArgumentException("text must have value!");
		}
		if (paramString.length() == 0) {
			return "";
		}

		Cipher localCipher = Cipher.getInstance("AES");
		localCipher.init(1, spec);
		byte[] plainBytes = paramString.getBytes("UTF-8");
		byte[] crypted = localCipher.doFinal(plainBytes);
		return toHex(crypted);
	}

	public static String deobfuscate(String paramString) throws Exception {
		if (paramString == null) {
			throw new IllegalArgumentException("String must have value!");
		}
		if (paramString.length() == 0) {
			return "";
		}

		byte[] arrayOfByte = hexToBytes(paramString);
		Cipher localCipher = Cipher.getInstance("AES");
		localCipher.init(2, spec);
		byte[] decrypted = localCipher.doFinal(arrayOfByte);
		return new String(decrypted, "UTF-8");
	}

}