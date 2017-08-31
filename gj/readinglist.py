"""Read from iCloud Reading List

"""

from __future__ import print_function


def lookup(data, *args):
    "Return result of sequence of lookups on data."
    for arg in args:
        if isinstance(arg, int):
            data = data[arg]
        elif isinstance(arg, str):
            data = data[arg]
        elif isinstance(arg, tuple):
            key, value = arg
            for item in data:
                if item[key] == value:
                    data = item
                    break
            else:
                raise LookupError
    return data


def read(clear=False):
    "Read item from reading list."
    import biplist  # pylint: disable=import-error
    import diskcache  # pylint: disable=import-error
    import os.path
    import webbrowser

    home_dir = os.path.expanduser('~')
    gj_dir = os.path.join(home_dir, '.gj')
    cache_dir = os.path.join(gj_dir, 'diskcache')
    cache = diskcache.FanoutCache(cache_dir)
    reading_list_index = cache.index('reading-list')

    if clear:
        reading_list_index.clear()
        return

    data = biplist.readPlist('/Users/grantj/Library/Safari/Bookmarks.plist')

    reading_list_all = lookup(
        data,
        'Children',
        ('Title', 'com.apple.ReadingList'),
        'Children'
    )

    reading_list = [
        item for item in reading_list_all
        if 'DateLastViewed' not in item['ReadingList']
    ]

    reading_list.sort(key=lambda item: item['ReadingList']['DateAdded'])

    for item in reading_list:
        url = item['URLString']

        if url not in reading_list_index:
            reading_list_index[url] = 1
            webbrowser.open(url)
            break
    else:
        print(u'Nothing to read \N{white frowning face}')
