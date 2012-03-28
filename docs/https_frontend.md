Configuring an HTTPS frontend for KSP
=====================================


Rationale
---------

Normally, the Kindle talking to the Amazon services looks like this:

    Kindle <--HTTPS-over-WiFi--> Amazon

Just putting KSP in between them, you'd have this:

    Kindle <--HTTP-over-WiFi--> KSP <--HTTPS--> Amazon

Just having `HTTP` between the Kindle and KSP may is unwise; having `HTTP-over-WiFi` is downright dangerous. The
solution is to add an HTTPS frontend to KSP, as such:

    Kindle <--HTTPS-over-WiFi--> HTTPS frontend <--HTTP--> KSP <--HTTPS--> Amazon

Now, the sensitive connection over WiFi between the Kindle and the frontend is secure as well. (The `HTTP` between the
HTTPS frontend and KSP is still a problem, though a much smaller one; I'm working on fixing it).


HTTP frontend configuration
---------------------------

You can use any standard http server for the frontend: Apache, nginx, etc, as long as it forwards connections to your
KSP daemon. The configuration for Apache looks like this:

    LoadModule proxy_module modules/mod_proxy.so
    LoadModule proxy_http_module modules/mod_proxy_http.so

    <Location /KSP/>
        SSLRequireSSL
        ProxyPass http://_ksp_server_:45350/KSP/
        ProxyPassReverse http://_ksp_server_:45350/KSP/
    </Location>

where _ksp_server_ is the machine where your KSP daemon is running. *Ideally*, it should be the same machine as the one
your frontend runs on:

    LoadModule proxy_module modules/mod_proxy.so
    LoadModule proxy_http_module modules/mod_proxy_http.so

    <Location /KSP/>
        SSLRequireSSL
        ProxyPass http://127.0.0.1:45350/KSP/
        ProxyPassReverse http://127.0.0.1:45350/KSP/
    </Location>

The `SSLRequireSSL` is important -- you only want to accept HTTPS connections on your `/KSP/` path.


Self-signed SSL certificates
----------------------------

One "small" problem appears when you're using a self-signed certificate for your HTTPS frontend -- the Kindle will
refuse to talk to it. The reason being, the Kindle has a (pretty large) list of known certificate issuers -- and
you're not on it. The solution is to add your CA certificate to Kindle's list of approved certificate issuers.

The files in question are:

* `/usr/java/lib/security/cacerts` -- Java keystore, used by the Java GUI process for API calls

* `etc/ssl/certs/ca-certificates.crt` -- plain-text list of certificates, used by `curl` to download the actual book
    files (when downloading books, the `tmd` daemon spawns `curl` instances to do the actual work -- no point in keeping
    the Java GUI busy with downloads)

**WARNING**: keep backup copies of any files you (intend to) modify.

You will need to:

* import your CA `cert.pem` into the Java keystore (`/usr/java/lib/security/cacerts`)

    This cannot be done on the device -- its Java deployment lacks the `keytool` utility to manage keystore files. So
    you have to copy this file to your machine, use the `keytool` utility from *your* deployment of Java (JRE or JDK,
    any version) to import your CA `cert.pem` into it, then copy it back and restart the device.

    The command to do the import is:

        keytool.exe -importcert -alias _cert_alias_ -keystore cacerts -file CAcert.pem -storepass changeit

    where `_cert_alias_` is a name under which the certificate will be kept in the keystore (the name of your HTTPS
    frontend server will do just fine), `cacerts` is the Java keystore, `CAcert.pem` is your CA certificate file, and
    `changeit` is the actual keystore password :).

* append the contents of you CA certificate (in PEM format!) to `curl`'s list of approved CAs
    (`etc/ssl/certs/ca-certificates.crt`)

And then you should be good to go.


(Semi-)Scripted configuration
-----------------------------

You can use the `tools/kindle4nt/ksp-config/RUNME.sh` script to automate this process somewhat:

1. connect the Kindle to your machine with the USB cable

2. copy `tools/kindle4nt/data.tag.gz` and `tools/kindle4nt/ksp-config/RUNME.sh` to the root of the mounted volume, next
    to the `documents` folder

3. create a folder named `KSP` (mind the capitals) next to the `documents` folder

4. eject he Kindle volume and restart the device

    After the Kindle restarts, you should have in the `KSP` folder, among other files, copies of those two certificate
    dumps mentioned earlier. Copies have been made on the device as well, just in case.

5. rename `cacerts.original` to `cacerts`

6. copy your CA certificate in the `KSP` folder, name it `CAcert.pem` (the name is important)

7. run the keystore command mentioned earlier

8. eject the Kindle volume, and restart the device

The `RUNME.sh` script should now copy your updated `cacerts` over the standard one, and append the contents of
`CAcert.pem` to `curl`'s list of approved certificates. Look at the `RUNME.log` file on the device to see the results of
the script's last run.

And you should be good to go. After you've confirmed the Kindle connects properly to your HTTPS frontend, and then the
requests reach your KSP daemon, you can delete the `RUNME.sh` script and `KSP` folder from the device.

(In the future, if time permits, I'll look into making a small Java utility to do the import on-device, without having
to run `keytool` on your machine.)
