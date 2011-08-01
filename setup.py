#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='memcache_toolbar',
    version='0.5.2',
    description='',
    author='Ross McFarland',
    author_email='rwmcfa1@neces.com',
    url='http://github.com/ross/memcache-debug-panel',
    packages=find_packages(exclude=('examples', 'examples.demo', 'test')),
    provides=['memcache_toolbar'],
    requires=['Django', 'debug_toolbar'],
    include_package_data=True,
    zip_safe=False,
)
