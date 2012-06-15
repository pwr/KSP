package ksp;

public class Log {
	private static final String INFO = " INFO  ";
	private static final String WARN = " WARN  ";
	private static final String ERROR = " ERROR ";

	private final String tag;

	public Log(Class _clazz) {
		tag = _clazz.getName();
	}

	public void i(String _text) {
		_log(tag, INFO, _text, null);
	}

	public void w(String _text) {
		_log(tag, WARN, _text, null);
	}

	public void w(String _text, Throwable _t) {
		_log(tag, WARN, _text, _t);
	}

	public void e(String _text, Throwable _t) {
		_log(tag, ERROR, _text, _t);
	}

	private static void _log(String _tag, String _level, String _text, Throwable _t) {
		System.out.print('{');
		System.out.print(Thread.currentThread().getName());
		System.out.print("} ");
		System.out.print(_tag);
		System.out.print(_level);
		System.out.print(_text);

		if (_t != null) {
			System.out.print(": ");
			System.out.print(_t.getClass().getName());
			System.out.print(": ");
			System.out.print(_t.getMessage());
		}
		System.out.println();

		if (_t != null) {
			_t.printStackTrace(System.out);
		}
	}
}
