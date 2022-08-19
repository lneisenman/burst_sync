# -*- coding: utf-8 -*-

import numpy as np

from burst_sync.rgs.R import quantile7, quantile8

x = np.linspace(1, 25, 25)
q = np.asarray([0.05, 0.95])


def test_quantile7():
    np.testing.assert_allclose(quantile7(x, q), [2.2, 23.8])


def test_quantile8():
    np.testing.assert_allclose(quantile8(x, q), [1.6, 24.4])
