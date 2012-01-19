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

Y=18
/usr/sbin/eips -c
log() {
	echo "$@"
	/usr/sbin/eips 11 $Y "$@"
	Y=$((Y+1))
}


if test -x /usr/local/bin/dropbearmulti; then
	log SSH binaries already available
else
	log Copying SSH binaries to the main partition
	mount_rw
	mkdir /mnt/JB-diags
	# blk0p2 is the partition that gets mounted in Diagnostics mode
	mount -o ro /dev/mmcblk0p2 /mnt/JB-diags
	cp -a /mnt/JB-diags/usr/local /usr/
	umount /mnt/JB-diags
	rmdir /mnt/JB-diags
fi

if grep -q 'A INPUT -i wlan0 -p tcp -m tcp --dport 22 -j ACCEPT' /etc/sysconfig/iptables; then
	log Firewall already allowing SSH over WiFi
else
	log Adding firewall rule for SSH over WiFi
	mount_rw
	sed -i '/^-A INPUT -i wlan0 -p tcp -m state --state RELATED,ESTABLISHED -j ACCEPT/a-A INPUT -i wlan0 -p tcp -m tcp --dport 22 -j ACCEPT' /etc/sysconfig/iptables
fi

mount_ro

exit 0 # required?
