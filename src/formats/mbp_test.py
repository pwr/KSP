# testing
import sys, os.path, time
from collections import namedtuple

import mbp

ppath = os.path.join(__file__, '../../..')
sys.path += [ os.path.join(ppath, 'src'), os.path.join(ppath, 'etc') ]
import config
config.database_path = os.path.join(ppath, 'captures/mbp')
import annotations


ASIN = '34436c3a-8233-41f9-aed2-4cd4b019cb3e'

sidecar_list = annotations.list(ASIN)
for s in sidecar_list:
	print(*s)
book = namedtuple('_Book', 'file_path added_to_library')(os.path.join(config.database_path, 'test.mobi'), int(time.time()))

print()

content_type, b = mbp.assemble_sidecar(book, sidecar_list)
l = 0
print("Offset(h) 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F\n")
while l < len(b):
	line = b[l:min(len(b), l+32)]
	count = len(line)

	fmt = "%08x  " + ("%02x " * count) + ("   " * (32 - count)) + "  " # + ("%c" * count)
	s = fmt % tuple([l, ] + [c for c in line]) # * 2)

	for i in range(0, count):
		c = b[l + i]
		if c in range(0x00, 0x20):
			s += '.'
		elif c in range(0x20, 0x80):
			s += chr(c)
		# elif c in range(0x80, 0xFF):
		# 	s += chr(c)
		else:
			s += '.'
	print(s)
	l += 32
