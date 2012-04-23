import calibre.db as _db
import calibre


def _collections(asin_mappings):
	collections = {}
	for name, asin_list in asin_mappings.items():
		books_list = [ calibre.book(asin) for asin in asin_list ]
		books_list = [ b for b in books_list if b ]
		books_with_files = [ b for b in books_list if b.file_path ]
		if books_with_files: # if at least _some_ books in the collection have files
			collections[name] = books_list
	return collections

def series():
	return _collections(_db.load_series_collections())

def tags():
	return _collections(_db.load_tag_collections())
