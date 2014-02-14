#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        super(PyTest, self).finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import sys
        import pytest

        sys.exit(pytest.main(self.test_args))


setup(
    name='g4s',
    version='0.0.0',
    author='east301',
    author_email='me@east301.net',
    url='http://github.com/east301/g4s',
    download_url='http://github.com/east301/g4s',
    description='calendar synchronization toolkit',
    long_description='',
    platforms='any',
    packages=['g4s', 'g4s.core'],
    package_dir={'': 'src'},
    package_data={},
    keywords='calendar synchronization',
    classifiers=[],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
