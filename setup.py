#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for burst_sync.

"""

import setuptools
from setuptools import setup

from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

from burst_sync._version import version

requirements = ['cython', 'numpy']
spike_source_files = ["burst_sync/spike/cython_spike/cython_spike.pyx",
                      "burst_sync/spike/cython_spike/find_corner_spikes.c"]
sttc_source_files = ["burst_sync/sttc/cython_sttc/cython_sttc.pyx",
                     "burst_sync/sttc/cython_sttc/spike_time_tiling_coefficient.c"]
include_dirs = [numpy.get_include()]
extensions = [Extension("burst_sync.spike.cython_spike",
                        sources=spike_source_files,
                        include_dirs=include_dirs),
              Extension("burst_sync.sttc.cython_sttc",
                        sources=sttc_source_files,
                        include_dirs=include_dirs)]
spike_other_files = ["burst_sync/spike/cython_spike/cython_spike.pyx",
                     "burst_sync/spike/cython_spike/find_corner_spikes.c",
                     "burst_sync/spike/cython_spike/find_corner_spikes.h"]
sttc_other_files = ["burst_sync/sttc/cython_sttc/cython_sttc.pyx",
                    "burst_sync/sttc/cython_sttc/spike_time_tiling_coefficient.c",
                    "burst_sync/sttc/cython_sttc/spike_time_tiling_coefficient.h"]

setup(name='burst_sync',
      version=version,
      license='BSD',
      packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
      install_requires=requirements,
      ext_modules=cythonize(extensions),
      tests_require=['pytest-cov', 'pytest'],
      package_data={'': ['*.pyx', '*.pxd', '*.h', '*.txt', '*.dat', '*.csv']},
      zip_safe=False)  # do not zip egg file after setup.py install
