# -*- coding: utf-8 -*-
"""
Python implementation of Igor tcrit burst detection code
"""

from __future__ import (print_function, division,
                        unicode_literals, absolute_import)

import numpy as np
import pandas as pd


class Burst():
    ''' dummy class to contain burst data '''
    pass


def calculate_bursts(data, tcrit=0.15):
    bursts = dict()
    for label, spike_times in data.items():
        isi = np.diff(spike_times)
#        if label == '76':
#            print(isi)
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
