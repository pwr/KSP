Kindle for Android
==================


KSP has been tested with the Android application *Amazon Kindle* versions 3.3 to 3.6, though other versions may work
as well.

The *Amazon Kindle* application's settings can be modified with a helper application you'll find in
`tools/android/KSPConfig.apk` (on the device, the application's title should be *Kindle Configuration*).


Requirements
------------

  * Android version 2.3 (Gingerbread) or newer. *KSPConfig* has been tested with 2.3.3, 4.0.3 and 4.1.

  * The device must be *jailbroken*, and have the
    [Superuser](https://play.google.com/store/apps/details?id=com.noshufou.android.su) application installed. This is
    necessary because *KSPConfig* requires root access to be able to read and modify *Amazon Kindle*'s private
    configuration files.


Configuration
-------------

First, make sure you can install apps from non-Market sources (*Settings* -> *Security*). The application is signed
with my developer key.

*KSPConfig* requires two permissions: INTERNET to contact the KSP server, and KILL_BACKGROUND_PROCESSES to kill the
*Amazon Kindle* application if it is running. This is done to make sure it will load the updated configuration
when you start it again.

Install `KSPConfig.apk` to your device, and run it. It will require root access, and the first time you run it you
should get the *Superuser* prompt to allow it.

You can then change the service URL the Kindle app uses to talk to Amazon's services, and give it the `server_url`
you've configured in your KSP deployment. The app will check that the given URL actually points to a KSP deployment.

If you're using an HTTPS connection (which is higly recommented, especially considering *Amazon Kindle* will
talk to the KSP server over WiFi and/or 3G), *KSPConfig* will check if the server certificate is recognized by your
Android device, and if necessary, try to import it. This should work without problems in Android 4+ (Ice Cream
Sandwich), however it will most likely fail on older versions. In this case, you will have to use an HTTP connection.

Then you nedd to push the 'Apply changes' button to actually update *Amazon Kindle*'s configuration files.

If you want to go back to Amazon's standard services with *Amazon Kindle*, just push the 'Use default service'
button and 'Apply'.
