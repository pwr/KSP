Deployment and configuration
============================

KSP runs as a background daemon, listening on port `45350` by default.


Software requirements
---------------------

To run KSP, you will need:

1. [Python 3.2](http://python.org/download/)

     KSP has been tested with Python version 3.2.2.

2. Either [pyOpenSSL](http://pypi.python.org/pypi/pyOpenSSL), or the [openssl](http://www.openssl.org/) command-line
    utility accessible in the `PATH`.

    NOTE: If you're using pyOpenSSL, make sure you get the package matching your Python version and architecture (32 vs
    64 bits).


KSP configuration
-----------------

The configuration files are `etc/config.py` and `etc/features.py`.

There are three entries you **need** to modify in `etc/config.py`:

* `server_url`

    This is the base URL under which your Kindle will make its API calls, instead of `https://_service_.amazon.com/`.
    Usually this is `https://_machine_running_ksp_:_ksp_port_/KSP/`. If you want to use an HTTPS frontend to proxy the
    calls to KSP, it will be the its server url.

    The value of this option **must** be matched by the modifications you do on the device, in the `ServerConfig.conf`
    file (see `docs/devices.md`).

	WARNING: while technically you can use just HTTP for the `server_url`, IS IS VERY UNSECURE.
	Consider that the Kindle will be talking to the KSP server in plain text, over WiFi. Please read `docs/security.md`
	for details.

* `server_certificate`

	Path to the SSL server certificate.  You have to set this for HTTPS to work in KSP.

    The file must contain the server private key and server certificate. You cannot use a self-signed certificate, but
    you can create your own private CA and sign the server certificate with that. In this case, you will have to add
    your CA certificate to this file.

* `calibre_library`

    Path to your Calibre library, where its `metadata.db` file is, e.g. `~/calibre`, or `C:\\Calibre`.

Everything else is optional, though you might find some interesting stuff in `etc/features.py`.


Running KSP
-----------

Just run `main.py` in the KSP folder. You can call it with `--help` to see what arguments it accepts.

When running as a daemon, all output will go into `logs/server.log`. If DEBUG logging is active, the server log
should come in handy with troubleshooting.

Windows users can use the [AutoHotKey_L](http://www.autohotkey.com/download/) script at `tools/windows.ahk`, it will
give you a nice SysTray icon to start/stop KSP. For the AHK script to work, make sure you have `PYTHONHOME` set in your
environment.


Device registration
-------------------

The first time a new Kindle connects to KSP, it will trigger a "dummy" run of a couple of API calls, in order to find
the device's serial number (it is passed as a parameter by some of the API calls).

Based on the serial, KSP will look for a file named `_your_device_serial_.p12` in its `db/` folder (where the devices
database is kept) -- it expects to find there the Kindle's SSL client certificate, which it will try to load. If the
operation succeeds, KSP will register the device in its database, and you should be able to do a manual sync on the
Kindle to get the list of books available from the Calibre library.

For any device, you can at any point update the SSL client certificate by placing a new version of
`_your_device_serial_.p12` in the `db/` folder.

The entire processed should be easy to follow in the `logs/server.log` file, in case you need to do troubleshooting.
