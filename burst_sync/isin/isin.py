# -*- coding: utf-8 -*-
"""
Python implementation of Igor ISI_N burst detection code
"""

from __future__ import (print_function, division,
                        unicode_literals, absolute_import)

from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as ss


def find_bursts(spikes, N=10, threshold=0.2):
    times = np.zeros(0)
    contacts = np.zeros(0)
    for key in spikes:
        times = np.append(times, spikes[key])
        contacts = np.append(contacts, [int(key)]*len(spikes[key]))

    order = np.argsort(times)
    times.sort()
    contacts = contacts[order].copy()

    isin = times[(N-1):] - times[:-(N-1)]
    start = np.zeros(0)
    end = np.zeros(0)
    num_contacts = np.zeros(0)
    num_spikes = np.zeros(0)
    i = 0
    last = len(isin)

    while i < last:
        if isin[i] < threshold:    # start burst
            start = np.append(start, times[i])
            count = 10
            i += 1
            while isin[i] < threshold:
                count += 1
                i += 1

            idx = i + N - 2
            end = np.append(end, times[idx])
            unique = len(np.unique(contacts[idx-count+1:idx+1]))
            num_contacts = np.append(num_contacts, unique)
            num_spikes = np.append(num_spikes, count)
            i += N-1    # advance past end of burst
        else:
            i += 1

    if len(start) > 0:
        data = (start, end, num_contacts, num_spikes)
        data = OrderedDict([('start', start), ('end', end),
                            ('num_contacts', num_contacts),
                            ('num_spikes', num_spikes)])
        df = pd.DataFrame(data=data)
        return df
    else:
        return None


def summary_plot(data, labels):
    num_points = len(data)
    num_bursts = np.zeros(num_points)
    dur = np.zeros(num_points)
    dur_sem = np.zeros(num_points)
    num_contacts = np.zeros(num_points)
    num_contacts_sem = np.zeros(num_points)
    num_spikes = np.zeros(num_points)
    num_spikes_sem = np.zeros(num_points)

    for i, dataset in enumerate(data):
        burst_dur = dataset.end - dataset.start
        num_bursts[i] = len(burst_dur)
        dur[i] = np.average(burst_dur)
        dur_sem[i] = ss.sem(burst_dur)
        num_contacts[i] = np.average(dataset.num_contacts)
        num_contacts_sem[i] = ss.sem(dataset.num_contacts)
        num_spikes[i] = np.average(dataset.num_spikes)
        num_spikes_sem[i] = ss.sem(dataset.num_spikes)

    columns = np.arange(num_points)
    plot1 = plt.figure(figsize=(10, 7))
    plt.subplot(221)
    plt.bar(columns, num_bursts, tick_label=labels, color='k')
    plt.ylabel('Number of Bursts')

    plt.subplot(222)
    plt.bar(columns, dur, tick_label=labels, yerr=dur_sem, color='k',
            capsize=10)
    plt.ylabel('Burst Duration (s)')

    plt.subplot(223)
    plt.bar(columns, num_contacts, tick_label=labels, yerr=num_contacts_sem,
            color='k', capsize=10)
    plt.ylabel('Contacts per Burst')

    plt.subplot(224)
    plt.bar(columns, num_spikes, tick_label=labels, yerr=num_spikes_sem,
            color='k', capsize=10)
    plt.ylabel('Spikes per Burst')

    plt.suptitle('ISI_N Burst Parameters')
    plt.tight_layout()

    return plot1
