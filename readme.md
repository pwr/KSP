
KSP
===

KSP is a Kindle Store proxy that enhances the results returned by KS with
books from a Calibre database. It integrates (as seamlessly as it can) the
list of books present in your Calibre library with the list of books the
Amazon returns, allowing you to download books to your device as if they were
on your Amazon account.

Additionally, it can do some automatic collections generation based on book
series and tags, as configured in Calibre.

To work, KSP requires some changes to the Kindle's internal configuration, and
a bit of work on managing the books in your Calibre library.

**NOTE**: To use KSP, the Kindle device(s) **must be registered to your Amazon
account**. KSP does not replace Amazon's services, it only piggybacks on them,
so if you do not have the device registered with your Amazon account, KSP
cannot help you.


Security considerations
-----------------------

Modifying your internal Kindle configuration, and using it with KSP has
certain security implications -- besides the obvious loss of guarantee,
violation of Amazon's Terms of Service, etc.

These security issues are vis-a-vis the communication between your device and
KSP, between KSP and Amazon's services, and the safety of your Amazon account.

*Please* read the [Security implications][docs/security.md] *before*
considering using KSP.


Deployment
----------

Deployment is rather simple; configuration needs a bit of care, though you
only have to do it once.

See docs/install.md for software requirements and deployment procedure.


Using devices with KSP
----------------------

To use a Kindle device with KSP, you have to change some of its internal
configuration.  While jailbreaking the Kindle is not strictly necessary, it
will help you troubleshoot if something goes wrong.

**WARNING**: KSP has only been tested with a Kindle 4 Non-Touch. It *may*
work on other devices, but the configuration can be tricky and you have to be
careful.

If you *do* make it work with other devices, please let me know.

See docs/devices.md for extended details.


Calibre library management
--------------------------

To have KSP use your Calibre books, you may have to work a bit on them.
Specifically, the books need to have the proper ASIN (book id) records,
matching their Calibre uuid.

It will certainly **not** work by just dropping MOBI files into Calibre!

See docs/library.md for details.


Thanks
------

KSP and its supplementary tools have been made possible by the generous
amounts of information available on the net about how Kindle work.

In particular, the stuff on [MobileRead wiki]
[http://wiki.mobileread.com/wiki/Kindle4NTHacking] and various hacks found by
intreprid [MobileRead forums]
[http://www.mobileread.com/forums/forumdisplay.php?f=140] members, too many of
them to list here.

Thanks!
