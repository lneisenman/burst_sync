# -*- coding: utf-8 -*-

'''

Comment by Thomas Kreuz:

This Python code (including all further comments) was written by Jeremy Fix (see http://jeremy.fix.free.fr/),
based on Matlab code written by Thomas Kreuz.

The SPIKE-distance is described in this paper:

Kreuz T, Chicharro D, Houghton C, Andrzejak RG, Mormann F:
Monitoring spike train synchrony.
J Neurophysiol 109, 1457-1472 (2013).

The Matlab codes as well as more information can be found at http://www.fi.isc.cnr.it/users/thomas.kreuz/sourcecode.html.

'''


import numpy as np

'''
Return the times (t1,t2) of the spikes in train[ibegin:]
such that t1 < t and t2 >= t
'''
def find_corner_spikes(t, train, ibegin, ti, te):
    if(ibegin == 0):
        tprev = ti
    else:
        tprev = train[ibegin-1]
    for idts, ts in enumerate(train[ibegin:]):
        if(ts >= t):
            return np.array([tprev, ts]), idts+ibegin
        tprev = ts
    return np.array([train[-1],te]), idts+ibegin


def bivariate_spike_distance(t1, t2, ti, te, N):
    '''Computes the bivariate SPIKE distance of Kreuz et al. (2012)
       t1 and t2 are 1D arrays with the spiking times of two neurones    
       It returns the array of the values of the distance
       between time ti and te with N samples.
       The arrays t1, t2 and values ti, te are unit less '''
    t = np.linspace(ti+(te-ti)/N, te, N)
    d = np.zeros(t.shape)

    t1 = np.insert(t1, 0, ti)
    t1 = np.append(t1, te)
    t2 = np.insert(t2, 0, ti)
    t2 = np.append(t2, te)

    # We compute the corner spikes for all the time instants we consider
    # corner_spikes is a 4 column matrix [t, tp1, tf1, tp2, tf2]
    corner_spikes = np.zeros((N,5))
 
    ibegin_t1 = 0
    ibegin_t2 = 0
    corner_spikes[:,0] = t
    for itc, tc in enumerate(t):
       corner_spikes[itc,1:3], ibegin_t1 = find_corner_spikes(tc, t1, ibegin_t1, ti, te)
       corner_spikes[itc,3:5], ibegin_t2 = find_corner_spikes(tc, t2, ibegin_t2, ti, te)

    #print corner_spikes
    xisi = np.zeros((N,2))
    xisi[:,0] = corner_spikes[:,2] - corner_spikes[:,1]
    xisi[:,1] = corner_spikes[:,4] - corner_spikes[:,3]
    norm_xisi = np.sum(xisi,axis=1)**2.0

    # We now compute the smallest distance between the spikes in t2 and the corner spikes of t1
    # with np.tile(t2,(N,1)) we build a matrix :
    # np.tile(t2,(N,1)) =    [   t2   ]        -   np.tile(reshape(corner_spikes,(N,1)), t2.size) = [                        ]
    #                        [   t2   ]                                                             [  corner  corner  corner]
    #                        [   t2   ]                                                             [                        ]
    dp1 = np.min(np.fabs(np.tile(t2,(N,1)) - np.tile(np.reshape(corner_spikes[:,1],(N,1)),t2.size)),axis=1)
    df1 = np.min(np.fabs(np.tile(t2,(N,1)) - np.tile(np.reshape(corner_spikes[:,2],(N,1)),t2.size)),axis=1)
    # And the smallest distance between the spikes in t1 and the corner spikes of t2
    dp2 = np.min(np.fabs(np.tile(t1,(N,1)) - np.tile(np.reshape(corner_spikes[:,3],(N,1)),t1.size)),axis=1)
    df2 = np.min(np.fabs(np.tile(t1,(N,1)) - np.tile(np.reshape(corner_spikes[:,4],(N,1)),t1.size)),axis=1)

    xp1 = t - corner_spikes[:,1]
    xf1 = corner_spikes[:,2] - t 
    xp2 = t - corner_spikes[:,3]
    xf2 = corner_spikes[:,4] - t

    S1 = (dp1 * xf1 + df1 * xp1)/xisi[:,0]
    S2 = (dp2 * xf2 + df2 * xp2)/xisi[:,1]

    d = (S1 * xisi[:,1] + S2 * xisi[:,0]) / (norm_xisi/2.0)

    return t,d

