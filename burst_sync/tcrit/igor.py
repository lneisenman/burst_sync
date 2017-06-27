from __future__ import (print_function, division, absolute_import,
                        unicode_literals)


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as ss

import burst_sync as bs
from burst_sync import tcrit
import meanet


def igor_analysis(mea):
    ''' perform the MEA data analysis originally coded in Igor '''
    analysis = dict()
    analysis['asdr'] = bs.asdr(mea, mea.dur)
    data = [(np.average(analysis['asdr']), np.std(analysis['asdr']),
            ss.sem(analysis['asdr']), np.NaN)]
    columns = ['ave', 'std', 'sem', 'number']
    analysis['summary'] = pd.DataFrame(data=data, index=['asdr'],
                                       columns=columns)

    analysis['B'] = bs.b_statistic(mea)

    analysis['isi'], ave, std, sem = tcrit.calculate_isi(mea)
    data = [(ave, std, sem, np.NaN)]
    isi = pd.DataFrame(index=['isi'], data=data, columns=columns)
    analysis['summary'] = analysis['summary'].append(isi)

    bursts = tcrit.calculate_bursts(mea)
    analysis['bursts'], num_bursts, dur_stats, spikes_stats, rates_stats = bursts
    data = [(np.NaN, np.NaN, np.NaN, num_bursts)]
    num = pd.DataFrame(index=['num_bursts'], data=data, columns=columns)
    data = [np.append(dur_stats, np.NaN)]
    dur = pd.DataFrame(index=['burst_dur'], data=data, columns=columns)
    data = [np.append(spikes_stats, np.NaN)]
    spikes = pd.DataFrame(index=['spikes_per_burst'], data=data,
                          columns=columns)
    data = [np.append(rates_stats, np.NaN)]
    rates = pd.DataFrame(index=['burst_spike_rate'], data=data,
                         columns=columns)
    data = [num, dur, spikes, rates]
    analysis['summary'] = analysis['summary'].append(data)

    analysis['ibi'], ave, std, sem = tcrit.calculate_ibi(analysis['bursts'])
    data = [(ave, std, sem, np.NaN)]
    ibi = pd.DataFrame(index=['ibi'], data=data, columns=columns)
    analysis['summary'] = analysis['summary'].append(ibi)

    analysis['nb'] = tcrit.calculate_network_bursts(mea, analysis['bursts'])
    data = [(np.NaN, np.NaN, np.NaN, len(analysis['nb'].start))]
    num = pd.DataFrame(index=['num_nb'], data=data, columns=columns)
    times = analysis['nb'].end - analysis['nb'].start
    data = [(np.average(times), np.std(times), ss.sem(times), np.NaN)]
    dur = pd.DataFrame(index=['nb_dur'], data=data, columns=columns)
    data = [(np.average(analysis['nb'].num_spikes),
             np.std(analysis['nb'].num_spikes),
             ss.sem(analysis['nb'].num_spikes), np.NaN)]
    spikes = pd.DataFrame(index=['nb_num_spikes'], data=data, columns=columns)
    data = [(np.average(analysis['nb'].total_spikes),
             np.std(analysis['nb'].total_spikes),
             ss.sem(analysis['nb'].total_spikes), np.NaN)]
    total = pd.DataFrame(index=['nb_total_spikes'], data=data, columns=columns)
    data = [(np.average(analysis['nb'].num_channels),
             np.std(analysis['nb'].num_channels),
             ss.sem(analysis['nb'].num_channels), np.NaN)]
    channels = pd.DataFrame(index=['nb_contacts'], data=data,
                            columns=columns)
    data = [num, dur, spikes, total, channels]
    analysis['summary'] = analysis['summary'].append(data)

    analysis['inbi'] = tcrit.calculate_inbi(analysis['nb'])
    data = [(np.average(analysis['inbi']), np.std(analysis['inbi']),
             ss.sem(analysis['inbi']), np.NaN)]
    inbi = pd.DataFrame(index=['inbi'], data=data, columns=columns)
    analysis['summary'] = analysis['summary'].append(inbi)

    return analysis


