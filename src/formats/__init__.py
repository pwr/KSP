import formats.mobi as mobi

def handles(content_type):
	return content_type in [ 'application/x-mobipocket-ebook', 'application/pdf' ]

def read_cde_type(path, content_type, asin):
	if content_type == 'application/x-mobipocket-ebook':
		return mobi.read_cde_type(path, asin)
	if content_type == 'application/pdf':
		return 'PDOC'
	return None
