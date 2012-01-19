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

K=/mnt/us/KSP/

apply_conf() { # device file, [KSP file name], ['overwrite'(default)|'append']
	if ! test -f $1; then
		echo $1 not found on the device!
		echo Are you sure this is a Kindle 4 Non-Touch?
		return
	fi
	if ! test -f $1.original; then
		echo Making a backup copy of $1
		mount_rw
		cp -a $1 $1.original
	fi
	cp -af $1.original $K

	fn=${2:-$(basename "$1")}
	if test -f $K/$fn; then
		mount_rw
		case ${3:-overwrite} in
			overwrite)
				echo Overwriting $K/$fn to $1
				mv -f $K/$fn $1 # so we don't find it the next reboot
				;;
			append)
				echo Appending $K/$fn to $1
				cat $K/$fn >> $1
				rm -f $K/$fn # so we don't find it the next reboot
				;;
		esac
	fi
}


if test -d $K; then
	serial=$(cat /proc/usid)
	echo Copying client.p12 to $K/$serial.p12
	cp -af /var/local/java/prefs/certs/client.p12 $K/$serial.p12

	apply_conf /opt/amazon/ebook/config/ServerConfig.conf
	apply_conf /usr/java/lib/security/cacerts
	apply_conf /etc/ssl/certs/ca-certificates.crt CAcert.pem append
fi

mount_ro

exit 0 # required because we have trailing junk data (?)