def _calc_centers(edges):
    centers = np.diff(edges) + edges[:-1]
    return centers


def igor_plots(mea, analysis):
    ''' generate plots similar to those from original Igor code '''
    plot1 = plt.figure(figsize=(10, 7))
    plt.subplot(321)
    meanet.draw_raster(mea, plot1)

    plt.subplot(323)
    time = np.arange(0, mea.dur)
    plt.plot(time, analysis['asdr'], 'r')
    plt.ylim(0, 1.1*np.max(analysis['asdr']))
    plt.xlabel('Time (s)')
    plt.ylabel('ASDR (Spikes per second)')

    plt.subplot(325)
    bins = np.arange(0, 10, 0.02)
    hist, edges = tcrit.calculate_ii_histogram(analysis['isi'], bins)
    centers = _calc_centers(edges)
    plt.semilogy(centers, hist, 'ok', mfc='none')
    plt.xlabel('Interspike Interval (s)')
    plt.ylabel('Number')

    plt.subplot(322)
    durations = tcrit.calculate_burst_durations(analysis['bursts'])
    bins = np.arange(0, 5, 0.05)
    hist, edges = np.histogram(durations, bins=bins)
    centers = _calc_centers(edges)
    plt.semilogy(centers, hist, 'ok', mfc='none')
    plt.xlabel('Burst Duration (s)')
    plt.ylabel('Number')

    plt.subplot(324)
    hist, edges = tcrit.calculate_ii_histogram(analysis['ibi'], bins)
    centers = _calc_centers(edges)
    plt.semilogy(centers, hist, 'ok', mfc='none')
    plt.xlabel('Inter Burst Interval (s)')
    plt.ylabel('Number')

    plt.tight_layout()

    plot2 = plt.figure(figsize=(10, 7))
    plt.subplot(321)
    bins = np.arange(0, 150, 5)
    hist, edges = tcrit.calculate_ii_histogram(analysis['inbi'], bins)
    centers = _calc_centers(edges)
    plt.semilogy(centers, hist, 'ok', mfc='none')
    plt.xlabel('Inter Network Burst Interval (s)')
    plt.ylabel('Number')

    plt.subplot(322)
    durations = analysis['nb'].end - analysis['nb'].start
    bins = np.arange(0, 5, 0.1)
    hist, edges = np.histogram(durations, bins=bins)
    centers = _calc_centers(edges)
    plt.semilogy(centers, hist, 'ok', mfc='none')
    plt.xlabel('Network Burst Duration (s)')
    plt.ylabel('Number')

    plt.subplot(323)
    bins = np.arange(0, 60, 1)
    hist, edges = np.histogram(analysis['nb'].num_channels, bins=bins)
    centers = _calc_centers(edges)
    plt.plot(centers, hist, 'ok', mfc='none')
    plt.xlabel('Contacts per Network Burst')
    plt.ylabel('Number')

    plt.tight_layout()

    return plot1, plot2


