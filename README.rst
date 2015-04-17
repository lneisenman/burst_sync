.. image:: https://travis-ci.org/lneisenman/burst_sync.svg?branch=master
   :target: https://travis-ci.org/lneisenman/burst_sync

.. image:: https://coveralls.io/repos/lneisenman/burst_sync/badge.svg?branch=master
   :target: https://coveralls.io/r/lneisenman/burst_sync?branch=master

.. image:: https://ci.appveyor.com/api/projects/status/3os4d1tmukcrlb38/branch/master?svg=true
   :target: https://ci.appveyor.com/api/projects/status/3os4d1tmukcrlb38

==========
burst_sync
==========

This is the source code for::

   Eisenman et al. Quantification of bursting and synchrony in cultured hippocampal neurons. J Neurophysiol submitted.

It includes both Python and Igor code as described below. Please cite this
article if you use any of the code. License issues are addressed in the
License.txt file.

The Python code in this package requires Numpy, Scipy and Pandas to run. Cython
is required to compile from source.

The Python code has been tested for the 64 bit versions of Python 2.7 and 3.4
in both Windows (`AppVeyor <http://www.appveyor.com/>`_) and
Linux (`Travis <https://travis-ci.org/>`_)

The Igor code requires `Igor Pro <http://www.wavemetrics.com>`_.


Installation on Windows
=======================

If you do not already have Python installed on your system or don't know how
to ensure you have the required packages installed, your best bet is to use a
complete scientific distrubution such as `Anaconda <http://continuum.io/downloads>`_, 
`Enthought Canopy <https://www.enthought.com/products/canopy/>`_
or `WinPython <http://winpython.github.io/>`_.

Wheels for the 64 bit versions of Python 2.7 and Python 3.4 were compiled
using Appveyor. These wheels can be installed using a current version of pip::

   pip install -U pip
   # for Python2.7 use:
   pip install -U https://github.com/lneisenman/burst_sync/releases/download/v1.0/burst_sync-1.0-cp27-none-win_amd64.whl
   
   # for Python3.4 use:
   pip install -U https://github.com/lneisenman/burst_sync/releases/download/v1.0/burst_sync-1.0-cp34-none-win_amd64.whl


Installation on Linux
=====================

Assuming the appropriate compilers and development files for Python are
present, the code can be built from source with ``python setup.py install``.

On Ubuntu you would need the ``build-essential``, ``python-dev`` ``gfortran``,
``liblapack-dev``, ``libatlas-base-dev`` and ``python-pip`` packages that can
be installed using apt-get.

Note that Igor Pro does not run on Linux.


Robust Gaussian Surprise
========================

The code for Robust Gaussian Surprise is based on the R code published with::

   Ko et al. Detection of bursts and pauses in spike trains. J Neurosci Methods, 2012:145

Please make sure to cite Ko et al. in addition to Eisenman et al. if you use
this code.

The code expects the interspike intervals to be in a Pandas dataframe with the
label `isi` which in turn is in a list that is passed to the code. Multiple
dataframes can be passed in the same list. It returns lists of dataframes
for the identified bursts and pauses.

.. code-block:: py3

   import scipy as sp
   import pandas as pd
   from burst_sync import rgs

   isi = sp.stats.expon.rvs(lambda=2, size=1000)    # ISI's for Poisson spikes
   data = [pd.DataFrame({'isi': isi})]
   bursts, pauses = rgs.bp_summary(data, min_spikes=3)


SPIKE Syncrhony Meausure
========================

The SPIKE synchrony measure is described in::

   Kreuz et al. Monitoring spike train synchrony. J Neurophysiol, 2013:1457

Please make sure to cite Kreuz et al. in addition to Eisenman et al. if you use
this code.

This is a reimplementation of the code from `Kreuz <http://wwwold.fi.isc.cnr.it/users/thomas.kreuz/images/spike_distance.py>`_ 
using C and Cython. It assumes that the spike times for each channel are in a
numpy array. The parameters ti and tf represent the start and end times of the
spike train. The last parameter is the number of samples.

