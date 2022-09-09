# -*- coding: utf-8 -*-

from string import whitespace
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd

from burst_sync.t_crit import fit_ISI_hist, double_exp


def raster_plot(spike_list: list, end_time: float,
                ax: plt.Axes | None = None) -> None:
    plt.style.use({'axes.spines.top': False, 'axes.spines.right': False})
    if ax is None:
        __, ax = plt.subplots(1, 1)

    for i, channel in enumerate(spike_list):
        ax.plot(channel, [i]*len(channel), 'k|')

    ax.set_xlim([0, int(end_time + 1)])
    ax.set_xlabel('sec')
    ax.set_ylabel('Contact')


def ASDR_plot(ASDR: npt.NDArray, end_time: float,
              ax: plt.Axes | None = None) -> None:
    plt.style.use({'axes.spines.top': False, 'axes.spines.right': False})
    if ax is None:
        __, ax = plt.subplots(1, 1)
    ax.plot(ASDR, 'r')
    ax.set_xlim([0, int(end_time + 1)])
    ax.set_xlabel('sec')
    ax.set_ylabel('Spikes per second')


def ISI_histogram(isi_hist: npt.NDArray, isi_edges: npt.NDArray,
                  ax: plt.Axes | None = None) -> None:
    plt.style.use({'axes.spines.top': False, 'axes.spines.right': False})
    if ax is None:
        __, ax = plt.subplots(1, 1)

    ax.semilogy(isi_edges, isi_hist, 'o', color='k',
                fillstyle='none')
    ax.set_ylim((1e-5, 1))
    ax.set_xlabel('ISI (sec)')
    ax.set_ylabel('Probablity')

    params, cov = fit_ISI_hist(isi_hist, isi_edges)
    fit = double_exp(isi_edges, *params)    # type: ignore
    ax.semilogy(isi_edges, fit, 'r')
    std = np.sqrt(np.diag(cov))
    np.set_printoptions(precision=4)
    text = '\n'.join((
        f'a0 = {params[0]:.4g} \u00B1 {std[0]:.4g}',
        f'a1 = {params[1]:.4g} \u00B1 {std[1]:.4g}',
        f'a2 = {params[2]:.4g} \u00B1 {std[2]:.4g}',
        f'tau1 = {params[3]:.4g} \u00B1 {std[3]:.4g}',
        f'tau2 = {params[4]:.4g} \u00B1 {std[4]:.4g}'))
    ax.text(0.45, 0.65, text, transform=ax.transAxes, fontsize=8)


def burst_duration_histogram(bursts: pd.DataFrame,
                             ax: plt.Axes | None = None) -> None:
    plt.style.use({'axes.spines.top': False, 'axes.spines.right': False})
    if ax is None:
        __, ax = plt.subplots(1, 1)

    duration = bursts['end_time'].values - bursts['start_time'].values
    hist, edges = np.histogram(duration, bins=100, range=(0, 5))
    x_vals = edges[:-1] + (edges[1] - edges[0])/2
    hist = hist/np.sum(hist)
    ax.semilogy(x_vals, hist, 'o',  color='k', fillstyle='none')
    ax.set_xlabel('Burst Duration (sec)')
    ax.set_xlim([0, 5])
    ax.set_ylabel('Probability')


def IBI_histogram(bursts: pd.DataFrame, ax: plt.Axes | None = None) -> None:
    plt.style.use({'axes.spines.top': False, 'axes.spines.right': False})
    if ax is None:
        __, ax = plt.subplots(1, 1)

    ibis = np.zeros(0)
    grouped = bursts.groupby('channel_idx')
    idx = np.unique(bursts['channel_idx'].values)
    for i in idx:
        temp = grouped.get_group(i)
        if len(temp) > 1:
            ibi = temp['start_time'].values[1:] - temp['end_time'].values[:-1]
            ibis = np.append(ibis, ibi)

    hist, edges = np.histogram(ibis, bins=200, range=(0, 10))
    x_vals = edges[:-1] + (edges[1] - edges[0])/2
    hist = hist/np.sum(hist)
    ax.semilogy(x_vals, hist, 'o',  color='k', fillstyle='none')
    ax.set_xlabel('Inter Burst Interval (sec)')
    ax.set_xlim([0, 10])
    ax.set_ylabel('Probability')


def t_crit_summary(data: list, ASDR: npt.NDArray, isi_hist: npt.NDArray,
                   isi_edges: npt.NDArray, bursts: pd.DataFrame) -> plt.Figure:
    plt.style.use({'axes.spines.top': False, 'axes.spines.right': False})
    fig = plt.figure(figsize=(7.5, 10))
    gs = fig.add_gridspec(2, 1)
    upper = gs[0].subgridspec(2, 1, hspace=0.01, height_ratios=[3, 1])
    lower = gs[1].subgridspec(2, 2)     # , hspace=0.3, wspace=0.75)
    # raster_ax, ASDR_ax = upper.subplots()
    ASDR_ax = fig.add_subplot(upper[1])
    raster_ax = fig.add_subplot(upper[0], sharex=ASDR_ax)

    ISI_ax = fig.add_subplot(lower[0, 0])
    burst_dur_ax = fig.add_subplot(lower[0, 1])
    burst_ibi_ax = fig.add_subplot(lower[1, 1])

    raster_plot(data, 1800, raster_ax)
    raster_ax.spines['bottom'].set_visible(False)
    raster_ax.get_xaxis().set_visible(False)

    ASDR_plot(ASDR, 1800, ASDR_ax)
    ISI_histogram(isi_hist, isi_edges, ISI_ax)
    burst_duration_histogram(bursts, burst_dur_ax)
    IBI_histogram(bursts, burst_ibi_ax)

    fig.tight_layout()
