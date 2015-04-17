# -*- coding: utf-8 -*-
# cython: profile=True
"""
Cython interface to sttc code
"""

import numpy as np
cimport numpy as np


DTYPE = np.float
ctypedef np.float_t DTYPE_t


cdef extern from "spike_time_tiling_coefficient.h":
    void run_sttc(int *N1v, int *N2v, double *dtv, double *Time, double *index,
                  double *spike_times_1, double *spike_times_2)
             
                            
def sttc(t1, t2, double dt, double start, double end):
    ''' Computes the bivariate spike time tiling coefficient of Cutts and Eglen
    (2014)
    t1 and t2 are 1D lists/arrays with the spiking times of two neurones    
    It returns the spike time tiling coefficent
    '''
    cdef int N1 = len(t1)
    cdef int N2 = len(t2)
    assert N1 > 0
    assert N2 > 0
    cdef double index = 0
    cdef np.ndarray[DTYPE_t, ndim=1] t1_np = np.asarray(t1)
    cdef np.ndarray[DTYPE_t, ndim=1] t2_np = np.asarray(t2)
    cdef np.ndarray[DTYPE_t, ndim=1] time = np.asarray([start, end])

    run_sttc(&N1, &N2, &dt, &time[0], &index, &t1_np[0], &t2_np[0])
    assert index <= 1
    return index


def multivariate_sttc(spike_trains, double dt, double start, double end):
    """ calculate sttc for all arrays of spike times in the list spike_trains
    returns an array of sttc values
    """
    n_trains = len(spike_trains)
    result = np.ones((n_trains, n_trains))
    for i, t1 in enumerate(spike_trains[:-1]):
        for j, t2 in enumerate(spike_trains[i+1:]):
             result[i, i+j+1] = result[i+j+1, i] = sttc(t1, t2, dt, start, end)

    return result
