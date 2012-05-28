Kindle for Android
==================


KSP has been tested with Kindle for Android versions 3.3, 3.4 and 3.5, though other versions may work as well.

The Kindle for Android application's settings can be modified with a helper application you'll find in
'tools/android/KSPConfig.apk'.


Requirements
------------

  * Android version 2.3 (Gingerbread) or newer. KSPConfig has been tested with 2.3.3 and 4.0.3.

  * The device must be *jailbroken*, and have the
    [Superuser](https://play.google.com/store/apps/details?id=com.noshufou.android.su) application installed. This is
    necessary because KSPConfig requires root access to be able to read and modify Kindle for Android's configuration.


Configuration
-------------

First, make sure you have enabled installing apps from non-Market sources (Settings -> Security). The KSPConfig app is
signed with my developer key.

Install KSPConfig.apk to your device, and run it. It will require root access, and the first time you run it you should
get the Superuser prompt to allow it.

You can then change the base URL the Kindle app uses to talk to Amazon's services, and give it the `server_url` you've
configured in your KSP deployment. The app will check that the given url actually points to a KSP deployment, and then
you have to push the 'Apply configuration' button.

If you change your mind and want to go back to Amazon's service, use the 'Reset configuration' button.


Caveats
-------

While using https to talk to KSP is highly recommended (especially as the Kindle for Android app will talk to KSP over
WiFi), it may be difficult to convince your Android device to talk to your KSP server if you're using a self-signed
certificate. On Android 4+ (Ice Cream Sandwich), you can just copy the CA certificate to the SD card and then install
it from Settings -> Security. I have not managed to do that on older versions; if you do, please let me know how.
