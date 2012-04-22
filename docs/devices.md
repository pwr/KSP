Configuring the Kindle(s) to use KSP
====================================


WARNING
-------

KSP has only been tested on a **Kindle 4 (Non-Touch)**, software version **4.0.1**. Sorry, it's the only device I have
to test it with. The scripts have been tested only on a Kindle4NT; on other devices they will, in a best-case scenario,
not work.

KSP _may_ work with Kindle 3 (aka Kindle Keyboard). The configuration steps detailed here are most likely wrong, so **do
not** follow them. They also may be close enough, so if you know what you're doing the sections below might give you an
idea of what you need to do.

KSP _may_ also be made to work with Kindle Touch, but **do not** follow the instructions here -- they will almost
guarantee briking it. You'll have to do the configuration by hand, if configuring a Touch is possible at all.

If you have an usupported device, continue reading for details on what configuration changes are necessary. Maybe you'll
figure out what you need to do on your device. And if you do, please let me know :).


Scripted configuration
----------------------

The scripts in `tools/kindle4nt/ksp-config/` can be used to update the Kindle's internal configuration without the need
to SSH in. It *should* be safe, and if you break something, it *should* allow you to fix a broken configuration. But...
it works on my device. I can make no other guarantees.

In any case, if you _do_ have SSH enabled on your Kindle, and want to make the necessary changes yourself, you can just
skip to the next section.

To use the scripts, follow these steps:

1. Connect the Kindle to your machine with the USB cable.

2. Copy `tools/kindle4nt/data.tag.gz` and `tools/kindle4nt/ksp-config/*.sh` to the root of the mounted volume, next
    to the `documents` folder.

3. *Edit the `RUNME.sh` script*. In the first few lines of the script, there is an option you need to change,
    `SERVER_URL`. This is the url you've configured in `etc/config.py`, option `server_url`. If you don't change the
    script, it won't do much.

    NOTE: Windows users, please use a decent text editor (*not* Notepad) to edit the file. The script uses Unix line
    endings which are usually mangled by most Windows text editors, making it unusable on your Kindle.

4. Eject he Kindle volume, remove the USB cable, and restart the device.

    What the `RUNME.sh` script will do:

    * When the device boots, it will update the runtime java config
        (`/var/local/java/prefs/com.amazon.ebook.framework/ServerConfig`, contains overrides for the default values in
        `/opt/amazon/ebook/config/ServerConfig.conf`), adding customized entries for a few API urls, based on the
        value you've set in the `RUNME.sh` script for `SERVER_URL`.

    * Start a background task that waits for WiFi to come up (make sure you have WiFi enabled). It will then grab the
        HTTPS server's CA certificate and import it, if it is unknown to the Kindle. After the CA certificate is
        imported, the Java GUI will restart, so your device will look as if it's rebooting twice.

    * Make backups of all changed files :).

5. Connect the USB cable and mount the device.

6. In the device's root folder you should find a file named `_your_device_serial_.p12` -- it is your Kindle's SSL client
    certificate; copy it next to KSP's database file (in `db/`).

7. Eject the Kindle volume.

Your Kindle should now be talking to your KSP daemon instead of Amazon's services.

If it does not work, or if you just change your mind and want to go back to the original configuration, see the last
section of this file.

When you're done with the configuration on the Kindle, you should delete the `RUNME.sh` and `get_certificate.sh` scripts
from the device.


Configuration changes
---------------------

This section details the exact configuration changes needed on the Kindle device to make it talk to KSP. If you've
already followed the steps in the section above, you don't need to do anything else -- this section is for documentation
purposes only.

The Kindle internal software uses a few API urls to talk to Amazon. These are configured in the master configuration
file `/opt/amazon/ebook/config/ServerConfig.conf`, but its values are can be overriden by the properties file
`/var/local/java/prefs/com.amazon.ebook.framework/ServerConfig`. To have the Kindle talk to KSP instead of directly to
Amazon, you need to add a few lines in the second file (*don't change the master file*).

**NOTE**: Before changing the file on the device, **make a backup first!** You never know.

These four URLs are necessary to make KSP work. You'll *have* to add them, and point them to the KSP daemon's
`server_url`.

* `url.todo` (metadata sync) -- default `https://todo-g7g.amazon.com/FionaTodoListProxy`
* `url.cde` (content download) -- default `https://cde-g7g.amazon.com/FionaCDEServiceEngine`
* `url.firs` -- default `https://firs-g7g.amazon.com/FirsProxy`
* `url.firs.unauth` -- default `https://firs-ta-g7g.amazon.com/FirsProxy`

The changes involve replacing `https://_service_.amazon.com/` with the url of your KSP server, the one you've configured
in `etc/config.py`. More exactly, you will add 4 lines, like this:

    url.todo=https://_my_server_:_port_/KSP/FionaTodoListProxy
    url.cde=https://_my_server_:_port_/KSP/FionaCDEServiceEngine
    url.firs=https://_my_server_:_port_/KSP/FirsProxy
    url.firs.unauth=https://_my_server_:_port_/KSP/FirsProxy

The `/KSP/` part is optional, but makes it easier to filter and forward requests if you use an HTTPS frontend to
KSP. The port is also optional, if you use the default 443 port for HTTPS.

To apply these changes, restart your device. Or, if you're SSH'ed in, you can just kill the `cvm` process
(should be only one).

One more important thing: if your server's SSL certificate is not signed by a known CA authority, the Kindle will not be
able to talk to the KSP daemon. You will have to:

* Append your CA's certificate to `/etc/ssl/certs/ca-certificates.crt`, used by the daemon that does book downloads.
* Import it into the Java VM's certificate store, `/usr/java/lib/security/cacerts`. You need to use the `keytool`
    utility from a Java deployment on your machine -- the utility is *not* present on the device. Or, you can use the
    script `tools/ksp-config/keytool.sh` which provides a limited (but sufficient) sub-set of `keytool`'s functions.
* Restart the device.


Reverting the cofiguration
--------------------------

If something does not work, or if you just change your mind and want to go back to the original configuration, you just
need to revert the device's `ServerConfig` properties file to its original contents by removing the 4 lines you've
added. Technically you could also just remove the file, though it may contain additional configuration entries set-up by
Amazon.
