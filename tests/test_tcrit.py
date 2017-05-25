# -*- coding: utf-8 -*-

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)


import numpy as np
import pandas as pd


from burst_sync import tcrit


def read_spikes(file_name='tests/spikes.csv'):
    data = pd.read_csv(file_name)
    spikes = dict()
    for key in data.keys():
        spikes[key[3:5]] = np.asarray(data[key].dropna())

    return spikes


def read_igor_bursts(file_name='tests/bursts.csv'):
    data = pd.read_csv(file_name)
    bursts = dict()
    count = 0
    for i in range(0, data.shape[1], 2):
        burst_data = tcrit.Burst()
        label = data.keys()[i]
        burst_data.start = np.asarray(data[label].dropna())
        count += len(burst_data.start)
        label = data.keys()[i+1]
        burst_data.end = np.asarray(data[label].dropna())
        bursts[data.keys()[i][3:5]] = burst_data

#    print('Number of Igor bursts =', count)
    return bursts


def compare_data(set1, set2):
    for key in set1:
        np.testing.assert_allclose(set1[key].start, set2[key].start)
        np.testing.assert_allclose(set1[key].end, set2[key].end)


def compare_num_spikes_in_bursts(bursts,
                                 file_name='tests/numSpikesInBurst.csv'):
    data = pd.read_csv(file_name)
#    print(data.tail())
    igor = np.asarray(data['numSpikesInBurst'].dropna())
    num_spikes = np.zeros(0)
    keys = sorted(list(bursts.keys()))
    for key in keys:
        num_spikes = np.append(num_spikes, bursts[key].num_spikes)

#    print(len(igor), len(num_spikes))
#    df = pd.DataFrame({'numSpikesInBurst': num_spikes})
#    df.head()
#    df.to_csv(file_name)
    np.testing.assert_allclose(igor, num_spikes)


def test_tcrit():
    """ Use Igor sample data to test python tcrit functions"""
    spikes = read_spikes()
    bursts = tcrit.calculate_bursts(spikes)
    igor_bursts = read_igor_bursts()
    compare_data(bursts, igor_bursts)
    compare_num_spikes_in_bursts(bursts)


if __name__ == '__main__':
    spikes = read_spikes('spikes.csv')
    bursts = tcrit.calculate_bursts(spikes)
    test = '46'
#    print(bursts[test].start, bursts[test].end)
    igor = read_igor_bursts('bursts.csv')
#    print(igor[test].start, igor[test].end)
#    for i in range(len(bursts[test].start)):
#        print(i, bursts[test].start[i], igor[test].start[i])
#    for key in bursts.keys():
#        print(key)
#        print(len(bursts[key].start), len(igor[key].start))
#        print(bursts[key].start[-1], igor[key].start[-1])
#        print()

#    print(igor['17'].start, igor['17'].end)
#    print(bursts['13'].num_spikes[:10])
    compare_num_spikes_in_bursts(bursts, 'numSpikesInBurst.csv')
