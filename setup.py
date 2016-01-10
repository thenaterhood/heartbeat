#!/usr/bin/env python

from setuptools import setup
import sys
import os

install_requires = [
    'pymlconf',
    'pyyaml',
    'pycryptodome'
    ]

test_requires = [
    'nose',
    'mock'
    ]

suggested = {
    'Pushbullet': ["pushbullet.py >= 0.5"],
    'Blinkstick': ["blinkstick >= 1.1.6"]
        }

if (sys.version_info < (3, 4)):
    install_requires.append('enum34')

if (sys.platform == 'win32'):
    data_location = os.path.join(os.environ['PROGRAMDATA'], 'Heartbeat')
    data_files=[
        (os.path.join(data_location, 'Settings'), ['dist/_etc/heartbeat/heartbeat.conf']),
        (os.path.join(data_location, 'Settings'), ['dist/_etc/heartbeat/monitoring.conf']),
        (os.path.join(data_location, 'Settings'), ['dist/_etc/heartbeat/notifying.conf']),
        ]
else:
    data_files=[
        ('etc/heartbeat', ['dist/_etc/heartbeat/heartbeat.conf']),
        ('etc/heartbeat', ['dist/_etc/heartbeat/monitoring.conf']),
        ('etc/heartbeat', ['dist/_etc/heartbeat/notifying.conf']),
        ('lib/systemd/system', ['dist/_lib/systemd/system/heartbeat.service']),
        ]


setup(name='heartbeat',
    version='2.8.0',
    description='Minimalist network monitoring tool',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/heartbeat/archive/master.zip',
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite='nose.collector',
    package_dir={'':'src'},
    entry_points={
        'console_scripts': [
            'startheart = heartbeat.main:main'
            ]
    },
    packages=[
        'heartbeat',
        'heartbeat.modules',
        'heartbeat.network',
        'heartbeat.monitoring',
        'heartbeat.notifications',
        'heartbeat.platform',
        'heartbeat.plugin',
        'heartbeat.multiprocessing',
        'heartbeat.security',
        'heartbeat.pluggable'
        ],
    data_files=data_files
    )
