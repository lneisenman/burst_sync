from __future__ import (print_function, division, absolute_import,
                        unicode_literals)


import numpy as np


def b_statistic(data):
    ''' Python implementation of Igor B statistic code '''
    times = np.zeros(0)
    for key in data:
        times = np.append(times, data[key])

    times = np.sort(times)
    isi = np.diff(times)
    isi_sq = isi**2

    t_bar = np.average(isi)
    tsq_bar = np.average(isi_sq)
    b_stat = ((np.sqrt(tsq_bar - t_bar**2)/t_bar) - 1)/np.sqrt(len(data))
    return b_stat
