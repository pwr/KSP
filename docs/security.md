KSP: Security implications
==========================


The device client certificate
-----------------------------

Normally, Kindle devices talk to the Amazon services through HTTPS. Each
device has its own SSL client certificate; whithout the valid client
certificate (issued by Amazon for that Kindle device), Amazon will just refuse
connections.

For KSP to work, it has to use the indivitual device's client certificate to
connect to Amazon services, basically impersonating the device as far as
Amazon is concerned. This means KSP has to have a copy of the device's client
certificate.

KSP keeps that copy of the cerficate in its devices databasae (the file is
db/devices.sqlite). But whoever else gains access to the KSP database may read
your device's client certificate and use it to impersonate the device -- and
**access your Amazon account**. This means, potentially, not only access to
the books you've purchased, but also being able to make purchases if your
Amazon account has a Credit Card attached to it.

So if you use KSP, you **must** make sure its devices database is placed in a
secure location and, if possible, not accessible by anyone else other than the
KSP daemon.

On *NIX machines, you should ideally run KSP under its own account, and
have the devices database only accessible by that account.

On Windows machines... well.

Of course, this does not guarantee anything. If someone breaks into the
machine running KSP, they will most likely still be able to access the KSP
database file.


Kindle to KSP communication
---------------------------

While technically, you can use HTTP for the Kindle--KSP connection, doing so
is **very unsafe**.

Even if you only use your Kindle in your home, the WiFi connection can be
sniffed and highly sensitive information gathered from there -- including your
device client certificate, which is sent by Amazon in API calls dealing with
Kindle registration and de-registration.

Using HTTP with WiFi access points other than ones controlled by you (i.e.
your home WiFi) exposes this information not only to the owner of that WiFi
access point, but also whoever else may be listening on route to the machine
running KSP.

In conclusion, unless you live in the middle of nowhere, with no-one else in
range of your WiFi access point (hi C! :)), **use a HTTPS frontend server**.
Configuring a HTTPS server and updating the device to connect to it may be
complicated and troublesome, but it's certainly preferable to the alternative.
And you only have to do it once.

See docs/https_frontend.md for details.


KSP log files
-------------

The KSP log files (logs/server.log and logs/access.log) may contain sensitive
information related to the Kindle device(s) using it. As with the devices
database, you should make sure only the KSP daemon has access to it.

Also, you should not have DEBUG logging enabled unless you need to
troubleshoot the KSP daemon. Use the '--loglevel' option when running KSP
to only log INFO and WARNING messages.
