# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import pytest

import burst_sync
from burst_sync.t_crit import calc_ASDR, calc_ISI_hist


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
def ASDR(baseline_data):
    return calc_ASDR(baseline_data, 1800)


@pytest.fixture
def bursts(baseline_data):
    return burst_sync.t_crit.find_bursts(baseline_data, 1800)


@pytest.fixture
def isi(baseline_data):
    return burst_sync.t_crit.calc_ISI(baseline_data)


@pytest.fixture
def isi_histogram(isi):
    return calc_ISI_hist(isi)


@pytest.fixture
def isi_hist(isi_histogram):
    return isi_histogram[0]


@pytest.fixture
def isi_edges(isi_histogram):
    return isi_histogram[1]


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


@pytest.fixture
def rgs_data():
    data1 = pd.read_csv('tests/data/rgs/testdata1.csv')
    data2 = pd.read_csv('tests/data/rgs/testdata2.csv')
    data3 = pd.read_csv('tests/data/rgs/testdata3.csv')
    return [data1, data2, data3]


@pytest.fixture
def rgs_bursts():
    bursts1 = pd.read_csv('tests/data/rgs/output_b1.csv')
    bursts2 = pd.read_csv('tests/data/rgs/output_b2.csv')
    bursts3 = pd.read_csv('tests/data/rgs/output_b3.csv')
    bursts3['id'] = bursts3['id'].astype(np.int32)
    bursts3['clusid'] = bursts3['clusid'].astype(np.int32)
    return [bursts1, bursts2, bursts3]


@pytest.fixture
def rgs_pauses():
    pauses1 = pd.read_csv('tests/data/rgs/output_p1.csv')
    pauses2 = pd.read_csv('tests/data/rgs/output_p2.csv')
    pauses2['id'] = pauses2['id'].astype(np.int32)
    pauses2['clusid'] = pauses2['clusid'].astype(np.int32)
    pauses3 = pd.read_csv('tests/data/rgs/output_p3.csv')
    pauses3['id'] = pauses3['id'].astype(np.int32)
    pauses3['clusid'] = pauses3['clusid'].astype(np.int32)
    return [pauses1, pauses2, pauses3]
