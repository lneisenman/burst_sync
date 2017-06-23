# -*- coding: utf-8 -*-

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from burst_sync import tcrit
import meanet

plt.style.use({'axes.spines.top': False, 'axes.spines.right': False})


def read_spikes(file_name='spikes.csv'):
    data = pd.read_csv(file_name)
    spikes = meanet.MEA()
    for key in data.keys():
        spikes[key[3:5]] = np.asarray(data[key].dropna())

    spikes.dur = 1800
    return spikes


def draw_plots():
    ''' Use Igor sample data to draw Igor plots '''
    spikes = read_spikes()
    analysis = tcrit.igor_analysis(spikes)
#    tcrit.igor_plots(spikes, analysis)
    tcrit.igor_summary_plots([analysis['summary']], ['baseline'])
    plt.show()


if __name__ == '__main__':
    draw_plots()
