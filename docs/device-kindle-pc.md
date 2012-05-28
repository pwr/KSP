Kindle for PC
=============


KSP has been tested with Kindle for PC versions 1.9+, though the configuration steps detailed below *may* work with
other versions as well.

The Kindle for PC configuration resides in the file `%LOCALAPPDATA%\Amazon\Kindle\storage\.kinf2011`. Unfortunately it
is heavily crypted and obfuscated, so you can't mess with it directly.


Configuration
-------------

This method has been tested with Kindle for PC versions 1.9+.

Before starting, you should make a backup of the `.kinf2011` configuration file -- in case something goes wrong, you can
just stop K4PC, restore the file from backup, and restart it again.

You will need to install an HTTPS proxy, on the machine that will be running Kindle for PC. I've used
[Fiddler 2](http://www.fiddler2.com/fiddler2), and the following steps are Fiddler-specific. However, any HTTPS proxy
capable of editing responses should work.

 1. Configure Fiddler to decrypt HTTPS traffic: Tools -> Fiddler Options -> HTTPS. Check 'Capture HTTPS CONNECTs' and
    'Decrypt HTTPS traffic'.

    Fiddler should now ask you if you want to import its custom CA certificate into Windows' certificate store. This is
    necessary to allow Fiddler to act as a man-in-the-middle in the HTTPS conversation between K4PC and Amazon's
    services, and will allow you to view and modify the responses Amazon gives to K4PC.

 2. If you've configured KSP with an `https://` url, with your custom CA, you will need to import it into Windows'
    certificate store: in Fiddler, Tools -> WinINET Options -> Content, and click the 'Certificates' button. Click
    'Import', select your CA certificate, and import it into the 'Trusted Root Certification Authorities' store.

 3. Start K4PC, and enable the HTTPS proxy: Tools -> Options -> Network -> Manual proxy configuration. Set
    'HTTP Proxy' to `127.0.0.1`, and 'Port' to `8888`.

    Restart K4PC (tends to behave a bit wonky right after you've changed its Network settings), and sync (F5). In
    Fiddler, you should see requests to `todo-ta-g7g.amazon.com` and `cde-ta-g7g.amazon.com`, and you should be able to
    see the request and respose bodies in the 'Inspectors' tab at the right. Make sure the proxy works (all responses
    should have status 200) before going further.

 4. On the right side, switch to the 'Autoresponder' tab. On the left side, look for a request to
    `FionaTodoListProxy/getItems`, and drag it to the right side. You then should have an entry like this:

    If URI matches... `EXACT:https://todo-ta-g7g.amazon.com/FionaTodoListProxy/getItems` then respond with...
    `*200-SESSION-<number>`.

    Disable it (checkbox at its left), in case K4PC makes more requests while you edit the response.

 5. Right click the entry in 'Autoresponder', select 'Edit response', and switch to the TextView tab. Replace whatever
    text is there with the code below:

    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <response>
        <total_count>1</total_count>
        <next_pull_time>...</next_pull_time>
        <items>
            <item action="SET" type="SCFG" key="KSP.set.scfg" priority="60" is_incremental="false"
                sequence="0">url.todo=_SERVER_URL_</item>
        </items>
    </response>
    ```

    You *must* replace `_SERVER_URL_` with the value of KSP's `server_url`; just the base url, you *must not* include
    `/FionaTodoListProxy` as for the Kindle 4.

    Save the edited response, and enabled the autoresponder for this request (checkbox to its left).

 6. In K4PC, sync (F5). Fiddler should reply to its `getItems` request with the response you've edited. After the request
    has been replied once, disable it in the 'Autoresponder' tab.

 7. Disable the proxy in K4PC, and restart it.

At this point, K4PC should be talking with your KSP server, and should have been registered automatically.


Book covers
-----------

K4PC tries to download book covers from one of Amazon's servers (`ecx.images-amazon.com`). For books from Calibre's
library, provided by KSP, it will not find those covers. Though this is not exactly a necessary feature, K4PC can be
tricked to get the book covers from KSP.

First, you will need to set-up an HTTP server (I've used Apache, any other should work), and modify your Windows' hosts
file (`%windir%\system32\drivers\etc\hosts`) to point `ecx.images-amazon.com` to the HTTP server's IP, by adding a new
line like this:

    <your HTTP server's IP> ecx.images-amazon.com

This will have the unfortunate side-effect of breaking *all* Amazon images (including when browsing the site), so we
have to fix that.

In your HTTP server's configuration, add a couple of Rewrite rules (this configuration is for Apache, if you use another
HTTP server you should look into its documentation for an equivalent):

    RewriteEngine on
    RewriteCond %{HTTP_HOST} ecx.images-amazon.com
    RewriteRule ^/images/P/[-a-f0-9]{36}\.01\._SX..._SY..._SCLZZZZZZZ_\.jpg$ _your_KSP_server_url_$0 [R=302,NC]
    RewriteCond %{HTTP_HOST} ecx.images-amazon.com
    RewriteRule ^/.*$ http://z-ecx.images-amazon.com$0 [R=302]

The first rule matches requests for book covers, for books provided by KSP (identified by having their ID in the form of
a UUID), and redirects them to KSP's image handler, which will return the book cover from Calibre. Make sure to replace
`_your_KSP_server_url_` with KSP's `server_url`, without any trailing slashes.

The second rule matches all other requests to `ecx.images-amazon.com`, and redirects them to `z-ecx.images-amazon.com`,
which appears to be an equivalent to `ecx`.


Reverting the cofiguration
--------------------------

Stop Kindle for PC, and remove the file `%LOCALAPPDATA%\Amazon\Kindle\storage\.kinf2011`. A side effect is that you will
lose *all* its configuration, so when you start Kindle for PC again, you will have to re-register it.