.. code-block:: py3

   import numpy as np
   from burst_sync import spike
   
   ti = 0
   tf = 1300
   samples = 50
   unit1 = np.arange(100, 1201, 100, dtype=np.float)
   unit2 = np.arange(100, 1201, 110, dtype=np.float)
   unit3 = np.arange(100, 1201, 120, dtype=np.float)
   tb, Sb = spike.bivariate_spike_distance(unit1, unit2, ti, tf, samples)
   bi_distance = np.average(Sb)
   
   unit_list = [unit1, unit2, unit3]
   tm, Sm = spike.multivariate_spike_distance(unit_list, ti, tf, samples)
   mv_distance = np.average(Sm)

 
STTC Synchrony Measure
======================

The Spike Time Tiling Coefficent is described in::

   Cutts and Eglen. Detecting pairwise correlations in spike trains: an objective comparison of methods and application to the study of retinal waves. J Neurosci, 2014:14288

Please make sure to cite Cutts and Eglen in addition to Eisenman et al. if you 
use this code.

This implementation uses Cython to access the C code from their manuscript.It 
assumes that the spike times for each channel are in a numpy array. The 
parameters dt, ti and tf represent the time step, start time and end time of 
the spike train. The multivariate_sttc returns a 2-D array whose values 
represent the bivariate sttc for the corresponding pair of spike trains.

.. code-block:: py3

   import numpy as np
   from burst_sync import sttc
   
   ti = 0
   tf = 1300
   dt = 1
   unit1 = np.arange(100, 1201, 100, dtype=np.float)
   unit2 = np.arange(100, 1201, 110, dtype=np.float)
   unit3 = np.arange(100, 1201, 120, dtype=np.float)
   bi_sttc = sttc.sttc(unit1, unit2, dt, ti, tf)
   
   unit_list = [unit1, unit2, unit3]
   mv_sttc = sttc.multivariate_sttc(unit_list, dt, ti, tf)


Global Synchrony Measure
========================

The Global synchrony measure is described in::

   Li et al. Synchronization measurement of multiple neuronal populations. J Neurophysiol, 2007:3341
   Patel et al. Dynamic changes in neural circuit topology following mild mechanical injury in vitro. Annals of biomedical engineering, 2012:23 
   Patel et al. Single-neuron NMDA receptor phenotype influences neuronal rewiring and reintegration following traumatic injury. J Neurosci, 2014:4200

Please make sure to cite these authors in addition to Eisenman et al. if you
use this code.

This code assumes that the spike times for each channel are in a numpy array. 
The parameter tf represent the end time of the data.
of the spike train.

.. code-block:: py3

   import numpy as np
   from burst_sync import global_sync as gs
   

   tf = 1300
   unit1 = np.arange(100, 1201, 100, dtype=np.float)
   unit2 = np.arange(100, 1201, 110, dtype=np.float)
   unit3 = np.arange(100, 1201, 120, dtype=np.float)
   unit_list = [unit1, unit2, unit3]
   sync = gs.calc_global_sync(unit_list, tf)


Tcrit, ISI_N and B Statistic
============================

The Tcrit method is described in::

   Wagenaar et al. An extremely rich repertoire of bursting patterns during the development of cortical cultures. BMC Neurosci, 2006:11

The ISI_N method is described in::

   Bakkum et al. Parameters for burst detection. Front Comput Neurosci, 2013:193

The B Statistic is described in::

   Tiesinga and Sejnowski. Rapid temporal modulation of synchrony by competition in cortical interneuron networks. Neural Comput, 2004:251
   Bogaard et al. Interaction of cellular and network mechanisms in spatiotemporal pattern formation in neuronal networks. J Neurosci, 2009:1677

Please make sure to cite the relevant authors in addition to Eisenman et al. 
if you use any of this code.

This code was written for Igor Pro. The Igor code and a demo experiment are
included in the corresponding folder. Instructions are included in the demo
experiment.


Other Credits
=============

The boilerplate code for this project was created using `PyScaffold <http://pyscaffold.readthedocs.org/en/latest/index.html>`_.

AppVeyor and Travis configurations were based on the demo projects created by
`Oliver Grisel <https://github.com/ogrisel/python-appveyor-demo.git>`_ and 
`Rob McGibbon <https://github.com/rmcgibbo/python-appveyor-conda-example.git>`_

