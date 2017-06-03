# -*- coding: utf-8 -*-
"""
Python implementation of Igor tcrit burst detection code
"""

from __future__ import (print_function, division,
                        unicode_literals, absolute_import)

import numpy as np


class Burst():
    ''' dummy class to contain burst data '''
    pass


def calculate_isi(spikes):
    isi = dict()
    for key in spikes:
        isi[key] = np.diff(spikes[key])

    return isi


def calculate_bursts(spikes, tcrit=0.15):
    bursts = dict()
    intervals = calculate_isi(spikes)
    for label, spike_times in spikes.items():
        isi = intervals[label]
        num = index = 0
        start = np.zeros(0)
        end = np.zeros(0)
        num_spikes = np.zeros(0)
        while index < len(isi)-1:
            if (isi[index] < tcrit) and (isi[index+1] <= tcrit):
                start = np.append(start, spike_times[index])
                num = 3
                index += 1
                while (index < len(isi)-1) and (isi[index+1] < tcrit):
                    num += 1
                    index += 1

                end = np.append(end, spike_times[index+1])
                num_spikes = np.append(num_spikes, num)

            index += 1

        if len(start) > 0:
            burst = Burst()
            burst.start = start
            burst.end = end
            burst.num_spikes = num_spikes
            bursts[label] = burst

    return bursts


def calculate_ibi(bursts):
    ibi = dict()
    for key in bursts:
        ibi[key] = bursts[key].start[1:] - bursts[key].end[:-1]

    return ibi


def count_spikes_in_network_burst(start, end, spikes):
    num_spikes = 0
    for channel in spikes:
        test = np.logical_and(spikes[channel] >= start,
                              spikes[channel] <= end)
        index = np.where(test == True)  # test is True doesn't work
        num_spikes += len(index[0])

    return num_spikes


def calculate_network_bursts(spikes, bursts):
    burst_start = np.zeros(0)
    burst_end = np.zeros(0)
    burst_num_spikes = np.zeros(0)
    burst_channel = np.empty(0, dtype=np.int)
    nb_start = np.zeros(0)
    nb_end = np.zeros(0)
    nb_num_spikes = np.zeros(0)
    nb_num_channels = np.zeros(0)
    nb_total_spikes = np.zeros(0)
    for key in bursts:
        burst_start = np.append(burst_start, bursts[key].start)
        burst_end = np.append(burst_end, bursts[key].end)
        burst_num_spikes = np.append(burst_num_spikes, bursts[key].num_spikes)
        burst_channel = np.append(burst_channel,
                                  len(bursts[key].start)*[int(key)])

    order = np.argsort(burst_start)
    burst_num_spikes = burst_num_spikes[order].copy()
    burst_end = burst_end[order].copy()
    burst_channel = burst_channel[order].copy()
    burst_start = np.sort(burst_start)
    i = 0
    num_bursts = len(burst_start)
    while (i < num_bursts - 1):
        channels = list()
        if burst_start[i+1] <= burst_end[i]:
            # Network burst
            start = burst_start[i]
            end = burst_end[i]
            if burst_end[i+1] > end:
                end = burst_end[i+1]

            num_spikes = burst_num_spikes[i] + burst_num_spikes[i+1]
            channels.append(burst_channel[i])
            channels.append(burst_channel[i+1])
            i += 1
            while (i < num_bursts - 1) and (burst_start[i+1] < end):
                # Network burst continues
                if burst_end[i+1] > end:
                    end = burst_end[i+1]

                num_spikes += burst_num_spikes[i+1]
                channels.append(burst_channel[i+1])
                i += 1

            nb_start = np.append(nb_start, start)
            nb_end = np.append(nb_end, end)
            nb_num_spikes = np.append(nb_num_spikes, num_spikes)
            nb_num_channels = np.append(nb_num_channels, len(channels))
            total_spikes = count_spikes_in_network_burst(start, end, spikes)
            nb_total_spikes = np.append(nb_total_spikes, total_spikes)
        else:
            i += 1

    network_burst = Burst()
    network_burst.start = nb_start
    network_burst.end = nb_end
    network_burst.num_spikes = nb_num_spikes
    network_burst.num_channels = nb_num_channels
    network_burst.total_spikes = nb_total_spikes
    return network_burst


def calculate_inbi(nb):
    inbi = nb.start[1:] - nb.end[:-1]
    return inbi


def extract_times(ii):
    times = np.zeros(0)
    if not isinstance(ii, dict):
        ii = {'key': ii}

    for key in ii:
        times = np.append(times, ii[key])

    return times


def calculate_ii_stats(ii):
    ''' returns mean and std for isi, ibi or inbi '''
    times = extract_times(ii)
    return np.average(times), np.std(times)


def calculate_ii_histogram(ii, bins=50, range_=None):
    ''' returns histogram of isi, ibi or inbi times '''
    times = extract_times(ii)
    return np.histogram(times, bins=bins, range=range_)
