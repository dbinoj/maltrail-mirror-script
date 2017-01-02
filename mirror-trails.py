#!/usr/bin/env python

"""
Thanks to Miroslav Stampar (@stamparm) for the software "maltrail"
This script calls a function from from stamparm/maltrail's core/update module which is used to generate updated trails.csv
Copyright (c) 2016 Binoj D (@dbinoj)
See the file 'LICENSE' for copying permission
"""

import subprocess
import os
import sys
import time

MALTRAIL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "maltrail"))
MALTRAIL_MIRROR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "maltrail-update-mirror"))
TRAILS_FILE_NAME = "trails.csv"

sys.path.append(MALTRAIL_DIR)

from core import update
from core.settings import TRAILS_FILE

subprocess.call(["cp", "maltrail.conf", ".."], cwd=MALTRAIL_DIR)
subprocess.call(["git", "checkout", "maltrail.conf"], cwd=MALTRAIL_DIR)
subprocess.call(["git", "pull", "origin", "master"], cwd=MALTRAIL_DIR)
subprocess.call(["mv", "../maltrail.conf", "."], cwd=MALTRAIL_DIR)

update.main()

filesize = os.path.getsize(TRAILS_FILE) >> 20

if filesize > 90:
    print " [x] Trails file size is greater than 90mb. Aborting."
    exit()

subprocess.call(["cp", ".git/config", "../gitconfig"], cwd=MALTRAIL_MIRROR_DIR)

subprocess.check_call(["rm", "-rf", ".git"], cwd=MALTRAIL_MIRROR_DIR)

subprocess.check_call(["rm", "-f", TRAILS_FILE_NAME], cwd=MALTRAIL_MIRROR_DIR)
subprocess.check_call(["cp", TRAILS_FILE, os.path.join(MALTRAIL_MIRROR_DIR, TRAILS_FILE_NAME)])

subprocess.check_call(["git", "init"], cwd=MALTRAIL_MIRROR_DIR)

subprocess.call(["mv", "../gitconfig", ".git/config"], cwd=MALTRAIL_MIRROR_DIR)

subprocess.check_call(["git", "add", "."], cwd=MALTRAIL_MIRROR_DIR)
subprocess.call(["git", "commit", "-m", "%s update" % time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())], cwd=MALTRAIL_MIRROR_DIR)

subprocess.check_call(["git", "push", "-u", "--force", "origin", "master"], cwd=MALTRAIL_MIRROR_DIR)

print " [c] %s Mirror Update script exit." % time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
