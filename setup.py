#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from distutils.extension import Extension
from Cython.Build import cythonize

import numpy


spike_source_files = ['burst_sync/spike/cython_spike/cython_spike.pyx',
                      'burst_sync/spike/cython_spike/find_corner_spikes.c']
sttc_source_files = ['burst_sync/sttc/cython_sttc/cython_sttc.pyx',
                     'burst_sync/sttc/cython_sttc/spike_time_tiling_coefficient.c']
include_dirs = [numpy.get_include()]
extensions = [Extension('cython_spike',
                        sources=spike_source_files,
                        include_dirs=include_dirs),
              Extension('cython_sttc',
                        sources=sttc_source_files,
                        include_dirs=include_dirs)]

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = ['cython', 'numpy']


setup(
    name='burst_sync',
    version='0.1.1.dev0',
    description="burst_sync",
    long_description=readme + '\n\n' + history,
    author="Larry Eisenman",
    author_email='leisenman@wustl.edu',
    url='https://github.com/lneisenman/burst_sync',
    packages=[
        'burst_sync',
    ],
    package_dir={'burst_sync':
                 'burst_sync'},
    package_data={'': ['*.pyx', '*.pxd', '*.h', '*.txt', '*.dat', '*.csv']},
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='burst_sync',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Cython',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    ext_modules=cythonize(extensions),
)
