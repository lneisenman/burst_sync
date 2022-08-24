# -*- coding: utf-8 -*-

import numpy as np
import numpy.typing as npt
import pandas as pd


def calc_ASDR(data: list, end_time: int) -> npt.NDArray:
    ''' This function calculates the array-wide spike detection rate
        Wagenaar et al BMC Neuroscience 7:11 2006 '''

    ASDR = np.zeros(end_time, dtype=int)
    for channel in data:
        for spike in channel:
            ASDR[int(spike)] += 1

    return ASDR


def calc_B(data: list, end_time: float) -> float:
    ''' This function calculates the interspike synchrony measure
        called B in Bogaard J Neurosci 2009
        that was taken from Tiesinga and Sejnowski  Neural Computation 2004.
        The value is zero for asynchronous activity
        and 1 for completely synchronous activity. '''

    num_channels = 0
    num_spikes = 0
    spike_list = np.zeros(0)
    for channel in data:
        if len(channel) > 0:
            num_channels += 1
            num_spikes += len(channel)
            spike_list = np.concatenate((spike_list, channel))

    spike_list.sort()
    isi = np.diff(spike_list)
    isi_time = (spike_list[:-1] + spike_list[1:])/2
    isi_sq = isi**2
    t_bar = np.mean(isi)
    tsq_bar = np.mean(isi_sq)

    return ((np.sqrt(tsq_bar - t_bar**2)/t_bar) -1)/np.sqrt(num_channels)


def find_bursts():
    pass
