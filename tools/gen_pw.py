#!/usr/bin/env python

import hashlib

serial = input("Enter your device serial number: ").strip()
serialmd5 = hashlib.md5((serial + '\n').encode('utf-8'))
print("Serial md5 is", serialmd5)
pw = 'fiona' + serialmd5.hexdigest()[7:11]
print("Password for device [%s] is [%s]" % (serial, pw))
