# -*- coding: utf-8 -*-

"""
Cythonized version of code to calculate SPIKE distance
"""

import numpy as np
cimport numpy as np


DTYPE = np.float
ctypedef np.float_t DTYPE_t

#def find_corner_spikes(float t, np.ndarray[DTYPE_t, ndim=1] train,
#                       float ibegin, float ti, float te):
#    '''
#    Return the times (t1,t2) of the spikes in train[ibegin:]
#    such that t1 < t and t2 >= t
#    '''
#    cdef float tprev, ts
#    cdef int idts
#    if(ibegin == 0):
#        tprev = ti
#    else:
#        tprev = train[ibegin-1]
#    for idts, ts in enumerate(train[ibegin:]):
#        if(ts >= t):
#            return np.array([tprev, ts]), idts+ibegin
#        tprev = ts
#    return np.array([train[-1],te]), idts+ibegin
cdef extern from "find_corner_spikes.h":
    void find_corner_spikes(double t, double *train, long len, long ibegin,
                            double ti, double te, double *result)
                            
def bivariate_spike_distance(np.ndarray[DTYPE_t, ndim=1] t1,
                             np.ndarray[DTYPE_t, ndim=1] t2, 
                             double ti, double te, long N):
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
 
    cdef double tc
    cdef long ibegin_t1, ibegin_t2, itc, len1, len2
    cdef np.ndarray[DTYPE_t] result = np.zeros(3)
    ibegin_t1 = 0
    len1 = len(t1)
    ibegin_t2 = 0
    len2 = len(t2)
    corner_spikes[:,0] = t
    for itc, tc in enumerate(t):
        find_corner_spikes(tc, &t1[0], len1, ibegin_t1, ti, te, &result[0])
        ibegin_t1 = int(result[0])
        corner_spikes[itc, 1] = result[1]
        corner_spikes[itc, 2] = result[2]
        #corner_spikes[itc,1:3], ibegin_t1 = find_corner_spikes(tc, t1, ibegin_t1, ti, te)
        find_corner_spikes(tc, &t2[0], len2, ibegin_t2, ti, te, &result[0])
        ibegin_t2 = int(result[0])
        corner_spikes[itc, 3] = result[1]
        corner_spikes[itc, 4] = result[2]
        #corner_spikes[itc,3:5], ibegin_t2 = find_corner_spikes(tc, t2, ibegin_t2, ti, te)

    #print corner_spikes
    cdef np.ndarray[DTYPE_t, ndim=2] xisi
    cdef np.ndarray[DTYPE_t, ndim=1] norm_xisi
    xisi = np.zeros((N,2))
    xisi[:,0] = corner_spikes[:,2] - corner_spikes[:,1]
    xisi[:,1] = corner_spikes[:,4] - corner_spikes[:,3]
    norm_xisi = np.sum(xisi,axis=1)**2.0

    # We now compute the smallest distance between the spikes in t2 and the corner spikes of t1
    # with np.tile(t2,(N,1)) we build a matrix :
    # np.tile(t2,(N,1)) =    [   t2   ]        -   np.tile(reshape(corner_spikes,(N,1)), t2.size) = [                        ]
    #                        [   t2   ]                                                             [  corner  corner  corner]
    #                        [   t2   ]  
#    cdef float dp1, df1, dp2, df2
#    cdef np.ndarray xp1, xf1, xp2, xf2, S1, S2, d                                                       [                        ]
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

    return t, d


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
    return t, d
