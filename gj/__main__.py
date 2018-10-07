"Grant Jenks Tools main entry point."
# pylint: disable=invalid-name

import argparse
import logging

from . import backups, packages, readinglist, utils

parser = argparse.ArgumentParser(
    'gj',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')

subparsers = parser.add_subparsers(dest='subcommand', help='<subcommand>')

parser_release = subparsers.add_parser('release', help='release package')
parser_release.add_argument('--no-pylint', action='store_true')
parser_release.add_argument('--no-tox', action='store_true')
parser_release.add_argument('--no-docs', action='store_true')

parser_upload_docs = subparsers.add_parser('upload-docs', help='upload docs')
parser_upload_docs.add_argument('name')

parser_reading_list = subparsers.add_parser(
    'reading-list',
    help='reading list',
)
parser_reading_list.add_argument('-c', '--clear', action='store_true')

parser_watch = subparsers.add_parser(
    'watch',
    help='watch paths for changes and run command',
)
parser_watch.add_argument('command')
parser_watch.add_argument('path', nargs='+')

parser_backup_google_calendar = subparsers.add_parser(
    'backup-google-calendar',
    help='backup Google calendar',
)

args = parser.parse_args()

if args.debug:
    log_level = logging.DEBUG
elif args.verbose:
    log_level = logging.INFO
else:
    log_level = logging.WARNING

logging.basicConfig(level=log_level)

if args.subcommand == 'release':
    packages.release(
        pylint=not args.no_pylint,
        tox=not args.no_tox,
        docs=not args.no_docs,
    )
elif args.subcommand == 'upload-docs':
    packages.upload_docs(
        name=args.name,
    )
elif args.subcommand == 'reading-list':
    readinglist.read(
        clear=args.clear,
    )
elif args.subcommand == 'watch':
    utils.watch(
        command=args.command,
        paths=args.path,
    )
else:
    assert args.subcommand == 'backup-google-calendar'
    backups.backup_google_calendar()