def igor_summary_plots(data, labels):
    ''' generate summary bar-plots

    data is a list of Pandas DataFrames containing summary data for each
    dataset included in the summary

    labels is a list of names for the columns in the plots (e.g. the names of
    the experiments)
    '''
    num_points = len(data)
    columns = np.arange(num_points)

    asdr = np.zeros(num_points)
    asdr_sem = np.zeros(num_points)
    num_bursts = np.zeros(num_points)
    burst_dur = np.zeros(num_points)
    burst_dur_sem = np.zeros(num_points)
    spikes_per_burst = np.zeros(num_points)
    spikes_per_burst_sem = np.zeros(num_points)
    burst_spike_rate = np.zeros(num_points)
    burst_spike_rate_sem = np.zeros(num_points)
    ibi = np.zeros(num_points)
    ibi_sem = np.zeros(num_points)

    num_nb = np.zeros(num_points)
    nb_dur = np.zeros(num_points)
    nb_dur_sem = np.zeros(num_points)
    nb_total_spikes = np.zeros(num_points)
    nb_total_spikes_sem = np.zeros(num_points)
    nb_contacts = np.zeros(num_points)
    nb_contacts_sem = np.zeros(num_points)
    inbi = np.zeros(num_points)
    inbi_sem = np.zeros(num_points)

    for i, df in enumerate(data):
        asdr[i] = df.loc['asdr', 'ave']
        asdr_sem[i] = df.loc['asdr', 'sem']
        num_bursts[i] = df.loc['num_bursts', 'number']
        burst_dur[i] = df.loc['burst_dur', 'ave']
        burst_dur_sem[i] = df.loc['burst_dur', 'sem']
        spikes_per_burst[i] = df.loc['spikes_per_burst', 'ave']
        spikes_per_burst_sem[i] = df.loc['spikes_per_burst', 'sem']
        burst_spike_rate[i] = df.loc['burst_spike_rate', 'ave']
        burst_spike_rate_sem[i] = df.loc['burst_spike_rate', 'sem']
        ibi[i] = df.loc['ibi', 'ave']
        ibi_sem[i] = df.loc['ibi', 'sem']

        num_nb[i] = df.loc['num_nb', 'number']
        nb_dur[i] = df.loc['nb_dur', 'ave']
        nb_dur_sem[i] = df.loc['nb_dur', 'sem']
        nb_total_spikes[i] = df.loc['nb_total_spikes', 'ave']
        nb_total_spikes_sem[i] = df.loc['nb_total_spikes', 'sem']
        nb_contacts[i] = df.loc['nb_contacts', 'ave']
        nb_contacts_sem[i] = df.loc['nb_contacts', 'sem']
        inbi[i] = df.loc['inbi', 'ave']
        inbi_sem[i] = df.loc['inbi', 'sem']

    plot1 = plt.figure(figsize=(10, 7))
    plt.subplot(321)
    plt.bar(columns, asdr, yerr=asdr_sem, tick_label=labels, color='k',
            capsize=10)
    plt.ylabel('ASDR')

    plt.subplot(323)
    plt.bar(columns, num_bursts, tick_label=labels, color='k')
    plt.ylabel('Number of Bursts')

    plt.subplot(325)
    plt.bar(columns, burst_dur, yerr=burst_dur_sem, tick_label=labels,
            color='k', capsize=10)
    plt.ylabel('Burst Duration (s)')

    plt.subplot(326)
    plt.bar(columns, spikes_per_burst, yerr=spikes_per_burst_sem,
            tick_label=labels, color='k', capsize=10)
    plt.ylabel('Spikes per Burst')

    plt.subplot(324)
    plt.bar(columns, burst_spike_rate, yerr=burst_spike_rate_sem,
            tick_label=labels, color='k', capsize=10)
    plt.ylabel('Burst Spike Rate (spikes/s)')

    plt.subplot(322)
    plt.bar(columns, ibi, yerr=ibi_sem, tick_label=labels, color='k',
            capsize=10)
    plt.ylabel('Inter-burst Interval (s)')

    plt.tight_layout()

    plot2 = plt.figure(figsize=(10, 7))
    plt.subplot(321)
    plt.bar(columns, num_nb, tick_label=labels, color='k')
    plt.ylabel('Number of Network Bursts')

    plt.subplot(323)
    plt.bar(columns, nb_dur, yerr=nb_dur_sem, tick_label=labels, color='k',
            capsize=10)
    plt.ylabel('Network Burst Duration (s)')

    plt.subplot(322)
    plt.bar(columns, nb_total_spikes, yerr=nb_total_spikes_sem,
            tick_label=labels, color='k', capsize=10)
    plt.ylabel('Spikes per Network Burst')

    plt.subplot(324)
    plt.bar(columns, nb_contacts, yerr=nb_contacts_sem,
            tick_label=labels, color='k', capsize=10)
    plt.ylabel('Contacts per Network Burst')

    plt.subplot(325)
    plt.bar(columns, inbi, yerr=inbi_sem, tick_label=labels, color='k',
            capsize=10)
    plt.ylabel('Inter Network Burst Interval (s)')

    plt.tight_layout()

    return plot1, plot2