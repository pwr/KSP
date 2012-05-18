#!/usr/bin/env python

import sys, os, os.path


def abspath(p, mkdir = False):
	if not p:
		return None
	if p[0] == '~':
		if os.environ['HOME']:
			p = os.environ['HOME'] + p[1:]
		elif os.environ['USERPROFILE']:
			p = os.environ['USERPROFILE'] + p[1:]
		else:
			raise Exception("don't know how to translate ~ to $HOME")
	elif not os.path.isabs(p):
		p = os.path.join(os.path.dirname(__file__), p)
	p = os.path.abspath(p)
	if mkdir and not os.path.exists(p):
		os.makedirs(p)
	return p

def _args():
	import argparse
	p = argparse.ArgumentParser(description = "Device manager for Kindle Store proxy")
	p.add_argument('--config', dest = 'etc_path', default = 'etc', help = "Path to the configration folder")
	p.add_argument('--db', dest = 'db_path', default = 'db', help = "Path to the database folder")
	p.add_argument('--device', dest = 'device_id', help = "The id of the device to operate on")
	p.add_argument('--rename', dest = 'new_name', help = "Rename the specified --device")
	p.add_argument('--delete', action = 'store_const', const = True, help = "Delete the specified --device")
	return p.parse_args()

import logging

def main():
	args = _args()
	sys.path.append(abspath(args.etc_path))

	import config
	logging.basicConfig(format = "%(levelname)-8s %(message)s", level = 'DEBUG')
	logging.getLogger()
	logging.captureWarnings(True)

	config.database_path = abspath(args.db_path, True)

	# add the src/ folder to the import path
	sys.path.append(abspath('src'))
	import devices

	d = devices.get(args.device_id)
	if args.device_id and not d:
		logging.warn("Device %s not found", args.device_id)
	elif args.delete:
		if not args.device_id:
			logging.warn("--device parameter required")
		else:
			logging.warn("Deleting device %s", d)
			devices._db.delete(d)
	elif args.new_name:
		if not args.device_id:
			logging.warn("--device parameter required")
		else:
			logging.warn("Renaming device %s to %s", d, args.new_name)
			d.alias = args.new_name
			devices._db.update(d)
	elif d:
		logging.info("%s", d)


if __name__ == '__main__':
	main()
	os._exit(0)
