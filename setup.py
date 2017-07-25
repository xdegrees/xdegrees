#!/usr/bin/env python

import os
import pip
from glob import glob
from os.path import basename, splitext
from pip.req import parse_requirements
from setuptools import Command, find_packages, setup
from setuptools.command.test import test
import sys


def read(*paths):
    """ Read files. """
    with open(os.path.join(*paths), 'r') as filename:
        return filename.read()


class CleanCommand(Command):
    """ Clean the local workspace more aggressively than the default setuptools equivalent. """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info ./.eggs')


class PyTest(test):
    """ Allows us to execute tests using py.test as a one-liner. """
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


# load requirements from the config file
reqs_from_file = parse_requirements('requirements.txt', session=pip.download.PipSession())
requirements = [str(ir.req) for ir in reqs_from_file]
# ditto test requirements
test_reqs_from_file = parse_requirements('requirements-tests.txt', session=pip.download.PipSession())
test_requirements = [str(ir.req) for ir in test_reqs_from_file]

# load the version from the root module
version = {}
exec(read('xdegrees/_version.py'), version)


setup(
    name='xdegrees',
    version = version['__version__'],
    author='Josh',
    author_email='jtoberon@gmail.com',
    description=(read('README.md')),
    license='MIT',
    url='https://github.com/jtoberon/xdegrees',
    packages=find_packages('xdegrees'),
    package_dir={'': 'xdegrees'},
    py_modules=[splitext(basename(path))[0] for path in glob('xdegrees/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=test_requirements,
    cmdclass={
        'clean': CleanCommand,
        'test': PyTest,
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5'
    ]
)
