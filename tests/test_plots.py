# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pytest


from burst_sync.plots import (raster_plot, ASDR_plot, ISI_histogram,
                              burst_duration_histogram, IBI_histogram,
                              t_crit_summary)


# pytest.skip('Skipping graphs', allow_module_level=True)


def test_raster_plot(baseline_data):
    raster_plot(baseline_data, 1800)
    plt.show()


def test_ASDR_plot(ASDR):
    ASDR_plot(ASDR, 1800)
    plt.show()


def test_ISI_histogram(isi_hist, isi_edges):
    ISI_histogram(isi_hist, isi_edges)
    plt.show()


def test_burst_duration_histogram(bursts):
    burst_duration_histogram(bursts)
    plt.show()


def test_IBI_histogram(bursts):
    IBI_histogram(bursts)
    plt.show()


def test_t_crit_summary(baseline_data, ASDR, isi_hist, isi_edges, bursts):
    t_crit_summary(baseline_data, ASDR, isi_hist, isi_edges, bursts)
    plt.show()
