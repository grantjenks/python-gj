"Packages tools."

from __future__ import print_function

import ftplib
import getpass
import glob
import os
import os.path as op
import re
import shutil
import subprocess as sp
import sys


def run(command):
    "Run `command` and display output."
    print('gj$', command)
    sp.check_call(command.split())


def chdir(path):
    "Change working directory to `path`."
    print('gj$ cd', path)
    os.chdir(path)


def ftp_mkdir(ftp, path):
    "Make directory at `path` using `ftp` connection."
    print('gj$ # ftp.mkdir', path)
    try:
        ftp.mkd(path)
    except ftplib.error_perm:
        pass


def ftp_upload(ftp, path, reader):
    "Upload binary file `reader` to `path` using `ftp` connection."
    print('gj$ # ftp.storb', path)
    command = 'STOR %s' % path
    ftp.storbinary(command, reader)


def lookup_name(cwd):
    "Lookup package name in directory `cwd`."

    _, dirname = op.split(cwd)

    prefix = 'python-'

    if dirname.startswith(prefix):
        dirname = dirname[len(prefix):]

    dirname = dirname.replace('_', '')

    return dirname


def lookup_version(name):
    "Lookup version for `name` package."

    try:
        with open(op.join(name, '__init__.py')) as reader:
            lines = reader.readlines()
    except IOError:
        with open('%s.py' % name) as reader:
            lines = reader.readlines()

    for line in lines:
        match = re.match(r'^__version__ = \'(.*)\'$', line)
        if match:
            return match.group(1)

    print('Error: Unknown version.')
    sys.exit(1)


def upload_docs(name):
    "Upload docs for package with `name`."

    print('gj$ # Uploading Docs')

    for _ in range(5):
        try:
            ftps = ftplib.FTP_TLS(
                'grantjenks.com',
                user='grant',
                passwd=getpass.getpass()
            )
            break
        except ftplib.error_perm as exception:
            error = exception
    else:
        raise error

    ftps.prot_p()

    base = '/domains/grantjenks.com/docs/%s' % name

    ftp_mkdir(ftps, base)

    chdir(op.join('_build', 'html'))

    for path, dirs, files in os.walk('.'):
        for directory in dirs:
            ftp_mkdir(ftps, '/'.join([base, path, directory]))

        for filename in files:
            with open(op.join(path, filename), 'rb') as reader:
                ftp_upload(ftps, '/'.join([base, path, filename]), reader)


def release(name=None, version=None, pylint=True, tox=True, docs=True):
    "Release package with `name` and `version`."

    cwd = os.getcwd()
    name = name or lookup_name(cwd)
    version = version or lookup_version(name)
    version = 'v%s' % version

    run('git checkout master')

    if version in sp.check_output(['git', 'tag']):
        print('Error: Version already tagged.')
        sys.exit(1)

    if sp.check_output(['git', 'status', '--porcelain']):
        print('Error: Commit files in working directory before release.')
        run('git status')
        sys.exit(1)

    run('git pull')

    if pylint:
        run('pylint %s' % name)

    if tox:
        run('tox --skip-missing-interpreters')

    run('rst-lint README.rst')
    run('doc8 docs')
    run('git tag -a %s -m %s' % (version, version))
    run('git push')
    run('git push --tags')
    shutil.rmtree('dist', ignore_errors=True)
    run('python setup.py sdist bdist_wheel --universal')
    run('twine upload ' + ' '.join(glob.glob('dist/*')))

    if not docs:
        return

    shutil.rmtree(op.join('docs', '_build'), ignore_errors=True)

    print('gj$ # Building Docs')

    chdir(op.join(cwd, 'docs'))

    run('make clean')
    run('make html')

    upload_docs(name)
