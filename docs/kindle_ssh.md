SSH access to your Kindle
=========================

While SSH access into your Kindle 4 Non-Touch (again, no other Kindle is supported!) is not strictly necessary to make
the configuration changes, it may help to ensure the proper changes have been made and troubleshoot possible problems.
If you don't have SSH enabled on your Kindle, and don't want to bother with it, just skip to the next section.

If you do not have SSH enabled, you can use the script `tools/kindle4nt/enable-ssh/RUNME.sh` as such:

1. Connect the Kindle with the USB cable to your machine.

2. Copy `tools/kindle4nt/data.tar.gz` and `tools/kindle4nt/enable-ssh/RUNME.sh` to the root of the mounted volume, next
    to the `documents` folder.

Eject the Kindle volume, and restart the device: [MENU] -> _Settings_ -> [MENU] -> _Restart_.

When the device finishes restarting and shows up again as a disk, you should see a `RUNME.log` file. Look into it to
check the results. You should see something like this:

    Copying SSH binaries to the main partition
    Adding firewall rule for SSH over WiFi

This means you can eject the volume, and should be able to connect with SSH to the Kindle's WiFi IP. The username is
`root`, and the password should be either `mario` (if you have software version 4.0) or `fionaXXXX`, where the `XXXX`
part depends on your device serial. Use the `tools/gen_pw.py` script to compute it.

NOTE: Some users report sometimes the device does not restart properly -- i.e. does not run the whole boot sequence. If
you do not see the `RUNME.log` file, restart it again -- it should show up this time.
