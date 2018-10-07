"""Backup Utilities

"""

from __future__ import print_function

import logging
import os

log = logging.getLogger(__name__)

def backup_google_calendar():
    """Backup Google Calendar

    """
    import browsercookie
    # TODO: Consider using pycookiecheat instead of browsercookie.
    import requests

    cj = browsercookie.chrome()
    url = 'https://calendar.google.com/calendar/exporticalzip'
    home_dir = os.environ['HOME']
    filename = 'google-calendar.zip'
    filepath = os.path.join(home_dir, filename)

    log.info('Get %s', url)
    resp = requests.get(url, cookies=cj)

    log.info('Save %s', filepath)
    with open(filepath, 'wb') as writer:
        writer.write(resp.content)
