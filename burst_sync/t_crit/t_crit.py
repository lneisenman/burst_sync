# -*- coding: utf-8 -*-

import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy import optimize as opt


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


def calc_ISI(data: list) -> npt.NDArray:
    isi = np.zeros(0)
    for channel in data:
        if len(channel) > 1:
            isi = np.append(isi, np.diff(channel))

    return isi


def calc_ISI_hist(isi: npt.NDArray, bins: int = 500,
                  _range: int = 10) -> tuple[npt.NDArray, npt.NDArray]:
    hist, edges = np.histogram(isi, bins=bins, range=(0, _range))
    total = np.sum(hist)
    hist = hist/total
    midpts = edges[:-1] + (edges[1] - edges[0])/2
    return hist, midpts


def double_exp(x: float, a0: float, a1: float, a2: float,
               tau1: float, tau2: float) -> float:
    return a0 + a1*np.exp(-x/tau1) + a2*np.exp(-x/tau2)   # type: ignore


def fit_ISI_hist(hist: npt.NDArray, edges: npt.NDArray,
                 sp: int = 1) -> tuple[npt.NDArray, npt.NDArray]:
    p0 = [0.01, 0.01, 0.01, 0.1, 1]
    weights = np.sqrt(hist)
    zeros = np.where(weights == 0)[0]
    weights[zeros] = 1
    params, cov = opt.curve_fit(double_exp, xdata=edges[sp:], ydata=hist[sp:],
                                p0=p0, sigma=weights[sp:])
    return params, cov


def calc_t_crit(tau1: float, tau2: float) -> float:
    def _t_crit_fcn(t: float, tau: list) -> float:
        return float(1 - np.exp(-t/tau[0]) - np.exp(-t/tau[1]))

    result = opt.root_scalar(_t_crit_fcn, method='brentq',
                             bracket=[tau1, tau2],
                             args=[tau1, tau2])
    if result.converged:
        return result.root    # type: ignore
    else:
        raise ValueError('failed to converge')


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
            while (i < len(idx)-1):
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
                elif (idx[j] - idx[j-1] == 1) and (j == len(idx) - 1):
                    burst = {'channel_idx': ch_idx,
                             'start_time': data[ch_idx][idx[i]],
                             'end_time': data[ch_idx][idx[j-1]+1],
                             'num_spikes': 3}
                    temp = pd.DataFrame(data=burst, index=[0])
                    bursts = pd.concat((bursts, temp), axis=0,
                                       ignore_index=True)

                i = j

    bursts = bursts.sort_values(by=['start_time'])
    bursts.reset_index(drop=True, inplace=True)
    return bursts


def calc_IBI(bursts: pd.DataFrame, num_channels: int) -> npt.ArrayLike:
    ibis = np.zeros(0)
    grouped = bursts.groupby(['channel_idx'])
    for channel in range(num_channels):
        name = 'channel_' + str(channel+1)
        ibi = np.zeros(0)
        if channel in bursts['channel_idx'].values:
            df = grouped.get_group(channel)
            ibi = df['start_time'][1:].values - df['end_time'][:-1].values
            ibis = np.append(ibis, ibi)

    return ibis


def find_NB(bursts: pd.DataFrame) -> pd.DataFrame:
    columns = ['start_time', 'end_time', 'num_channels',
               'num_spikes', 'channels']
    nb = pd.DataFrame(columns=columns)
    nb['channels'] = nb['channels'].astype(object)
    i = 0
    num_nb = 0
    while i < len(bursts) - 1:
        if bursts['start_time'][i+1] < bursts['end_time'][i]:
            nb.at[num_nb, 'start_time'] = bursts['start_time'][i]
            end = bursts['end_time'][i+1] if bursts['end_time'][i+1] > \
                bursts['end_time'][i] else bursts['end_time'][i]
            num_channels = 2
            num_spikes = (bursts['num_spikes'][i] +
                          bursts['num_spikes'][i+1])
            channels = [bursts['channel_idx'][i],
                        bursts['channel_idx'][i+1]]
            i += 1
            while ((i < len(bursts) - 1) and
                   (bursts['start_time'][i+1] <= end)):
                i += 1
                if bursts['end_time'][i] > end:
                    end = bursts['end_time'][i]
                num_channels += 1
                num_spikes += bursts['num_spikes'][i]
                channels.append(bursts['channel_idx'][i])

            nb.at[num_nb, 'end_time'] = end
            nb.at[num_nb, 'num_channels'] = num_channels
            nb.at[num_nb, 'num_spikes'] = num_spikes
            nb.at[num_nb, 'channels'] = channels
            num_nb += 1
        else:
            i += 1

    return nb


def calc_INBI(nb: pd.DataFrame) -> npt.ArrayLike:
    inbi: npt.NDArray = nb['end_time'][1:].values - \
                        nb['start_time'][:-1].values
    return inbi.astype(float)
