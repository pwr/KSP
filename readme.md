
KSP
===

KSP is a Kindle Store proxy that enhances the results returned by KS with
books from a Calibre database. It integrates the list of books present in your
Calibre library with the list of books the Amazon returns, allowing you to
download books from the device as if they were on your Amazon account.

Additionally, it can do some automatic collections generation based on book
series and tags, as configured in Calibre.

To work, KSP requires some changes to the Kindle's internal configuration, and
a bit of work on managing the books in your Calibre library.


Security considerations
-----------------------

Modifying your Kindle and using it with KSP has some security implications,
vis-a-vis its communication with Amazon's Kindle Store service.

Please read docs/security.md before considering using KSP.


Deployment
----------

Deployment is rather simple; configuration needs a bit of care, though you
only have to do it once.

See docs/install.md for software requirements and deployment procedure.


Using devices with KSP
----------------------

To use a Kindle device with KSP, you have to change some of its internal
configuration.  While jailbreaking the Kindle is not strictly necessary,
it will help you troubleshoot if something goes wrong.

**WARNING**: KSP has only been tested with a Kindle 4 Non-Touch. It *may*
work on other devices, but the configuration can be tricky and you have to be
careful.

If you do make it work with other devices, please let me know.

See docs/devices.md for extended details.


Calibre library management
--------------------------

To have KSP use your Calibre books, you may have to work a bit on them.
Specifically, the books need to have the proper ASIN (book id) records,
matching their Calibre uuid.

It will certainly **not** work by just dropping MOBI files into Calibre!

See docs/library.md for details.
