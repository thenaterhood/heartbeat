#!/usr/bin/env python

from distutils.core import setup
import sys

install_requires = []
suggested = {
    'Pushbullet': ["pushbullet.py >= 0.5"],
    'Blinkstick': ["blinkstick >= 1.1.6"]
        }

if (sys.version_info < (3, 4)):
    install_requires.append('enum34 >= 1.0')

setup(name='Heartbeat',
    version='2.3.1',
    description='Heartbeat monitoring tool',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/heartbeat/archive/master.zip',
    requires=install_requires,
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
        ('etc', ['dist/_etc/heartbeat.yml']),
        ]
    )

print()
print("====================> Suggested Packages <=====================")
for k in suggested:
    print("        " + k + ", satisfiable by " + str(suggested[k]))
print()
