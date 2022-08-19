# -*- coding: utf-8 -*-
"""
Duplicate functions available in R that are not in numpy
"""

from __future__ import print_function
from __future__ import division


import numpy as np
import pandas as pd


def quantile7(x, p):
    """
    calculate quantile using type=7 method from R's quantile function
    This is the same as np.percentile
    """
    n = len(x)
    index = (n - 1) * p
    lo = np.asarray(index, dtype=np.int)
    hi = lo + 1
    x = np.sort(x)
    qs = x[lo]
    h = index - lo
    qs = ((1 - h) * qs) + (h * x[hi])
    return qs


def quantile8(x, p):
    """
    calculate quantile using type=8 method from R's quantile function
    """
    n = len(x)
    if n < 2:
        raise ValueError('length of x must be at least two')

    nppm = 1/3 + (p * (n + 1 - 2/3)) - 1
    j = np.asarray(nppm, dtype=np.int)
    h = nppm - j
    x = np.sort(x)
    qs = x[j]
    qs = ((1 - h) * qs) + (h * x[j + 1])
    return qs


def test_quantile():
    x = np.linspace(1,25,25)
    q = np.asarray([0.05, 0.95])
    print(quantile7(x, q))
    print([np.percentile(x, 100*p) for p in q])
    print(quantile8(x, q))
    x2 = np.linspace(1,30,30)
    x2[25:] = 0
    print(quantile8(x2, q))
    
    
def runmed(x, k):
    k2 = k//2 + 1
    length = len(x)
    med = np.zeros(length)
    med[:k2] = np.median(x[:k])
    med[-k2:] = np.median(x[-k:])
    for i in range(k2, length-k2):
        med[i] = np.median(x[i-k2+1:i+k2])
    
    return med


def mad(x, c=1.4826):
    """
    median absolute deviation
    """
    med = np.median(x)
    result = np.median(np.abs(x - med)) * c
    return result


def seq(x):
    """
    sequence of length x
    """
    result = np.asarray(range(1, len(x)+1))
    return result


def table(x):
    """
    sequence of number of repeats of each value in x
    """
    data = np.asarray(x)
    if (len(data) == 0):
        return np.empty(0, dtype=np.int)
    __, freq = np.unique(data, return_counts=True)
    return freq


if __name__ == '__main__':
    pass
