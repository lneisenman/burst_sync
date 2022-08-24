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
    B: float = ((np.sqrt(tsq_bar - t_bar**2)/t_bar) - 1)/np.sqrt(num_channels)

    return B


def find_bursts(data: list, end_time: float,
                t_crit: float = 0.15) -> pd.DataFrame:
    ''' bursts are defined as two or more sequential interspike intervals
        less than t_crit '''
    columns = ['channel_idx', 'start_time', 'end_time', 'num_spikes']
    bursts = pd.DataFrame(columns=columns)
    isi_list = [np.diff(ch) if len(ch) > 2 else np.zeros(0) for ch in data]
    for ch_idx, isi in enumerate(isi_list):
        if len(isi) > 1:
            idx = np.where(isi <= t_crit)[0]
            i = 0
            while (i < len(idx)-2):
                j = i + 1
                while ((idx[j] - idx[j-1] == 1) and (j < len(idx)-1)):
                    j += 1

                if j - i > 1:
                    burst = {'channel_idx': ch_idx,
                             'start_time': data[ch_idx][idx[i]],
                             'end_time': data[ch_idx][idx[j-1]+1],
                             'num_spikes': j - i + 1}
                    temp = pd.DataFrame(data=burst, index=[0])
                    bursts = pd.concat((bursts, temp), axis=0,
                                       ignore_index=True)

                i = j

    bursts = bursts.sort_values(by=['start_time'])
    return bursts
