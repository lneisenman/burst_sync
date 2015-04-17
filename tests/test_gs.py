# -*- coding: utf-8 -*-
"""
use Kreuz spikes from Fig 2B to test global_sync code
"""

from __future__ import print_function, division


import numpy as np
import numpy.testing as nptest
import pandas as pd

from burst_sync import global_sync as gs


def test_get_phase_spikes():
    spikes = np.round(pd.read_csv('tests/test_data.csv').values[:, 1])
    spikes[0] = 2
    phase = gs.get_phase_spikes(spikes, 4000)

    # kreuz_phase.csv from running Matlab code
    result = pd.read_csv('tests/kreuz_phase.csv', header=None)[0].values
    nptest.assert_allclose(phase[:-1], result[:-1])     # last value is random


def test_calc_global_sync():
    spikes = np.round(pd.read_csv('tests/test_data.csv').values[:, 1:])
    (M, N) = spikes.shape

    # Matlab code assumed unique integer spike times
    spikes[spikes == 0] = 2
    for i in range(M):
        for j in range(N-1):
            if spikes[i, j] == spikes[i, j+1]:
                spikes[i, j+1] += 1

    spike_list = [list(spikes[:, i]) for i in range(N)]
    sync = gs.calc_global_sync(spike_list, 4000)
    SI = (20.632722 - 1)/(N - 1)    # 20.63 from running Matlab code
    nptest.assert_allclose(sync, SI, atol=.001)
