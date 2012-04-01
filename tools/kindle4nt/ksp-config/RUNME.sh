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

RW=
mount_rw() {
  if [ -z "$RW" ]; then
    RW=yes
    mount -o rw,remount /
  fi
}

mount_ro() {
  if [ -n "$RW" ]; then
    RW=
    mount -o ro,remount /
  fi
}

SC=/opt/amazon/ebook/config/ServerConfig.conf
if test ! -f "$SC"; then
	echo "$SC not found on the device!"
	echo "Are you sure this is a Kindle 4 Non-Touch?"
	exit 1
fi

K=/mnt/us/KSP/
test -d $K || exit 0

serial=$(cat /proc/usid)
echo Copying client.p12 to $K/$serial.p12
cp -af /var/local/java/prefs/certs/client.p12 $K/$serial.p12

if ! test -f $SC.original; then
	echo Making a backup copy of $SC
	mount_rw
	cp -a $SC $SC.original
fi
# copy the original to /mnt/us/KSP/ as well
cp -af $1.original $K

if test -f "$K/ServerConfig.conf"; then
	# a version of ServerConfig.conf is present in /mnt/us/KSP/, we apply it as-is
	mount_rw
	echo Overwriting $SC with $K/ServerConfig.conf
	mv -f $K/$fn $SC # so we don't find it the next reboot
elif test "$SERVER_URL" == "NOT_SET"; then
	echo "You must set SERVER_URL in the script $0!"
else
	if expr match "$SERVER_URL" '.*/' >/dev/null; then
		SERVER_URL=$(expr match $SERVER_URL '\(.*\)/')
	fi
	mount_rw
	# replace the configured urls with the new value
	sed -i -e "s!^url.todo=http.*/FionaTodoListProxy$!url.todo=$SERVER_URL/FionaTodoListProxy!" $SC
	sed -i -e "s!^url.cde=http.*/FionaCDEServiceEngine$!url.cde=$SERVER_URL/FionaCDEServiceEngine!" $SC
	sed -i -e "s!^url.firs=http.*/FirsProxy$!$SERVER_URL/FirsProxy!" $SC
	sed -i -e "s!^url.firs.unauth=http.*/FirsProxy$!$SERVER_URL/FirsProxy!" $SC
	sed -i -e "s!^url.det=http.*/DeviceEventProxy$!$SERVER_URL/DeviceEventProxy!" $SC
	sed -i -e "s!^url.det.unauth=http.*/DeviceEventProxy$!$SERVER_URL/DeviceEventProxy!" $SC
	sed -i -e "s!^url.messaging.post=http.*$!url.messaging.post=$SERVER_URL!" $SC

	GC=/mnt/us/get_certificates.sh
	# at this point, we certainly don't have network access, so launch it in background
	# it will do its job as soon as WiFi is available
	text -r $GC && /bin/sh $GC "$SERVER_URL" >$GC.log 2>&1 &
fi

mount_ro

exit 0 # required because we have trailing junk data (?)
