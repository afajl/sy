# -*- coding: utf-8 -*-

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sy, sy.path


setup(
    name='sy',
    version=sy.__version__,
    url='http://sy.afajl.com',
    license='BSD',
    author='Paul Diaconescu',
    author_email='p@afajl.com',
    description='Simple tools for system administration tasks',
    long_description=sy.path.slurp('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=['sy', 'sy.net', 'sy.net.intf'],
    package_data={
        'sy': ['lib/*']
    },
    platforms='Python 2.4 and later on Unix',
    install_requires=['logbook>=0.3', 'ipaddr>=2.0.0']
)
