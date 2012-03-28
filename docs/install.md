Deployment and configuration
============================


Software requirements
---------------------

To run KSP, you will need:

1. [Python 3.2] [http://python.org/download/]
	KSP has been tested with Python 3.2.2 .
2. [pyOpenSSL] [http://pypi.python.org/pypi/pyOpenSSL]
	NOTE: Make sure you get the package matching your Python version and architecture (32 vs 64 bits).


KSP configuration
-----------------

The configuration files are etc/config.py and etc/features.py .

There are two entries you NEED to modify in etc/config.py:

* server_url:
	This is the base URL under which your Kindle will make its API calls, instead of [https://_service_.amazon.com/] .
	This value MUST be matched by the modifications you do on the device, in the ServerConfig.conf file.
	See docs/devices.md for more details.

* calibre_library:
	Path to your Calibre library, where the metadata.db file is.
	E.g. '/home/_user_/calibre', or 'C:\\Users\\_user_\\Documents\\Calibre'


Front-end HTTPS server
----------------------

It is **highly** recommended to have an HTTPS server in front of KSP, proxying
calls to the KSP daemon. For the reasons why, please read docs/security.md
(you should have done that already!).

For details on the HTTPS configuration and the changes you may need to do on
your Kindle device to make it work, see docs/https_frontend.md .


Running KSP
-----------

Just start main.py in the KSP folder.
You can call it with '--help' to see what arguments it accepts.

When runnig as a daemon, all output will go into logs/server.log . If DEBUG
logging is active, the server log will come in handy with troubleshooting.

Windows users can use the [AutoHotKey_L] [http://www.autohotkey.com/download/]
script at tools/windows.ahk, it will give you a nice SysTray icon to
start/stop KSP.

For the AHK script to work, make sure you have PYTHONPATH set in you environment.
