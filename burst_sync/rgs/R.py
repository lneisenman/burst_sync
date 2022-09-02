# -*- coding: utf-8 -*-
"""
Duplicate functions available in R that are not in numpy
"""

from typing import Sequence, TypeAlias, Union

import numpy as np
import numpy.typing as npt


Value: TypeAlias = int | float
Val_Array: TypeAlias = list[Value] | npt.NDArray


def quantile7(x: Val_Array, p: Val_Array) -> npt.NDArray:
    """
    calculate quantile using type=7 method from R's quantile function
    This is the same as np.percentile
    """
    n = len(x)
    index = (n - 1) * p
    lo = np.asarray(index, dtype=int)
    hi = lo + 1
    xs = np.sort(x)
    qs = xs[lo]
    h = index - lo
    qs = ((1 - h) * qs) + (h * xs[hi])
    return qs   # type: ignore


def quantile8(x: Val_Array, p: Val_Array) -> npt.NDArray:
    """
    calculate quantile using type=8 method from R's quantile function
    """
    n = len(x)
    if n < 2:
        raise ValueError('length of x must be at least two')

    nppm = np.asarray(((n + 1/3) * p) - 2/3)    # type: ignore
    j = nppm.astype(int)
    h = nppm - j
    xs = np.sort(x)
    qs = xs[j]
    qs = ((1 - h) * qs) + (h * xs[j + 1])
    return qs   # type: ignore


def runmed(x: Val_Array, k: int) -> npt.NDArray:
    k2 = int(k//2 + 1)
    length = len(x)
    med = np.zeros(length)
    med[:k2] = np.median(x[:k])
    med[-k2:] = np.median(x[-k:])
    for i in range(k2, length-k2):
        med[i] = np.median(x[i-k2+1:i+k2])

    return med


def mad(x: Val_Array, c: float = 1.4826) -> float:
    """
    median absolute deviation
    """
    med = np.median(x)
    result: float = np.median(np.abs(x - med)) * c  # type:ignore
    return result


def seq(x: Val_Array) -> npt.NDArray:
    """
    sequence of length x
    """
    result: npt.NDArray = np.asarray(range(1, len(x)+1))
    return result


def table(x: Val_Array) -> npt.NDArray:
    """
    sequence of number of repeats of each value in x
    """
    data = np.asarray(x)
    if (len(data) == 0):
        return np.empty(0, dtype=int)

    __, freq = np.unique(data, return_counts=True)
    return freq     # type: ignore
