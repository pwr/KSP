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
DM_PATH = '/PostDeviceMessages'
WWW = 'www'
#EMBER_PATH = '/gp/ember/xyml/'
#STORE_PATH = '/gp/g7g/xyml1/'

def is_uuid(text):
	if not text or len(text) != 36:
		return False
	if text[8] != '-' or text[13] != '-' or text[18] != '-' or text[23] != '-':
		return False
	# good enough
	return True

from .dummy import *
from .upstream import *
from .sync_metadata import *
from .get_items import *
from .remove_items import *
from .download_content import *
from .upload_snapshot import *
from .sidecar import *
from .collections import *
#from .store import *
