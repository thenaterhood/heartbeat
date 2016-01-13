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

setup(name='heartbeat',
    version='2.10.0',
    description='Minimalist network monitoring tool',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/heartbeat/archive/master.zip',
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite='nose.collector',
    package_dir={'':'src'},
    package_data={
        '': [
            '*.conf',
            'systemd',
            'sysvinit'
        ]
    },
    entry_points={
        'console_scripts': [
            'startheart = heartbeat.main:main',
            'heartbeat-install = heartbeat.install:main'
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
        'heartbeat.pluggable',
        # Heartbeat file resources
        'heartbeat.resources',
        'heartbeat.resources.cfg',
        'heartbeat.resources.service'
        ],
    )

print("Run `heartbeat-install --install-cfg` to install Heartbeat's default configuration files in order to complete your installation.")
