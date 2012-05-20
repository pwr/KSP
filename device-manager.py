#!/usr/bin/env python -bBu
import sys, os, os.path, logging

from main import abspath


def _args():
	import argparse
	p = argparse.ArgumentParser(description = "Device manager for Kindle Store proxy", epilog = """
			If --device is given, and no other options, the specified device is checked.
			If no options are given, all devices are listed and checked.
		""")
	p.add_argument('--config', dest = 'etc_path', default = 'etc', help = "Path to the configration folder")
	p.add_argument('--db', dest = 'db_path', default = 'db', help = "Path to the database folder")
	p.add_argument('--device', dest = 'device_id', help = "The id of the device to operate on; may be only the start of an existing device id")
	p.add_argument('--rename', dest = 'new_name', help = "Changed the stored name of the specified --device")
	p.add_argument('--delete', action = 'store_const', const = True, help = "Delete the specified --device from KSP's database")
	return p.parse_args()

def check_device(d):
	if d.is_kindle():
		if d.load_context():
			logging.info("device %s, client certificate validated", d)
		else:
			logging.warn("device %s, client certificate FAILED", d)
	else:
		logging.info("device %s", d)


if __name__ == '__main__':
	logging.basicConfig(format = "%(levelname)-8s %(message)s", level = 'INFO')
	logging.getLogger()
	logging.captureWarnings(True)

	args = _args()
	sys.path.append(abspath(args.etc_path))

	import config
	config.database_path = abspath(args.db_path)

	# add the src/ folder to the import path
	sys.path.append(abspath('src'))
	import devices.db as _db

	devices = { d.serial: d for d in _db.load_all() }

	if args.device_id:
		d = devices.get(args.device_id)
		if not d:
			for k,v in devices.items():
				if k.startswith(args.device_id):
					d = v
					break
	else:
		d = None

	if args.device_id and not d:
		logging.warn("Device %s not found", args.device_id)
	elif args.delete:
		if not args.device_id:
			logging.warn("--device parameter required")
		else:
			logging.warn("Deleting device %s", d)
			_db.delete(d)
	elif args.new_name:
		if not args.device_id:
			logging.warn("--device parameter required")
		else:
			logging.warn("Renaming device %s to %s", d, args.new_name)
			d.alias = args.new_name
			_db.update(d)
	elif d:
		check_device(d)
	else:
		for d in devices.values():
			check_device(d)
