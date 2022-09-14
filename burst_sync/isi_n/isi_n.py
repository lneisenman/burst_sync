# -*- coding: utf-8 -*-

import numpy as np
import numpy.testing as npt
import pandas as pd


def isi_n(data: pd.DataFrame, N: int = 10,
          threshold: float = 0.2) -> pd.DataFrame:
    sorted = data.sort_values('spike_time', ignore_index=True)
    times = sorted['spike_time'].values
    channels = sorted['channel'].values
    isi = times[(N-1):] - times[:-(N-1)]
    indices = np.where(isi < 0.2)[0]
    num_idx = len(indices)
    if num_idx == 0:
        raise ValueError('No bursts detected')

    columns = ['start_time', 'end_time', 'num_spikes', 'channels',
               'num_channels']
    bursts = pd.DataFrame(columns=columns)
    ii = 0
    i_burst = 0
    i_start = indices[ii]
    while ii < num_idx:
        i_end = i_start + N - 1
        while ii < num_idx - 1 and (indices[ii+1] - indices[ii] == 1):
            ii += 1
            i_end += 1

        bursts.loc[i_burst, 'start_time'] = times[i_start]
        bursts.loc[i_burst, 'end_time'] = times[i_end]
        bursts.loc[i_burst, 'num_spikes'] = i_end - i_start + 1
        chan = channels[i_start:i_end+1]
        bursts.loc[i_burst, 'channels'] = chan
        bursts.loc[i_burst, 'num_channels'] = len(np.unique(chan))
        i_burst += 1
        while ii < num_idx and indices[ii] <= i_end:
            ii += 1

        if ii < num_idx:
            i_start = indices[ii]

    return bursts
