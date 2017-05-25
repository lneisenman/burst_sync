# -*- coding: utf-8 -*-

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)


import numpy as np
import pandas as pd


import burst_sync as bs


def read_spikes(file_name='tests/spikes.csv'):
    data = pd.read_csv(file_name)
    spikes = dict()
    for key in data.keys():
        spikes[key[3:5]] = np.asarray(data[key].dropna())

    return spikes


def test_b_stat(file_name='tests/ASDR+B.csv'):
    ''' Use Igor sample data to test python asdr function '''
    spikes = read_spikes()
    b = bs.b_statistic(spikes)
    df = pd.read_csv(file_name)
    igor = np.asarray(df['B'].dropna())
    assert np.abs(igor[0] - b) < 1e-6


if __name__ == '__main__':
    test_b_stat('ASDR+B.csv')
