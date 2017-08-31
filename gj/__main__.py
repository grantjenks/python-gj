"Grant Jenks Tools main entry point."
# pylint: disable=invalid-name

import argparse

from . import packages, readinglist

parser = argparse.ArgumentParser(
    'gj',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

subparsers = parser.add_subparsers(dest='command', help='<command>')

parser_release = subparsers.add_parser('release', help='release package')
parser_release.add_argument('-n', '--name', default=None)
parser_release.add_argument('-v', '--version', default=None)
parser_release.add_argument('--no-pylint', action='store_true')
parser_release.add_argument('--no-tox', action='store_true')
parser_release.add_argument('--no-docs', action='store_true')

parser_upload_docs = subparsers.add_parser('upload-docs', help='upload docs')
parser_upload_docs.add_argument('name')

parser_reading_list = subparsers.add_parser(
    'reading-list',
    help='reading list'
)
parser_reading_list.add_argument('-c', '--clear', action='store_true')

args = parser.parse_args()

if args.command == 'release':
    packages.release(
        name=args.name,
        version=args.version,
        pylint=not args.no_pylint,
        tox=not args.no_tox,
        docs=not args.no_docs,
    )
elif args.command == 'upload-docs':
    packages.upload_docs(
        name=args.name,
    )
elif args.command == 'reading-list':
    readinglist.read(
        clear=args.clear,
    )
