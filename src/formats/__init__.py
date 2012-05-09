import logging


CONTENT_TYPE_MOBIPOCKET = 'application/x-mobipocket-ebook'
CONTENT_TYPE_PDF = 'application/pdf'
CONTENT_TYPES = {
	'EPUB'	: 'application/epub+zip',
	'MOBI'	: CONTENT_TYPE_MOBIPOCKET,
	'AZW'	: CONTENT_TYPE_MOBIPOCKET,
	'PRC'	: CONTENT_TYPE_MOBIPOCKET,
	'PDF'	: CONTENT_TYPE_PDF,
	# 'AZW1'	: 'application/x-topaz-ebook',
	# 'AZW3'	: 'application/x-mobi8-ebook',
	# 'HTML'	: 'text/html',
	# 'TXT'	: 'text/plain',
	# 'CBZ'	: 'application/zip',
}
CDE_TYPES = {
	'EPUB'	: 'EBOK',
	'MOBI'	: 'EBOK',
	'AZW'	: 'EBOK',
	'PRC'	: 'EBOK',
	'PDF'	: 'PDOC',
	# 'AZW1'	: 'EBOK',
	# 'AZW3'	: 'EBOK',
	# 'HTML'	: 'PDOC',
	# 'TXT'	: 'PDOC',
	# 'CBZ'	: 'PDOC',
}

#	'MBP'  : ( '????', 'application/x-mobipocket-sidecar' ),
#	'TAN'  : ( '????', 'application/x-topaz-sidecar' ),
# 	'XYML' : ( '????', 'text/xyml' ),
# 	'JPG'  : ( '????', 'image/jpeg' ),
# 	'AZW2' : ( '????', 'application/x-kindle-application' ),
# 	'KCRT' : ( '????', 'application/x-developer-certificate' ),
# 	'PHL'  : ( 'PHL',  'application/xml+phl' ),
# 	'APNX' : ( 'APNX', 'application/x-apnx-sidecar' ),
# 	'EA'   : ( 'EA',   'application/xml+ea' ),
# 	'SA'   : ( '????', 'application/xml+sa' ),
# 	'AAX'  : ( '????', 'audio/vnd.audible.aax' ),
# 	'MP3'  : ( '????', 'audio/mpeg' ),
# 	'HAN'  : ( '????', 'application/json' ),
# 	'APG'  : ( '????', 'application/x-apg-zip' ),


import features


if hasattr(features, 'supported_formats'):
	features.supported_formats = [ k.upper() for k in features.supported_formats if k.upper() in CONTENT_TYPES ]
else:
	# default supported formats
	_SUPPORTED = [ 'MOBI', 'AZW', 'PRC', 'PDF' ]
	features.supported_formats = [ k for k in _SUPPORTED if k in CONTENT_TYPES ]
	del _SUPPORTED
logging.debug("supported formats: %s", features.supported_formats)


import formats.mobi as mobi
import formats.mbp as mbp


def handles(content_type):
	return content_type in ( CONTENT_TYPE_MOBIPOCKET, CONTENT_TYPE_PDF )

def read_cde_type(path, content_type, asin):
	if content_type == CONTENT_TYPE_MOBIPOCKET:
		return mobi.read_cde_type(path, asin)
	if content_type == CONTENT_TYPE_PDF:
		return 'PDOC'


import annotations

def sidecar(book, annotations_list = None):
	if book.content_type == CONTENT_TYPE_MOBIPOCKET:
		if not annotations_list:
			annotations_list = annotations.get_all(book.asin)
		return mbp.assemble_sidecar(book, annotations_list)
