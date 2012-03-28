Deployment and configuration
============================

KSP runs as a background daemon, listening on port `45350` by default.


Software requirements
---------------------

To run KSP, you will need:

1. [Python 3.2](http://python.org/download/)

     KSP has been tested with Python version 3.2.2.

2. [pyOpenSSL](http://pypi.python.org/pypi/pyOpenSSL)

     NOTE: Make sure you get the package matching your Python version and architecture (32 vs 64 bits).


HTTPS frontend
--------------

It is **highly** recommended to have an HTTPS server in front of KSP, proxying calls to the KSP daemon. For the reasons
why, *please* read `docs/security.md` -- though you should have done that already!

For details on the HTTPS configuration and the changes you may need to do on your Kindle device to make it work, see
`docs/https_frontend.md`.

The main end result of that configuration is the new base URL the Kindle will connect to, instead of Amazon's services.
You'll use it in the configuration below.


KSP configuration
-----------------

The configuration files are `etc/config.py` and `etc/features.py`.

There are two entries you **need** to modify in `etc/config.py`:

* `server_url`

    This is the base URL under which your Kindle will make its API calls, instead of `https://_service_.amazon.com/`.
    This value **must** be matched by the modifications you do on the device, in the `ServerConfig.conf`
    file (see `docs/devices.md`).

* `calibre_library`

    Path to your Calibre library, where its metadata.db file is, e.g. `/home/_user_/calibre`, or
    `C:\\Users\\_user_\\Documents\\Calibre`.

Everything else is optional, though you might find some interesting options in etc/features.py.


Running KSP
-----------

Just start main.py in the KSP folder. You can call it with `--help` to see what arguments it accepts.

When runnig as a daemon, all output will go into `logs/server.log`. If DEBUG logging is active, the server log will
come in handy with troubleshooting.

Windows users can use the [AutoHotKey_L](http://www.autohotkey.com/download/) script at `tools/windows.ahk`, it will
give you a nice SysTray icon to start/stop KSP. For the AHK script to work, make sure you have PYTHONHOME set in you
environment.
