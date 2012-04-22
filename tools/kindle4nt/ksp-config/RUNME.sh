#!/bin/sh

##########################################
# YOU HAVE TO SET THIS TO THE SERVER URL #
##########################################
# e.g.
# SERVER_URL=https://_server_name_:_server_port_
# where :_server_port_ is optional and defaults to 443
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
	exit 1
fi

# update the API urls
SC=/var/local/java/prefs/com.amazon.ebook.framework/ServerConfig

if ! grep -q $SERVER_URL $SC; then
	cp $SC $SC.$(date -u +%s).bak

	cat >> $SC <<-SERVER_CONFIG
		url.todo=$SERVER_URL/FionaTodoListProxy
		url.cde=$SERVER_URL/FionaCDEServiceEngine
		url.firs=$SERVER_URL/FirsProxy
		url.firs.unauth=$SERVER_URL/FirsProxy
	SERVER_CONFIG
fi

GC=/mnt/us/get_certificates.sh
# at this point, we certainly don't have network access, so launch it in background
# it will do its job as soon as WiFi is available
text -r $GC && /bin/sh $GC "$SERVER_URL" >$GC.log 2>&1 &

exit 0 # required because we have trailing junk data (?)
