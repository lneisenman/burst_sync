# -*- coding: utf-8 -*-

from __future__ import (print_function, division,
                        absolute_import, unicode_literals)

import numpy as np
from burst_sync import spike


def test_bivariate():
    """
    We test the simulation of Kreuz(2012)
    With 2 spikes trains
    """
    ti = 0
    tf = 1300
    t1 = np.arange(100, 1201, 100, dtype=np.float)
    t2 = np.arange(100, 1201, 110, dtype=np.float)
    t, Sb = spike.bivariate_spike_distance(t1, t2, ti, tf, 50)
    t2, Sb2 = spike.orig.bivariate_spike_distance(t1, t2, ti, tf, 50)
    np.allclose(Sb, Sb2)
#    plt.figure(figsize=(10, 6))
#
#    plt.subplot(211)
#    for i in range(t1.size):
#        plt.plot([t1[i], t1[i]], [0.5, 1.5], 'k')
#    for i in range(t2.size):
#        plt.plot([t2[i], t2[i]], [1.5, 2.5], 'k')
#    plt.xlim([ti, tf])
#    plt.ylim([0, 3])
#    plt.title("Spike trains")
#
#    plt.subplot(212)
#    plt.plot(t, Sb, 'k')
#    plt.xlim([ti, tf])
#    plt.ylim([0, 1])
#    plt.xlabel("Time (ms)")
#    plt.title("Bivariate SPIKE distance")


def test_multivariate():
    """
    We test the simulation of Kreuz(2012)
    With multiple spikes trains
    """
    ti = 0
    tf = 4000
    num_trains = 50
    num_spikes = 40 # Each neuron fires exactly 40 spikes
    num_events = 5  # Number of events with increasing jitter
    # spike_times is an array where each rows contains the spike times of a neuron
    spike_times = np.zeros((num_trains, num_spikes))
    # The first spikes are randomly spread in the first half of the simulation time
    spike_times[:,range(num_spikes//2)] = tf/2.0 * np.random.random((num_trains, num_spikes/2))
    # We now append the times for the events with increasing jitter
    for i in range(1,num_events+1):
        tb = tf/2.0 * i / num_events 
        spike_times[:, num_spikes//2+i-1] = tb + (50 *(i-1) / num_events)* (2.0 * np.random.random((num_trains,)) - 1)

    # And the second events with the decreasing jitter
    num_last_events = num_spikes//2-num_events
    for i in range(num_last_events):
        tb = tf/2.0 + tf/2.0 * i / (num_last_events-1)
        spike_times[:, -(i+1)] = tb + (50 - 50 *i / (num_last_events-1))* (2.0 * np.random.random((num_trains,)) - 1)

    # Finally we sort the spike times by increasing time for each neuron
    spike_times.sort(axis=1) 
    
    # We compute the multivariate SPIKE distance
    list_spike_trains = []
    [list_spike_trains.append(spike_times[i,:]) for i in range(num_trains)]
    t, Sb = spike.multivariate_spike_distance(list_spike_trains, ti, tf, 1000)
    t2, Sb2 = spike.orig.multivariate_spike_distance(list_spike_trains, ti,
                                                     tf, 1000)
    np.allclose(Sb, Sb2)

#    plt.figure(figsize=(10, 6))
#    plt.subplot(211)
#    # We plot the spike trains
#    for i in range(spike_times.shape[0]):
#        for j in range(spike_times.shape[1]):
#            plt.plot([spike_times[i][j], spike_times[i][j]], [i, i + 1],'k')
#    plt.title('Spikes')
#    plt.subplot(212)
#    plt.plot(t, Sb, 'k')
#    plt.xlim([0, tf])
#    plt.ylim([0, 1])
#    plt.xlabel("Time (ms)")
#    plt.title("Multivariate SPIKE distance")
#
#
#if __name__ == '__main__':
#    import matplotlib
#    matplotlib.interactive(False)
#    test_bivariate()
#    test_multivariate()
#    plt.show()
