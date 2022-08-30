# -*- coding: utf-8 -*-

import numpy as np
import numpy.testing as npt

from burst_sync.t_crit import calc_ASDR, calc_B, find_bursts
from burst_sync.t_crit.t_crit import find_IBI


def test_calc_ASDR(baseline_data):
    ASDR = calc_ASDR(baseline_data, 1800)
    npt.assert_allclose(ASDR[:10], [30, 31, 29, 16, 30, 37, 19, 29, 20, 34])
    npt.assert_allclose(ASDR[-5:], [38, 26, 30, 23, 21])


def test_calc_B(baseline_data):
    B = calc_B(baseline_data, 1800)
    assert abs(B - 0.050442) < 1e-6


def test_find_bursts(baseline_data):
    bursts = find_bursts(baseline_data, 1800)
    npt.assert_allclose(bursts['start_time'][:10], [0.0484, 0.467, 1.1588,
                        1.5038, 1.6056, 2.4928, 2.708, 3.7044, 4.2846, 4.717])

    num_bursts = [0, 25, 0, 0, 0, 3]
    num_bursts = np.append(num_bursts, [0, 3, 0, 29, 0, 460, 0, 0])
    num_bursts = np.append(num_bursts, [0, 0, 4, 0, 12, 19, 0, 86])
    num_bursts = np.append(num_bursts, [55, 0, 2, 15, 5, 566, 0, 25])
    num_bursts = np.append(num_bursts, [0, 0, 0, 0, 80, 0, 63, 0])
    num_bursts = np.append(num_bursts, [0, 0, 0, 0, 0, 0, 303, 0])
    num_bursts = np.append(num_bursts, [168, 3, 0, 47, 6, 11, 0, 1])
    num_bursts = np.append(num_bursts, [0, 0, 326, 43, 904, 87])

    counts = bursts['channel_idx'].value_counts().sort_index()
    for i in range(len(num_bursts)):
        if i in counts:
            assert counts[i] == num_bursts[i]


def test_find_IBI(bursts):
    ibis = find_IBI(bursts, 60)
    npt.assert_allclose(ibis[20:30], [41.4588, 2.5342, 216.4758, 135.8884,
                        387.4208, 279.6726, 513.6184, 251.9698,
                        164.938, 6.95])
    assert len(ibis) == 3323
