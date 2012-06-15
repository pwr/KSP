Kindlet-Loader
==============


KL allows selectively loading Kindlets outside of the normal sandbox. With it you can launch unsigned kindlets, and
permit them full access to the filesystem and Java framework.


Supported devices
-----------------

Right now KL only works on the Kindle 4, software version 4.1.0.  It was compiled against the Kindlet API version 1.3.

It can most likely be ported to the Kindle 3 and Kindle Touch, but at the moment I don't have access to their Java
libraries to do the porting.

Do not try to install this KL version to an unsupported software version. At best, it will not work. At worst, you may
have to unbrick your Kindle afterwards.


Requirements
------------

You need to have SSH access into your Kindle.


How it works
------------

KL implements a custom classloader for the kindlets, skipping all the sandboxing checks: certificates, java permissions
and class whitelisting.

After you've installed the KL, when launching a Kindlet for the first time, you will get a dialog asking if you want to
allow it full permissions (using the custom classloader) or load it normally (inside the regular Kindlet API sandbox).

If you load it with full permissions:

  - the certificate checks will not be performed; so the kindlet can be signed with a developer key, or not signed at
	all, it does not matter; you will not need to install any developer certificates.

  - the kindlet will have full access to the device's filesystem, not just inside the regular sandbox -- it will be able
  to  read and write any file.

  - the kindlet will have full access to the Java framework's classes, not just to the Kindlet API. This is not as
  useful as it may sound, as the Kindle Java framework is heavily obfuscated, in a manner that makes some parts of the
  API unaccessible for development (but still fully functional). The parts that _are_ accessible are very hard to
  read and comprehend.

If you _do_ allow full permissions to a kindlet, it will most likely fail to load the first time. Just start it again
and it will be running with full permissions.

KL keeps a database in `/mnt/us/system/kindlets-whitelist.txt` with kindlets that are allowed full permissions, so you
will only be asked once for each kindlet you launch. You can change the file at any time, or delete it altogether.


Installing
----------

SSH into your device. Mount the root partition read-write (`mntroot rw`).

Copy `out/@unsigned-kindlets-loader-410.jar` to the device, in the folder `/opt/amazon/ebook/lib`. Make sure to keep
the file name as-is; the `@` at the beginning of the name ensures the custom classloader is seen first by the Java
framework.

Re-mount the root partition read-only (`mntroot ro`). Restart the Java framework:

	/etc/init.d/framework restart

Enjoy! :)


Un-installing
-------------

SSH into your device. Mount the root partition read-write (`mntroot rw`).

Remove the file `@unsigned-kindlets-loader-410.jar` from `/opt/amazon/ebook/lib`.

Re-mount the root partition read-only (`mntroot ro`), and restart the Java framwork.
