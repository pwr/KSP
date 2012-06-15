/**
 * Copyright (c) 2012, Daniel Pavel (pwr)
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * The views and conclusions contained in the software and documentation are those
 * of the authors and should not be interpreted as representing official policies,
 * either expressed or implied, of the FreeBSD Project.
 */

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
