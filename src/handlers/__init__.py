# when importing this module/folder, actually import all classes in all modules in this folder

def is_uuid(text, cde_type = None):
	def is_hex(text):
		if not text:
			return True
		# calibre ids use only lower-case for uuids
		return text[0] in '0123456789abcdef' and is_hex(text[1:])

	if not text:
		return False
	if len(text) == 36:
		# very unlikely not to be # is_hex(text.replace('-', ''))
		return cde_type in ('EBOK', None) and text[8] == '-' and text[13] == '-' and text[18] == '-' and text[23] == '-'
	if len(text) == 32:
		return cde_type in ('PDOC', None) and is_hex(text)
	# good enough
	return False


TODO = 'todo-g7g'
TODO_PATH = '/FionaTodoListProxy/'
CDE = 'cde-g7g'
CDE_PATH = '/FionaCDEServiceEngine/'
FIRS = 'firs-g7g'
FIRS_PATH = '/FirsProxy/'
FIRS_TA = 'firs-ta-g7g'
#WWW = 'www'
#EMBER_PATH = '/gp/ember/xyml/'
#STORE_PATH = '/gp/g7g/xyml1/'


_handlers = []
def register(h):
	_handlers.append(h)
def match(r):
	for h in _handlers:
		if h.accept(r):
			return r


# the order here is the order in which handlers are matched when processing a request
from .ksp import *
from .sync_metadata import *
from .get_items import *
from .remove_items import *
from .download_content import *
from .upload_snapshot import *
from .sidecar import *
from .page_numbers import *
from .get_annotations import *
from .collections import *
from .registration import *
#from .store import *
