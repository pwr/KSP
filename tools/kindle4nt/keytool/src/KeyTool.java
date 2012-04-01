import java.io.File;
import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.Map;

public class KeyTool {
	private static final Cmd[] commands = new Cmd[]{
			new CmdList(), new CmdText(), new CmdImport(), new CmdDelete(),
	};

	static void printHelp() {
		System.out.println("Use: java -jar keytool.jar <command> [<arguments>]\nCommands:");
		for (int i = 0; i < commands.length; i++) {
			Cmd c = commands[i];
			System.out.print("  " + c.name + " -keystore <cacerts file>");
			String[] required = c.requiredArgs;
			for (int j = 0; j < required.length; j++) {
				System.out.print(" " + required[j] + " <value>");
			}
			System.out.println();
		}
		System.out.println("Note: all arguments are required; the first argument must always be '-keystore'.");
		System.exit(1);
	}

	public static void main(String[] args) throws Exception {
		if (args.length < 3 || !args[1].equals("-keystore")) {
			printHelp();
		}

		File keystore = new File(args[2]);
		if (!keystore.exists()) {
			throw new FileNotFoundException(args[2]);
		}

		Cmd c = null;
		for (int i = 0; i < commands.length; i++) {
			if (commands[i].name.equals(args[0])) {
				c = commands[i];
				break;
			}
		}
		if (c == null) {
			throw new IllegalArgumentException("Unknown command " + args[0]);
		}

		Map margs = new HashMap();
		for (int i = 3; i < args.length; i++) {
			String key = args[i];
			i++;
			if (i < args.length) {
				if (args[i].startsWith("-")) {
					margs.put(key, Boolean.TRUE);
					i--;
				} else {
					margs.put(key, args[i]);
				}
			}
		}
		for (int i = 0; i < c.requiredArgs.length; i++) {
			if (!margs.containsKey(c.requiredArgs[i])) {
				throw new IllegalArgumentException("Command " + c + " expected argument " + c.requiredArgs[i]);
			}
		}
		c.run(keystore, margs);
	}
}
