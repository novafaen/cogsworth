# -*- coding: utf-8 -*-
"""``Cogsworth`` setup tools file."""

from setuptools import setup

setup(
    name='cogsworth',
    version='0.0.1',
    description='Well, there\'s the usual things: '
                'flowers... chocolates... '
                'promises you don\'t intend to keep...',
    author='Kristoffer Nilsson',
    author_email='smrt@novafaen.se',
    url='http://smrt.novafaen.se/',
    packages=['cogsworth'],
    install_requires=[
        'schedule==0.6.0',
        'requests>=2.21',
        'jsonschema>=3.0'
    ],
    test_suite='tests',
    tests_require=[

    ])
