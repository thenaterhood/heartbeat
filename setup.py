#!/usr/bin/env python

from distutils.core import setup

setup(name='Heartbeat',
    version='0.1',
    description='Heartbeat monitoring tool',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/heartbeat/archive/master.zip',
    package_dir={'':'src'},
    packages=['heartbeat'],
    )
