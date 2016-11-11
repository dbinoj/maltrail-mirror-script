#!/usr/bin/env python

"""
Thanks to Miroslav Stampar (@stamparm) for the software "maltrail"
This script has code from stamparm/maltrail's update logic which is used to get the feed list from maltrail's codebase.
Copyright (c) 2016 Binoj D (@dbinoj)
See the file 'LICENSE' for copying permission
"""

import subprocess
import os
import sys
import time

MALTRAIL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "maltrail"))
MALTRAIL_MIRROR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "maltrail-update-mirror"))
LFS_SIZE_MB = 99
TRAILS_FILE_NAME = "trails.csv"

sys.path.append(MALTRAIL_DIR)

from core import update
from core.settings import TRAILS_FILE

subprocess.call(["git", "pull", "origin", "master"], cwd=MALTRAIL_DIR)

update.main()

subprocess.check_call(["rm", "-f", ".gitattributes", TRAILS_FILE_NAME], cwd=MALTRAIL_MIRROR_DIR)
subprocess.check_call(["cp", TRAILS_FILE, os.path.join(MALTRAIL_MIRROR_DIR, TRAILS_FILE_NAME)])

subprocess.check_call(["git", "lfs", "track", TRAILS_FILE_NAME], cwd=MALTRAIL_MIRROR_DIR)
subprocess.check_call(["git", "add", ".gitattributes", TRAILS_FILE_NAME], cwd=MALTRAIL_MIRROR_DIR)
subprocess.call(["git", "commit", "-m", "%s update" % time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())], cwd=MALTRAIL_MIRROR_DIR)
subprocess.check_call(["git", "push", "origin", "master"], cwd=MALTRAIL_MIRROR_DIR)
print " [c] %s Mirror Update script exit." % time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
