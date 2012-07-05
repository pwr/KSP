package pwr.ksp.kindle;

class Hex {
	static byte[] toBytes(String s) {
		int len = s.length();
		byte[] data = new byte[len / 2];
		for (int i = 0; i < len; i += 2) {
			data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4) + Character.digit(s.charAt(i + 1), 16));
		}
		return data;
	}

	static String toHex(byte[] bytes) {
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
}
