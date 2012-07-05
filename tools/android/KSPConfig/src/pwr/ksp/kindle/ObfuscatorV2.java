package pwr.ksp.kindle;

import android.util.Log;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.PBEParameterSpec;

public class ObfuscatorV2 implements Obfuscator {
	private static final String BASE = "Thomsun was here!"; // hi Thomsun
	private static final String CIPHER = "PBEWithMD5AndDES";

	private final ObfuscatorV1 fallback = new ObfuscatorV1();

	private final Cipher encryptor;
	private final Cipher decryptor;

	public ObfuscatorV2(String _salt) throws Exception {
		Log.d("OBFv2", "initialized with salt " + _salt);

		byte[] salt = Hex.toBytes(_salt);

		PBEKeySpec keySpec = new PBEKeySpec(BASE.toCharArray(), salt, 503, 128);
		SecretKey key = SecretKeyFactory.getInstance(CIPHER).generateSecret(keySpec);
		PBEParameterSpec paramSpec = new PBEParameterSpec(salt, 503);
		encryptor = Cipher.getInstance(CIPHER);
		encryptor.init(1, key, paramSpec);
		decryptor = Cipher.getInstance(CIPHER);
		decryptor.init(2, key, paramSpec);
	}

	@Override
	public String deobfuscate(String _value) {
		if (_value == null || _value.length() == 0) {
			return "";
		}

		try {
			byte[] value = Hex.toBytes(_value);
			byte[] bytes = decryptor.doFinal(value);
			return new String(bytes, "UTF-8");
		} catch (Exception ex) {
			Log.e("OBFv2", "failed to decrypt " + _value);
		}
		return fallback.deobfuscate(_value);
	}

	@Override
	public String obfuscate(String _value) {
		if (_value == null || _value.length() == 0) {
			return "";
		}

		try {
			byte[] value = _value.getBytes("UTF-8");
			byte[] bytes = encryptor.doFinal(value);
			return Hex.toHex(bytes);
		} catch (Exception ex) {
			Log.e("OBFv2", "failed to encrypt " + _value);
		}
		return fallback.obfuscate(_value);
	}
}
