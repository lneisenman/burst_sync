# -*- coding: utf-8 -*-

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

plt.style.use({'axes.spines.top': False, 'axes.spines.right': False})

from burst_sync import isin


@pytest.fixture(scope='module')
def read_spikes():
    file_name = 'tests/spikes.csv'
    data = pd.read_csv(file_name)
    spikes = dict()
    for key in data.keys():
        spikes[key[3:5]] = np.asarray(data[key].dropna())

    return spikes


@pytest.fixture(scope='module')
def read_bursts():
    file_name = 'tests/isin_bursts.csv'
    bursts = pd.read_csv(file_name)
    return bursts


def test_find_isin(read_spikes, read_bursts):
    bursts = isin.find_bursts(read_spikes)
    igor = read_bursts
    np.testing.assert_allclose(bursts.start, igor.start)
    np.testing.assert_allclose(bursts.end, igor.end)
    np.testing.assert_allclose(bursts.num_contacts, igor.num_contacts)
    np.testing.assert_allclose(bursts.num_spikes, igor.num_spikes)


if __name__ == '__main__':
    bursts = isin.find_bursts(read_spikes())
    plot = isin.summary_plot([bursts], ['baseliine'])
    plt.show()
