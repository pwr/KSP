#!/bin/sh

#
# check for KSP setting, download and install SSL certificates if not already installed
#

if test -z "$1"; then
	echo "Use: $0 https://_server_[:_port_][/_path]"
	exit 1
fi
protocol=$(expr substr "$1" 1 8)
if test "$protocol" != "https://"; then
	echo "Protocol in url $1 is not 'https://', aborting."
	exit 1
fi

SERVER=$(expr substr "$1" 9 100)
if expr match "$SERVER" '.*/.*' >/dev/null; then
	# cut the path component from the url
	SERVER=$(expr match "$SERVER" '\([^/]*\)/.*')
fi
if expr match "$SERVER" '.*:.*' >/dev/null; then
	# split into name:port
	SERVER_NAME=$(expr match "$SERVER" '\(.*\):.*')
	SERVER_PORT=$(expr match "$SERVER" '.*:\(.*\)')
else
	SERVER_NAME=$SERVER
	SERVER_PORT=443
	SERVER="$SERVER:443"
fi
echo "Will check certificates from server [$SERVER], name [$SERVER_NAME], port [$SERVER_PORT]"

# we wait for WiFi to connect
WIFI=$(lipc-get-prop com.lab126.wifid cmState)
while test "$WIFI" != "CONNECTED"; do
	echo "Waiting for WiFi to connect."
	sleep 20
	WIFI=$(lipc-get-prop com.lab126.wifid cmState)
done
echo "WiFi connected"

T=/tmp/sslcert.$$
CURL_CA=/etc/ssl/certs/ca-certificates.crt
CACERTS=/usr/java/lib/security/cacerts

# first let's check if the cerfiticate is accepted
ssl_status=$(/usr/bin/openssl s_client -connect $SERVER -CAfile $CURL_CA </dev/null >$T 2>$T.err)
if grep -qe ":SSL23_GET_SERVER_HELLO:unknown protocol:" $T.err; then
	echo "Server $SERVER does not speak HTTPS? Aborting."
	cat $T.err
	rm -f $T $T.err
	exit 1
fi
if grep -qe "^    Verify return code: 0 (ok)" $T; then
	echo "Server certificate from $SERVER validated OK, nothing else to do."
	rm -f $T $T.err
	exit 0
fi
if grep -qe "^    Verify return code: 18 (self signed certificate)" $T; then
	echo "Server certificate from $SERVER is self-signed."
	echo "Server certificates HAVE to be signed by a CA to be imported. You will have to"
	echo "either get it signed by a recognized CA, or generate your own CA certiifcate"
	echo "and sign your server certificate with it."
	rm -f $T $T.err
	exit 1
fi
if grep -qe "^    Verify return code: 21 (unable to verify the first certificate)" $T; then
	echo "The server $SERVER did not provide a certificate for the CA it was signed with."
	echo "Cannot import, aborting."
	rm -f $T $T.err
	exit 1
fi

if grep -qe "^    Verify return code: 19 (self signed certificate in certificate chain)" $T; then
	echo Found untrusted CA, importing certificate:
	# we need to call it again to get the full certificate chain
	/usr/bin/openssl s_client -connect $SERVER -showcerts </dev/null >$T 2>$T.err
	sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/ p' $T >$T.pem
	# only keep the last certificate in the chain -- should be the CA one
	while test $(grep -ce '-BEGIN CERTIFICATE-' $T.pem) -gt "1"; do
		cat $T.pem | sed -e '1 d' | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/ p' >$T.pem
	done
	cat $T.pem

	mntroot rw

	# make a backup copy, just in case
	echo n | cp -ai $CURL_CA $CURL_CA.original 2>/dev/null
	# append the certificate
	echo -e "\n# Imported certificate for $SERVER by $0" >>$CURL_CA
	cat $T.pem >>$CURL_CA

	# make a backup copy, just in case
	echo n | cp -ai $CACERTS $CACERTS.original 2>/dev/null
	# import the certificate
	if $(dirname "$0")/keytool.sh -importcert -keystore $CACERTS -alias $SERVER -file $T.pem; then
		ca_imported=yes
	fi

	mntroot ro

	# restart the transfer daemon, so that it re-reads the certificates file
	lipc-set-prop com.lab126.pmond restart tmd
	# restart the java process, if we the import succeeded
	test -n "$ca_imported" && pkill -x cvm

	# if successful, don't leave this around, it should only do its job once
	rm -f $T $T.err $T.pem
	mv "$0" "$0.successful"
	exit 0
fi

echo "Found unknown certificate verification code, don't know what to do:"
cat $T
cat $T.err
rm -f $T $T.err
exit 1
