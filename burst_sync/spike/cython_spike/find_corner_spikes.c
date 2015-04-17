#include <stdio.h>
#include "find_corner_spikes.h"

void find_corner_spikes(double t, double *train, long len, long ibegin,
                        double ti, double te, double *result) {

    double tprev;
    long idts;

    if (ibegin == 0) {
        tprev = ti;
    } else {
        tprev = train[ibegin - 1];
    }

    for (idts = ibegin; idts < len; idts++) {
        if (train[idts] >= t) {
            result[0] = (double) (idts);
            result[1] = tprev;
            result[2] = train[idts];
            //printf("%i\t%i\t%f\n", idts, ibegin, result[2]);
            return;
        }
        tprev = train[idts];
    }

    //printf('idts = %i\tlen = %i\n', idts, len);
    result[0] = (double) (idts);
    result[1] = train[len-1];
    result[2] = te;
    //printf('here %f\n', result[2]);
    return;

}


//def find_corner_spikes(float t, np.ndarray[DTYPE_t, ndim=1] train,
//                       float ibegin, float ti, float te):
//    '''
//    Return the times (t1,t2) of the spikes in train[ibegin:]
//    such that t1 < t and t2 >= t
//    '''
//    cdef float tprev, ts
//    cdef int idts
//    if(ibegin == 0):
//        tprev = ti
//    else:
//        tprev = train[ibegin-1]
//    for idts, ts in enumerate(train[ibegin:]):
//        if(ts >= t):
//            return np.array([tprev, ts]), idts+ibegin
//        tprev = ts
//    return np.array([train[-1],te]), idts+ibegin
