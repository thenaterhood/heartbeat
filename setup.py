#!/usr/bin/env python

from distutils.core import setup

setup(name='Heartbeat',
    version='1.0.1',
    description='Heartbeat monitoring tool',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/heartbeat/archive/master.zip',
    package_dir={'':'src'},
    packages=['heartbeat', 'heartbeat.modules', 'heartbeat.network', 'heartbeat.monitoring', 'heartbeat.notifications', 'heartbeat.platform', 'heartbeat.multiprocessing'],
    data_files=[
        ('etc', ['dist/_etc/heartbeat.yml']),
        ]
    )
