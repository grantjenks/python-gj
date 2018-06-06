"""Miscellaneous Utilities

"""

from __future__ import print_function

import functools
import glob as globlib
import logging
import os
import subprocess
import sys
import time

log = logging.getLogger(__name__)


def watch(command, paths):
    """Run `command` when any of `paths` are modified.

    """
    if sys.hexversion < 0x03000000:
        glob = globlib.iglob
        if any('**' in path for path in paths):
            message = 'recursive glob support not implemented in Python 2'
            raise NotImplementedError(message)
    else:
        glob = functools.partial(globlib.iglob, recursive=True)

    mtimes = {}

    for path in paths:
        for filename in glob(path):
            try:
                mtime = os.path.getmtime(filename)
                mtimes[filename] = mtime
                log.debug('Recorded %.6f for %r', mtime, filename)
            except OSError:
                log.error('mtime error for %r', filename)
                return

    try:
        while True:
            changed = False

            for path in paths:
                for filename in glob(path):
                    try:
                        mtime = os.path.getmtime(filename)
                    except OSError:
                        log.error('mtime error for %r', filename)
                    else:
                        if mtime != mtimes.get(filename, 0):
                            log.info('Detected mtime change for %r', filename)
                            changed = True
                            mtimes[filename] = mtime

            if changed:
                log.info('Running %r', command)
                subprocess.call(command, shell=True)

            time.sleep(1)
    except KeyboardInterrupt:
        print()
        exit(0)
