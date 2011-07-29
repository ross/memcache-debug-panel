#!/usr/bin/env python

from setuptools import setup

setup(
    name='memcache_toolbar',
    version='0.5.1',
    description='',
    author='Ross McFarland',
    author_email='rwmcfa1@neces.com',
    url='http://github.com/ross/memcache-debug-panel',

    packages=['memcache_toolbar'],
    provides=['memcache_toolbar'],
    requires=['Django', 'debug_toolbar'],
)
