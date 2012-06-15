package pwr.kindlet;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

class StringSetFile {
	private final File setFile;
	private final Set set = new HashSet();
	private long lastModified = 0;

	StringSetFile(String _path) {
		setFile = new File(_path);
		load();
	}

	void add(String _s) {
		set.add(_s);
		save();
	}

	boolean contains(String _s) {
		load();
		return set.contains(_s);
	}

	private void load() {
		if (!setFile.exists()) {
			set.clear();
			return;
		}

		long modified = setFile.lastModified();
		if (modified <= lastModified) {
			return;
		}

		System.out.println("(re)loading " + setFile);

		synchronized (this) {
			lastModified = modified;
			set.clear();

			try {
				BufferedReader br = new BufferedReader(new FileReader(setFile));
				while (true) {
					String line = br.readLine();
					if (line == null) {
						break;
					}
					line = line.trim();
					if (line.length() == 0) {
						continue;
					}
					set.add(line.toLowerCase());
				}
				br.close();
			} catch (IOException ioex) {
				ioex.printStackTrace();
			}
		}
	}

	private void save() {
		System.out.print("saving " + setFile);

		synchronized (this) {
			try {
				BufferedWriter bw = new BufferedWriter(new FileWriter(setFile));
				for (Iterator it = set.iterator(); it.hasNext(); ) {
					bw.write((String) it.next());
					bw.write('\n');
				}
				bw.close();
			} catch (IOException ioex) {
				ioex.printStackTrace();
			}

			lastModified = setFile.lastModified();
		}
	}
}
