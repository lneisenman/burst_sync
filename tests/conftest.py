# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import pytest

import burst_sync


@pytest.fixture
def baseline():
    data = pd.DataFrame()
    files = ['tests/baseline/ch_1.txt', 'tests/baseline/ch_2.txt',
             'tests/baseline/ch_3.txt', 'tests/baseline/ch_4.txt',
             'tests/baseline/ch_5.txt', 'tests/baseline/ch_6.txt',
             'tests/baseline/ch_7.txt', 'tests/baseline/ch_8.txt']
    for fn in files:
        df = pd.read_table(fn)
        data = pd.concat([data, df], axis=1, ignore_index=True)

    names = data.columns.values.tolist()
    return names, [data[col].dropna().values for col in names]


@pytest.fixture
def baseline_names(baseline):
    return baseline[0]


@pytest.fixture
def baseline_data(baseline):
    return baseline[1]


@pytest.fixture
def bursts(baseline_data):
    return burst_sync.t_crit.find_bursts(baseline_data, 1800)


@pytest.fixture
def nb(bursts):
    return burst_sync.t_crit.find_NB(bursts)


@pytest.fixture
def Kreuz_spikes():
    return np.round(pd.read_csv('tests/data/test_data.csv').values[:, 1:])


@pytest.fixture
def Kreuz_spikes_1(Kreuz_spikes):
    temp = Kreuz_spikes[:, 0]
    temp[0] = 2
    return temp


@pytest.fixture
def Kreuz_phase():
    ''' from running Matlab code '''
    return pd.read_csv('tests/data/kreuz_phase.csv', header=None)[0].values
