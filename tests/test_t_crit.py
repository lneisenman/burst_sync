# -*- coding: utf-8 -*-

import numpy.testing as npt

from burst_sync.t_crit import calc_ASDR, calc_B, find_bursts


def test_calc_ASDR(baseline):
    ASDR = calc_ASDR(baseline, 1800)
    npt.assert_allclose(ASDR[:10], [30, 31, 29, 16, 30, 37, 19, 29, 20, 34])
    npt.assert_allclose(ASDR[-5:], [38, 26, 30, 23, 21])


def test_calc_B(baseline):
    B = calc_B(baseline, 1800)
    assert abs(B - 0.050442) < 1e-6


def test_find_bursts(baseline):
    bursts = find_bursts(baseline, 1800)
    npt.assert_allclose(bursts['start_time'][:10], [0.0484, 0.467, 1.1588,
                        1.5038, 1.6056, 2.4928, 2.708, 3.7044, 4.2846, 4.717])
