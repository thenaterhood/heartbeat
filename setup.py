#!/usr/bin/env python

from setuptools import setup
import sys

install_requires = [
    'pymlconf',
    'pyyaml'
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

setup(name='Heartbeat',
    version='2.4.1',
    description='Minimalist network monitoring tool',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/heartbeat/archive/master.zip',
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite='nose.collector',
    package_dir={'':'src'},
    packages=[
        'heartbeat',
        'heartbeat.modules',
        'heartbeat.network',
        'heartbeat.monitoring',
        'heartbeat.notifications',
        'heartbeat.platform',
        'heartbeat.multiprocessing'
        ],
    data_files=[
        ('../etc/heartbeat', ['dist/_etc/heartbeat/heartbeat.conf']),
        ('../etc/heartbeat', ['dist/_etc/heartbeat/monitoring.conf']),
        ('../etc/heartbeat', ['dist/_etc/heartbeat/notifying.conf']),
        ('lib/systemd/system', ['dist/_lib/systemd/system/heartbeat.service']),
        ('bin', ['dist/_bin/startheart'])
        ]
    )

