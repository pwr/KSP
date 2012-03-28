Configuring Kindle(s) to use KSP
================================


WARNING
-------

KSP has only been tested on a **Kindle 4 (Non-Touch)**, software version
**4.0.1**. Sorry, it's the only device I have to test it with.

KSP _may_ work with Kindle 3 (aka Kindle Keyboard). The configuration steps
detailed here are most likely wrong, so **do not** follow them.

KSP _may_ also be made to work with Kindle Touch, but **do not** follow the
instructions here -- they will almost guarantee briking it. You'll have to do
the configuration by hand, if configuring a Touch is possible at all.

If you have an usupported device, continue reading for details on what
configuration changes are necessary.  Maybe you'll figure out what you need to
do on your device. And if you do, please let me know :).


SSH access
----------

While SSH access into your Kindle 4 Non-Touch (again, no other Kindle is
supported!) is not strictly necessary to make the configuration changes, it
may help to ensure the proper changes have been made and troubleshoot possible
problems. If you don't have SSH enabled on your Kindle, and don't want to
bother with it, just skip to the next section.

If you do not have SSH enabled, you can use the script in
tools/kindle4nt/enable-ssh as such:

1. connect the Kindle with the USB cable to your machine
2. copy tools/kindle4nt/data.tar.gz and tools/kindle4nt/enable-ssh/RUNME.sh
to the root of the mounted volume, next to the 'documents' folder

Eject the Kindle volume, and restart the device: [MENU] -> _Settings_ ->
[MENU] -> _Restart_.

When the device finishes restarting and shows up again as a disk, you should
see a RUNME.log file. Look into it to see the results. You should see:

``````````````````````````````````````````
Copying SSH binaries to the main partition
Adding firewall rule for SSH over WiFi
``````````````````````````````````````````

This means you can eject the volume, and should be able to connect with SSH to
the Kindle's WiFi IP. The username is 'root', and the password should be either
'mario' (if you have software version 4.0) or 'fionaXXXX', where the XXXX part
depends on your device serial. Use the tools/gen_pw.py script to compute it.

NOTE: Some users report sometimes the device does not restart properly -- i.e.
does not run the whole boot sequence. If you do not see the RUNME.log file,
restart it again -- it should show up this time.


Scripted configuration
----------------------

In the tools/kindle4nt/ksp-config folder is a scripts you can use to update
the Kindle's internal configuration without the need to SSH in.

It *should* be safe, and if you break something, it *should* allow you to
fix a broken configuration. But... it works on my machine. I can make no other
guarantees.

In any case, if you _do_ have SSH enabled on your Kindle, and want to make
the necessary changes yourself, you can just skip to the next section.

To use it, follow these steps:

1. connect the Kindle to your machine with the USB cable
2. copy tools/kindle4nt/data.tag.gz and tools/kindle4nt/ksp-config/RUNME.sh
to the root of the mounted volume, next to the 'documents' folder
3. create a folder named 'KSP' (mind the capitals) next to the 'documents' folder
4. eject he Kindle volume and restart the device

After the Kindle restarts, you should have in the 'KSP' folder a copy of your
original 'ServerConfig.conf' file, named 'ServerConfig.conf.original' (a copy
of it was made on the device as well).

5. make a copy of 'ServerConfig.conf.original' on your machine -- just in case
6. rename 'ServerConfig.conf.original' to 'ServerConfig.conf'
7. edit 'ServerConfig.conf' as detailed in the next section

In the 'KSP' folder should also be a file named '_your_device_serial_.p12'.
It is your Kindle's SSL client certificate.

8. copy '_your_device_serial_.p12' next to KSP's database file (in db/)
9. eject he Kindle volume and restart the device

Your Kindle should now be talking to your HTTPS frontend instead of Amazon's
services, at least for the urls you've changed.

If it does not work, or if you just change your mind and want to go back
to the original configuration, see the last section of this file.

NOTE: If the 'KSP' folder exists on the device, the RUNME.sh script will
always place there the files 'ServerConfig.conf.original' and
'_your_device_serial_.p12'. Any 'ServerConfig.conf' file found there will
replace the device's configuration.


Configuration changes
---------------------

The Kindle internal software uses a few API urls to talk to Amazon. These are
configured in the file /opt/amazon/ebook/config/ServerConfig.conf (on the
device, obviously).

To have the Kindle talk to KSP instead of directly to Amazon, you need to
change the urls in that file.

**NOTE**: if you're changing the file directly on the device, through SSH,
**make a backup first**! You never know.

**NOTE**: if you're changing the file directly on the device, through SSH,
you'll have to make the root partition writable first (by default, it is
mounted as read-only -- no need to write to it during Kindle's normal
functioning). The command is 'mntroot rw'. When you're done, re-mount it
as read-only with 'mntroot ro'.

These two are the only ones stritcly necessary to make KSP work. You'll *have*
to change them, and point them to the KSP front-end HTTPS server.

* 'url.todo' (metadata sync) -- standard value 'https://todo-g7g.amazon.com/FionaTodoListProxy'
* 'url.cde' (content download) -- standard value 'https://cde-g7g.amazon.com/FionaCDEServiceEngine'

These two are used when registering and de-registering a device. If you don't
plan on doing that while using KSP, there is no need to change them.

* 'url.firs' -- standard value 'https://firs-g7g.amazon.com/FirsProxy'
* 'url.firs.unauth' -- standard value 'https://firs-ta-g7g.amazon.com/FirsProxy'

These three are used to upload device logs to Amazon. If you point these to
KSP, and disable the 'allow_logs_upload' setting in etc/features.py, these
logs *should* no longer reach Amazon. Entirely optional, functionality-wise.

* 'url.det' -- standard value 'https://det-g7g.amazon.com/DeviceEventProxy'
* 'url.det.unauth' -- standard value 'https://det-ta-g7g.amazon.com/DeviceEventProxy'
* 'url.messaging.post' -- standard value 'https://device-messaging-na.amazon.com'

The changes involve replacing 'https://_service_.amazon.com/' with the url of your
frontend HTTPS server, 'https://_my_server_/KSP'.

For example, you will have:

``````````````````````````````````````````````````````
url.todo=https://_my_server_/KSP/FionaTodoListProxy
url.cde=https://_my_server_/KSP/FionaCDEServiceEngine
``````````````````````````````````````````````````````

etc. The /KSP/ part is optional, but will make it easier to filter and forward
requests from the HTTPS frontend to the KSP daemon.

Then you must edit etc/config.py and set 'server_url':

``````````````````````````````````````
server_url = 'https://_my_server_/KSP'
``````````````````````````````````````

To apply the changes you've made to ServerConfig.conf, restart your device.
Or, if you're SSH'ed in, you can just kill the java process (should be only
one).

Additional configuration may be required to convince the Kindle to talk to
your HTTPS frontend. See [HTTPS frontend] [docs/https_frontend.md] for details.


Reverting the cofiguration
--------------------------

If it does not work, or if you just change your mind and want to go back
to the original configuration, you just need to replace the device's
'ServerConfig.conf' file with the original version and restart.

You can use the configuration script from the Scripted configuration
section. Just copy 'ServerConfig.conf.original' to the
'KSP' folder on the Kindle, rename it as 'ServerConfig.conf', and restart
the device.