def multivariate_spike_distance(spike_trains, ti, te, N):
    ''' t is an array of spike time arrays
    ti the initial time of the recordings
    te the end time of the recordings
    N the number of samples used to compute the distance
    spike_trains is a list of arrays of shape (N, T) with N spike trains
    The multivariate distance is the instantaneous average over all the pairwise distances
    '''
    d = np.zeros((N,))
    n_trains = len(spike_trains)
    t = 0
    for i, t1 in enumerate(spike_trains[:-1]):
        for t2 in spike_trains[i+1:]:
            tij, dij = bivariate_spike_distance(t1, t2, ti, te, N)
            if(i == 0):
                t = tij # The times are only dependent on ti, te, and N
            d = d + dij
    d = d / float(n_trains * (n_trains-1) /2)
    return t,d

if __name__ == '__main__':
    import matplotlib.pylab as plt
    # We test the simulation of Kreuz(2012)

    ######################
    # With 2 spikes trains
    ti = 0
    tf = 1300
    t1 = np.arange(100, 1201, 100)
    t2 = np.arange(100, 1201, 110)
    t, Sb = bivariate_spike_distance(t1, t2, ti, tf, 50)

    plt.figure(figsize=(20,6))

    plt.subplot(211)
    for i in range(t1.size):
        plt.plot([t1[i], t1[i]], [0.5, 1.5], 'k')
    for i in range(t2.size):
        plt.plot([t2[i], t2[i]], [1.5, 2.5], 'k')
    plt.xlim([ti,tf])
    plt.ylim([0,3])
    plt.title("Spike trains")

    plt.subplot(212)
    plt.plot(t, Sb,'k')
    plt.xlim([ti,tf])
    plt.ylim([0,1])
    plt.xlabel("Time (ms)")
    plt.title("Bivariate SPIKE distance")

    plt.savefig("kreuz_bivariate.png")

    plt.show()

    #############################
    # With multiple spikes trains
    ti = 0
    tf = 4000
    num_trains = 50
    num_spikes = 40 # Each neuron fires exactly 40 spikes
    num_events = 5  # Number of events with increasing jitter
    # spike_times is an array where each rows contains the spike times of a neuron
    spike_times = np.zeros((num_trains, num_spikes))
    # The first spikes are randomly spread in the first half of the simulation time
    spike_times[:,range(num_spikes/2)] = tf/2.0 * np.random.random((num_trains, num_spikes/2))
    # We now append the times for the events with increasing jitter
    for i in range(1,num_events+1):
        tb = tf/2.0 * i / num_events 
        spike_times[:,num_spikes/2+i-1] = tb + (50 *(i-1) / num_events)* (2.0 * np.random.random((num_trains,)) - 1)

    # And the second events with the decreasing jitter
    num_last_events = num_spikes/2-num_events
    for i in range(num_last_events):
        tb = tf/2.0 + tf/2.0 * i / (num_last_events-1)
        spike_times[:, -(i+1)] = tb + (50 - 50 *i / (num_last_events-1))* (2.0 * np.random.random((num_trains,)) - 1)

    # Finally we sort the spike times by increasing time for each neuron
    spike_times.sort(axis=1) 
    
    # We compute the multivariate SPIKE distance
    list_spike_trains = []
    [list_spike_trains.append(spike_times[i,:]) for i in range(num_trains)]
    t, Sb = multivariate_spike_distance(list_spike_trains, ti, tf, 1000)

    plt.figure(figsize=(20,6))
    plt.subplot(211)
    # We plot the spike trains
    for i in range(spike_times.shape[0]):
        for j in range(spike_times.shape[1]):
            plt.plot([spike_times[i][j], spike_times[i][j]],[i, i+1],'k')
    plt.title('Spikes')
    plt.subplot(212)
    plt.plot(t,Sb,'k')
    plt.xlim([0, tf])
    plt.ylim([0, 1])
    plt.xlabel("Time (ms)")
    plt.title("Multivariate SPIKE distance")

    plt.savefig("kreuz_multivariate.png")

    plt.show()
