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

# Pymlconf 0.3.21+ breaks on old versions of Python
if (sys.version_info < (3, 3)):
    del(install_requires[0])
    install_requires.append("pymlconf <= 0.3.20")

setup(name='heartbeat',
    version='3.5.1',
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
            'startheart = heartbeat.__main__:main',
            'heartbeat-install = heartbeat.__install__:main'
            ]
    },
    packages=[
        'heartbeat',
        'heartbeat.modules',
        'heartbeat.network',
        'heartbeat.monitoring',
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
