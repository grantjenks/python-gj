"""Miscellaneous Utilities

"""

from __future__ import print_function

import logging
import os
import subprocess
import time

log = logging.getLogger(__name__)


def watch(command, filenames):
    """Run `command` when any of `filenames` are modified.

    """
    filenames = sorted(set(filenames))
    mtimes = {}

    for filename in filenames:
        try:
            mtime = os.path.getmtime(filename)
            mtimes[filename] = mtime
            log.debug('Watching %s %r', mtime, filename)
        except OSError:
            log.error('mtime error for %r', filename)
            return

    try:
        while True:
            changed = False

            for filename in filenames:
                mtime = os.path.getmtime(filename)

                if mtimes[filename] != mtime:
                    log.info('Detected mtime change for %r', filename)
                    changed = True
                    mtimes[filename] = mtime

            if changed:
                log.info('Running %r', command)
                subprocess.call(command)

            time.sleep(1)
    except KeyboardInterrupt:
        print()
        exit(0)
