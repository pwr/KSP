import os.path, logging
import struct


def read_cde_type(path, asin):
	"""reads the CDE_TYPE record from the MOBI file"""
	if not os.path.isfile(path):
		return None

	# logging.debug("checking %s", path)
	asin_113 = None
	asin_504 = None
	cde_type = None

	with open(path, 'rb', 16 * 1024) as mobi:
		mobi.seek(0x3C)
		if mobi.read(8) != b'BOOKMOBI':
			logging.warn("%s: not a MOBI PDB?", path)
			return None
		mobi.seek(0x4C)
		pdb_records, = struct.unpack('!H', mobi.read(2))
		# logging.debug("%s: %d PDB records", path, pdb_records)
		mobi.seek(pdb_records * 8 + 2 + 0x10, 1)
		if mobi.read(7) != b'MOBI\x00\x00\x00':
			logging.debug("%s: MOBI header not found", path)
			return None
		header_length = mobi.read(1)[0]
		if header_length not in (0xE8, 0xF8): # MOBI7 (regular mobi), MOBI7 + MOBI8 (aka KF8) composite
			logging.debug("%s: MOBI content type %d not supported", path, hex(mobi_type))
			return None
		mobi.seek(header_length - 8, 1)
		if mobi.read(4) != b'EXTH':
			logging.debug("%s: EXTH header not found", path)
			return None

		exth_len, exth_record_count = struct.unpack('!II', mobi.read(8))
		# logging.debug("%s: %d EXTH records in %d bytes", path, exth_record_count, exth_len)
		while exth_record_count > 0:
			rec_head = mobi.read(8)
			rec_type, rec_length = struct.unpack('!II', rec_head)
			if rec_type == 0 or rec_length < 8:
				logging.warn("%s: damaged EXTH header", path)
				return None
			if rec_length > 8:
				rec_value = mobi.read(rec_length - 8)
				if rec_type == 113:
					asin_113 = str(rec_value, 'ascii')
				elif rec_type == 504:
					asin_504 = str(rec_value, 'ascii')
				elif rec_type == 501:
					cde_type = str(rec_value, 'ascii')
			exth_record_count -= 1

	if asin_504 and asin_504 != asin_113:
		logging.warn("%s: ASIN-504 %s different from ASIN-113 %s", path, asin_504, asin_113)
	if not asin_113:
		logging.warn("%s: ASIN-113 record not found", path)
		return None
	if asin_113 != asin:
		logging.warn("%s: ASIN-113 %s does not match expected ASIN %s", path, asin_113, asin)
		return None
	if not cde_type:
		logging.warn("%s: no CDE_TYPE record", path)
		return None
	if cde_type not in ( 'EBOK', 'PDOC' ):
		logging.warn("%s: unexpected CDE_TYPE '%s'", cde_type)
		return None
	# logging.debug("%s: confirmed ASIN %s with CDE TYPE %s", path, asin, cde_type)
	return cde_type
