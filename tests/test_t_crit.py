# -*- coding: utf-8 -*-

import numpy.testing as npt

from burst_sync.t_crit import calc_ASDR, calc_B


def test_calc_ASDR(baseline):
    ASDR = calc_ASDR(baseline, 1800)
    npt.assert_allclose(ASDR[:10], [30, 31, 29, 16, 30, 37, 19, 29, 20, 34])
    npt.assert_allclose(ASDR[-5:], [38, 26, 30, 23, 21])


def test_calc_B(baseline):
    B = calc_B(baseline, 1800)
    assert abs(B - 0.050442) < 1e-6
