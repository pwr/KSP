#!/bin/sh

##########################################
# YOU HAVE TO SET THIS TO THE SERVER URL #
##########################################
# e.g.
# SERVER_URL=https://_server_name_:_server_port_/KSP
# where _server_port_ is optional and defaults to 443
# this is the value that you set in etc/config.py
SERVER_URL=NOT_SET
##########################################

###########################################
# NO USER SERVICEABLE PARTS BELOW THIS LINE

serial=$(cat /proc/usid)
echo Copying client.p12 to /mnt/us/$serial.p12
cp -af /var/local/java/prefs/certs/client.p12 /mnt/us/$serial.p12

if test "$SERVER_URL" == "NOT_SET"; then
	echo "You must set SERVER_URL in the script $0!"
	echo "Aborting."
	exit 1
fi

protocol=$(expr substr "$1" 1 8)
if test "$protocol" == "https://"; then
	GC=$(dirname "$0")/get_certificates.sh
	if ! test -r "$GC"; then
		echo "You've configured a https SERVER_URL ($SERVER_URL), but I could not find the script to update CA certificates ($GC)."
		echo "Aborting."
		exit 1
	fi
fi

# update the API urls
SC=/var/local/java/prefs/com.amazon.ebook.framework/ServerConfig

if grep -q url.todo= $SC 2>/dev/null; then
	echo "== url.todo already configured in $SC:"
	grep url.todo= $SC
	echo "If you're sure about changing it, delete the line from the configuration file and run this script again."
	echo "Aborting."
	exit 2
fi

test -r $SC && cp $SC $SC.$(date -u +%s).bak
echo -e "\nurl.todo=$SERVER_URL/FionaTodoListProxy" >> $SC
echo "== url.todo updated in $SC:"
grep url.todo= $SC

# at this point, we certainly don't have network access, so launch it in background
# it will do its job as soon as WiFi is available
test "$protocol" == "https://" && /bin/sh "$GC" "$SERVER_URL" >$GC.log 2>&1 &

exit 0 # required because we have trailing junk data (?)
