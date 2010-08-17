# -*- coding: utf-8 -*-

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sy1 as sy


setup(
    name='sy',
    version=sy.__version__,
    url='http://github.com/pauldiacon/sy.git',
    license='BSD',
    author='Paul Diaconescu',
    author_email='p@feedem.net',
    description='Simple tools for system administration tasks',
    long_description=sy.path.slurp('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration'
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=['sy1', 'sy1.net', 'sy1.net.intf'],
    package_data={
        'sy1': ['lib/*']
    },
    platforms='Python 2.4 and later on Unix'
)
