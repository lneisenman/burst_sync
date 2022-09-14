# -*- coding: utf-8 -*-

import numpy as np
import numpy.testing as npt
import pandas as pd

from burst_sync.isi_n import isi_n


def test_isi_n(baseline_names, baseline_data):
    data = pd.DataFrame(columns=['channel', 'spike_time'])
    for channel, times in zip(baseline_names, baseline_data):
        df = pd.DataFrame(columns=['channel', 'spike_time'])
        df['spike_time'] = times
        df['channel'] = channel
        data = pd.concat([data, df])

    bursts = isi_n(data)
    start_times = [1.4612, 1.729, 2.4462, 2.6612, 4.2364, 5.0568,
                   5.7574, 6.1146, 7.256, 8.8958]
    end_times = [1.6392, 1.8992, 2.6028, 2.9016, 4.4658, 5.3732,
                 5.9618, 6.2646, 7.4538, 9.0684]
    num_spikes = [10, 11, 10, 11, 14, 16, 12, 13, 11, 10]
    num_channels = [5, 9, 7, 5, 7, 7, 8, 12, 7, 5]

    npt.assert_allclose(bursts['start_time'].astype(float).values[:10],
                        start_times)
    npt.assert_allclose(bursts['end_time'].astype(float).values[:10],
                        end_times)
    npt.assert_allclose(bursts['num_spikes'].astype(int).values[:10],
                        num_spikes)
    npt.assert_allclose(bursts['num_channels'].astype(int).values[:10],
                        num_channels)
