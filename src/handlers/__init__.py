# when importing this module/folder, actually import all classes in all modules in this folder

TODO = 'todo-g7g'
TODO_PATH = '/FionaTodoListProxy/'
CDE = 'cde-g7g'
CDE_PATH = '/FionaCDEServiceEngine/'
FIRS = 'firs-g7g'
FIRS_PATH = '/FirsProxy/'
FIRS_TA = 'firs-ta-g7g'
DET = 'det-g7g'
DET_PATH = '/DeviceEventProxy/'
DET_TA = 'det-ta-g7g'
DM = 'device-messaging-na'
DM_PATH = '/PostDeviceMessages?'
WWW = 'www'
#EMBER_PATH = '/gp/ember/xyml/'
#STORE_PATH = '/gp/g7g/xyml1/'

def is_uuid(text, cde_type = None):
	def is_hex(text):
		import string
		if not text:
			return True
		return text[0] in string.hexdigits and is_hex(text[1:])

	if not text:
		return False
	if len(text) == 36:
		# very unlikely not to be # is_hex(text.replace('-', ''))
		return cde_type in ('EBOK', None) and text[8] == '-' and text[13] == '-' and text[18] == '-' and text[23] == '-'
	if len(text) == 32:
		return cde_type in ('PDOC', None) and is_hex(text)
	# good enough
	return False

from .dummy import *
from .upstream import *
from .sync_metadata import *
from .get_items import *
from .remove_items import *
from .download_content import *
from .upload_snapshot import *
from .sidecar import *
from .collections import *
from .registration import *
#from .store import *
