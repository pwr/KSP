
KSP
===

KSP is a Kindle Store proxy that enhances the results returned by KS with books from a
[Calibre](http://calibre-ebook.com/) database. It integrates (as seamlessly as it can) the list of books present in
your Calibre library with the list of books the Amazon returns, allowing you to download books, from the Calibre
library to your device, as if they were on your Amazon account.

Additionally, it can do some automatic collections generation based on book series and tags, as configured in Calibre.

To work, KSP requires some changes to the Kindle's internal configuration, and a bit of work on managing the books in
your Calibre library.

**NOTE**: To use KSP, the Kindle device(s) **must be registered to your Amazon account**. KSP does not replace Amazon's
services, it only piggybacks on them, so if you do not have the device registered with your Amazon account, KSP cannot
help you.

**NOTE**: KSP has only been tested with the software it comes with (the standard Java GUI). I know there are possible
replacements for it (kite, coolreader3, other?), but it will most likely not work with them -- KSP relies on the
standard API calls the Kindle does to Amazon's services.


Security considerations
-----------------------

Modifying your internal Kindle configuration, and using it with KSP has certain security implications -- besides the
obvious loss of guarantee, violation of Amazon's Terms of Service, etc.

These security issues are vis-a-vis the communication between your device and KSP, between KSP and Amazon's services,
and the safety of your Amazon account.

*Please* read `docs/security.md` *before* considering using KSP.


It works on my machine
----------------------

... with my Kindle. Can't guarantee it will work on yours, with your Kindle. The configuration process may be a bit
long, configuring the Kindle(s) is longer and more error-prone. Caveat emptor.


Deployment
----------

Deployment is rather simple; configuration needs a bit of care, though you only have to do it once.

You should deploy, configure and start the KSP daemon first, along with the necessary HTTPS frontend. You can add new
devices at any point after that.

See `docs/install.md` for software requirements and deployment steps.


Using devices with KSP
----------------------

To use a Kindle device with KSP, you have to change some of its internal configuration. While jailbreaking the Kindle
for SSH access is not strictly necessary, it may help you troubleshoot if something goes wrong.

**WARNING**: KSP has only been tested with a Kindle 4 Non-Touch. It *may* work on other devices, but the configuration
can be tricky, you have to know what you are doing, and be careful. If you *do* make it work with other devices, please
let me know :).

See `docs/devices.md` for extended details.


Calibre library management
--------------------------

To have KSP use your Calibre books, you may have to work a bit on them. Specifically, the books need to have the proper
ASIN (book id) records, matching their Calibre uuid. It will certainly **not** work by just dropping MOBI files into
Calibre!

See `docs/library.md` for details.


But why... ?
------------

I'm a lazy bum, who does not like going to my PC and reaching for the USB cable everytime I want to put some more books
on the Kindle. Seriously.


Thanks
------

KSP and its additional tools have been made possible by the generous amounts of information available on the net about
how Kindles work.

In particular, the stuff on [MobileRead wiki](http://wiki.mobileread.com/wiki/Kindle4NTHacking) and various hacks found
by intreprid [MobileRead forums](http://www.mobileread.com/forums/forumdisplay.php?f=140) members, especially
[yifanlu](http://yifan.lu/p/kindle-touch-jailbreak/) and
[IxTab](http://www.mobileread.com/forums/showthread.php?p=1902438).

Thanks!
