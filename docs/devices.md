WARNING:
	KSP has only been tested on a Kindle 4 Non-Touch.
	It MAY work with Kindle 3 (aka Kindle Keyboard).
	It MAY work with Kindle Touch, but DO NOT follow the instructions here.


STEPS:

1. Jaibreak your Kindle
-----------------------

See [1] and [2] for details. You will need to enable ssh (dropbear) to log
into the device (as 'root').

[1] http://wiki.mobileread.com/wiki/Kindle4NTHacking
[2] http://yifan.lu/p/kindle-touch-jailbreak/

If you have software version 4.0, the login password is 'mario'. If you have
software version 4.0.1, in the tools/ folder you will find a python script to
generate the login password.


2. Get your Kindle certificate
------------------------------

The on-device file is '/var/local/java/prefs/certs/client.p12'. You will need
to copy it to the folder configured in etc/config.py ('certs_path').

If you'll be running under Python 3.3, you just need to rename 'client.p12' to
'*device-serial*.p12' where *device-serial* is the serial you find on the
device (the Settings page) without spaces.

If you'll be running KSP under Python 3.2, you will have to decrypt the PEM
file (the password is 'pass' -- not kidding):
	$ openssl pkcs12 -in client.p12 -nodes -out *device-serial*.pem

Either case, make sure '*device-serial*.pem' is reasonably secure (read-only,
and only readable by the user that will be running the KSP daemon).


3. Edit the Kindle API configuration
------------------------------------

The on-device file is /opt/amazon/ebook/config/ServerConfig.conf .

	Before modifying the file, MAKE A BACKUP!

Its contents should match config_device/ServerConfig.conf.original . See
config_device/ServerConfig.conf for a sample of what you should change (look
for '$SERVER_').

Before changing the file, you will have to re-mount the / filesystem as r/w:
	mntroot rw
After you're done with changing the file, don't forget to re-mount / as r/o:
	mntroot ro


4. Edit KSP configuration
-------------------------

In etc/config.py you are some variables you will need to modify:
	server_url
	calibre_library
Everything else is optional.

In etc/features.py are also some options you may want to tweak.
NOTE: 'register_devices' can be enabled from the KSP command line as well.


5. Start the KSP daemon
-----------------------

For the first run, don't forget to add --register-devices to the command line
(see etc/features.py for explanation). After you've registered your device(s),
the option is no longer needed.


6. Restart the device
---------------------

Menu button -> Settings, Menu button -> Restart

The first time the Kindle contacts KSP, the proxy will look for
'certs/*device_serial*.pem' to establish the device serial. After the device
has registered into KSP, you will have to do a manual sync (the first sync
just just a no-op, to establish the idenity of the device).

For trouble shooting, check the logs/server.log file to confirm the device has
properly registered.


And you should be good to go!
