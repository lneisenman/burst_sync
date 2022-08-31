# -*- coding: utf-8 -*-

import numpy as np
import numpy.testing as npt

from burst_sync.t_crit import (calc_ASDR, calc_B, find_bursts, calc_IBI,
                               find_NB, calc_INBI)


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


def test_calc_IBI(bursts):
    ibis = calc_IBI(bursts, 60)
    npt.assert_allclose(ibis[20:30], [41.4588, 2.5342, 216.4758, 135.8884,
                        387.4208, 279.6726, 513.6184, 251.9698,
                        164.938, 6.95])
    assert len(ibis) == 3323


def test_find_NB(bursts):
    nb = find_NB(bursts)
    npt.assert_allclose(nb['start_time'][:5].values.astype(float),
                        [1.5038, 2.4928, 6.9004, 8.8958, 10.2652])
    npt.assert_allclose(nb['end_time'][:5].values.astype(float),
                        [1.729, 3.0752, 7.1522, 9.1818, 11.2562])

    npt.assert_allclose(nb['start_time'][-5:].values.astype(float),
                        [1777.9236, 1788.6382, 1790.9318, 1795.1072, 1795.792])
    npt.assert_allclose(nb['end_time'][-5:].values.astype(float),
                        [1778.1976, 1789.392, 1791.3643, 1795.24, 1796.0815])


def test_calc_INBI(nb):
    inbi = calc_INBI(nb)
    npt.assert_allclose(inbi[:10], [1.5714, 4.6594, 2.2814, 2.3604, 1.5836,
                                    3.0212, 3.0158, 2.0138, 1.1938, 3.0352])
    npt.assert_allclose(inbi[-10:], [1.6338, 5.0902, 3.0026, 1.2164,
                                     0.8892, 4.6912, 11.4684, 2.726,
                                     4.3082, 0.9744])
