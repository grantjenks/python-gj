"Packages tools."

from __future__ import print_function

import glob
import os
import os.path as op
import re
import shutil
import subprocess as sp
import sys

import paramiko


def run(command):
    "Run `command` and display output."
    print('gj$', command)
    sp.check_call(command.split())


def chdir(path):
    "Change working directory to `path`."
    print('gj$ cd', path)
    os.chdir(path)


def sftp_mkdir(sftp, path):
    "Make directory at `path` using `sftp` connection."
    print('gj$ # sftp.mkdir', path)
    try:
        sftp.mkdir(path)
    except IOError:
        pass


def sftp_upload(sftp, local_path, remote_path):
    "Upload binary file `reader` to `path` using `sftp` connection."
    print('gj$ # sftp.put', local_path, remote_path)
    sftp.put(local_path, remote_path)


def lookup_name(cwd):
    "Lookup package name in directory `cwd`."

    _, dirname = op.split(cwd)

    prefixes = ['python-', 'python_', 'django-']

    for prefix in prefixes:
        if dirname.startswith(prefix):
            dirname = dirname[len(prefix):]
            break

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

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('104.198.0.77')
    sftp = ssh.open_sftp()

    base = '/srv/www/www.grantjenks.com/docs/%s' % name

    sftp_mkdir(sftp, base)

    chdir(op.join('_build', 'html'))

    for path, dirs, files in os.walk('.'):
        for directory in dirs:
            sftp_mkdir(sftp, '/'.join([base, path, directory]))

        for filename in files:
            local_path = op.join(path, filename)
            remote_path = '/'.join([base, path, filename])
            sftp_upload(sftp, local_path, remote_path)


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

    setup_py = open('setup.py').read()

    if 'Extension(' in setup_py:
        dist = 'sdist'  # Use source distribution for binary extensions.
    else:
        dist = 'sdist bdist_wheel --universal'

    run('python setup.py %s' % dist)
    run('twine upload ' + ' '.join(glob.glob('dist/*')))

    if not docs:
        return

    shutil.rmtree(op.join('docs', '_build'), ignore_errors=True)

    print('gj$ # Building Docs')

    chdir(op.join(cwd, 'docs'))

    run('make clean')
    run('make html')

    upload_docs(name)
