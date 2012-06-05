Kindle for Android
==================


KSP has been tested with *Kindle for Android* versions 3.3, 3.4 and 3.5, though other versions may work as well.

The *Kindle for Android* application's settings can be modified with a helper application you'll find in
`tools/android/KSPConfig.apk`.


Requirements
------------

  * Android version 2.3 (Gingerbread) or newer. *KSPConfig* has been tested with 2.3.3 and 4.0.3.

  * The device must be *jailbroken*, and have the
    [Superuser](https://play.google.com/store/apps/details?id=com.noshufou.android.su) application installed. This is
    necessary because *KSPConfig* requires root access to be able to read and modify *Kindle for Android*'s private
    configuration files.


Configuration
-------------

First, make sure you have enabled installing apps from non-Market sources (*Settings* -> *Security*). The *KSPConfig*
application is signed with my developer key.

*KSPConfig* requires two permissions: INTERNET to contact the KSP server, and KILL_BACKGROUND_PROCESSES to kill the
*Kindle for Android* application if it is running. This is done to make sure it will load the updated configuration
when you start it again.

Install `KSPConfig.apk` to your device, and run it. It will require root access, and the first time you run it you
should get the *Superuser* prompt to allow it.

You can then change the service URL the Kindle app uses to talk to Amazon's services, and give it the `server_url`
you've configured in your KSP deployment. The app will check that the given URL actually points to a KSP deployment.

If you're using an HTTPS connection (which is higly recommented, especially considering *Kindle for Android* will
talk to the KSP server over WiFi), *KSPConfig* will check if the server certificate is recognized by your Android
device, and if necessary, try to import it. This should work without problems in Android 4+ (Ice Cream Sandwich),
however it will most likely fail on older versions. In this case, you will have to use an HTTP connection.

Then you nedd to push the 'Apply changes' button to actually update *Kindle for Android*'s configuration files.

If you want to using Amazon's standard services with *Kindle for Android*, just push the 'Use default service'
button and 'Apply'.
