#!/usr/bin/env python

"""
Copyright (c) 2016 Binoj D (@dbinoj)
See the file 'LICENSE' for copying permission
"""

import subprocess
import glob
import inspect
import os
import sys
import time
import urllib
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

MALTRAIL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "maltrail"))
MALTRAIL_MIRROR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "maltrail-feeds-mirror"))

TRAIL_SIZE_LIMIT_MB = 90
TOTAL_SIZE_LIMIT_MB = 900

sys.path.append(MALTRAIL_DIR)
sys.path.append(os.path.abspath(os.path.join(MALTRAIL_DIR, "trails", "feeds")))
filenames = sorted(glob.glob(os.path.join(sys.path[-1], "*.py")))
filenames = [_ for _ in filenames if "__init__.py" not in _]

log = open(os.path.join(MALTRAIL_MIRROR_DIR, "MIRROR.log"), 'w')

total_size = 0

for i in xrange(len(filenames)):
	filename = filenames[i]

	try:
		module = __import__(os.path.basename(filename).split(".py")[0])
	except (ImportError, SyntaxError), ex:
		msg = "[x] something went wrong during import of feed file '%s' ('%s')" % (filename, ex)
		log.write("%s\n" % msg)
		print msg
		continue

	for name, function in inspect.getmembers(module, inspect.isfunction):
		if name == "fetch":
			print(" [o] %s%s" % (module.__name__, " " * 20 if len(module.__name__) < 20 else ""))

			head = requests.head(module.__url__, headers={'Accept-Encoding': 'identity'}).headers
			head = {k.lower(): v for k, v in head.items()}
			try:
				trail_size = int(head['content-length'])
				if trail_size > (TRAIL_SIZE_LIMIT_MB * 1048576):
					msg = '%s is ignored. File size exceeds %s MB.' % (module.__name__, str(TRAIL_SIZE_LIMIT_MB))
					log.write("%s\n" % msg)
					print msg
					continue
			except KeyError:
				trail_size = False
			else:
				total_size = total_size + trail_size
				if total_size > (TOTAL_SIZE_LIMIT_MB * 1048576):
					msg = '%s is ignored. Repo size exceeds %s MB.' % (module.__name__, str(TOTAL_SIZE_LIMIT_MB))
					log.write("%s\n" % msg)
					print msg
					continue

			try:
				urllib.urlretrieve(module.__url__, os.path.join(MALTRAIL_MIRROR_DIR, module.__name__))
			except:
				msg = "[x] something went wrong during remote data retrieval ('%s')" % module.__url__
				log.wrtie("%s\n" % msg)
				print msg

			if not trail_size:
				trail_size = os.path.getsize(os.path.join(MALTRAIL_MIRROR_DIR, module.__name__))
				total_size = total_size + trail_size
				if trail_size > (TRAIL_SIZE_LIMIT_MB * 1048576):
					msg = '%s ignored. File size exceeds %s MB.' % (module.__name__, str(TRAIL_SIZE_LIMIT_MB))
				elif total_size > (TOTAL_SIZE_LIMIT_MB * 1048576):
					msg = '%s ignored. Repo size exceeds %s MB.' % (module.__name__, str(TOTAL_SIZE_LIMIT_MB))
				else:
					continue
				os.remove(os.path.join(MALTRAIL_MIRROR_DIR, module.__name__))
				log.write("%s\n" % msg)
				print msg

log.close()

subprocess.check_call(["git", "add", "."], cwd=MALTRAIL_MIRROR_DIR)
subprocess.check_call(["git", "commit", "-m", "%s update" % time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())], cwd=MALTRAIL_MIRROR_DIR)
subprocess.check_call(["git", "push", "origin", "master"], cwd=MALTRAIL_MIRROR_DIR)

print " [v] %s Mirror Updated." % time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
