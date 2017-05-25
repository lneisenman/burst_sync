from __future__ import (print_function, division, absolute_import,
                        unicode_literals)


import numpy as np


def asdr(data, end, bin_size=1):
    ''' Python implementation of Igor ASDR code '''
    asdr = np.zeros(int(end/bin_size), dtype=np.int)
    if end % bin_size > 0:
        asdr = np.append(asdr, 0)

    for key in data:
        for time in data[key]:
            asdr[int(time/bin_size)] += 1

    return asdr
