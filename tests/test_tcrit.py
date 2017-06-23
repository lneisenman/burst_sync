# -*- coding: utf-8 -*-

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)


import numpy as np
import pandas as pd
import pytest


from burst_sync import tcrit


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
    file_name = 'tests/bursts.csv'
    data = pd.read_csv(file_name)
    bursts = dict()
    for i in range(0, data.shape[1], 3):
        burst_data = tcrit.Burst()
        label = data.keys()[i]
        burst_data.start = np.asarray(data[label].dropna())
        label = data.keys()[i+1]
        burst_data.end = np.asarray(data[label].dropna())
        label = data.keys()[i+2]
        burst_data.num_spikes = np.asarray(data[label].dropna())
        bursts[data.keys()[i][:2]] = burst_data

#    print('Number of Igor bursts =', count)
    return bursts


@pytest.fixture(scope='module')
def read_ibi():
    file_name = 'tests/ibi.csv'
    data = pd.read_csv(file_name)
    ibi = dict()
    for key in data:
        ibi[key] = np.asarray(data[key].dropna())

    return ibi


@pytest.fixture(scope='module')
def read_network_bursts():
    file_name = 'tests/networkBursts.csv'
    nb = pd.read_csv(file_name)
    return nb


def test_calculate_ibi(read_bursts, read_ibi):
    ibi = tcrit.calculate_ibi(read_bursts)[0]
    for key in ibi:
        np.testing.assert_allclose(ibi[key], read_ibi[key])


def test_tcrit_bursts(read_spikes, read_bursts):
    ''' Use Igor sample data to test python tcrit burst functions '''
    bursts = tcrit.calculate_bursts(read_spikes)[0]
    for key in bursts:
        np.testing.assert_allclose(bursts[key].start, read_bursts[key].start)
        np.testing.assert_allclose(bursts[key].end, read_bursts[key].end)
        np.testing.assert_allclose(bursts[key].num_spikes,
                                   read_bursts[key].num_spikes)


def test_tcrit_network_bursts(read_spikes, read_bursts, read_network_bursts):
    ''' Use Igor sample data to test python tcrit network burst functions '''
    nb = tcrit.calculate_network_bursts(read_spikes, read_bursts)
    np.testing.assert_allclose(read_network_bursts['start'], nb.start)
    np.testing.assert_allclose(read_network_bursts['end'], nb.end)
    np.testing.assert_allclose(read_network_bursts['num_spikes'],
                               nb.num_spikes)
    np.testing.assert_allclose(read_network_bursts['num_channels'],
                               nb.num_channels)
    np.testing.assert_allclose(read_network_bursts['total_spikes'],
                               nb.total_spikes)
