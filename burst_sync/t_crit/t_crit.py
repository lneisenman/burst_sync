# -*- coding: utf-8 -*-

import numpy as np
import numpy.typing as npt
import pandas as pd


def t_crit():
    pass


def calc_ASDR(data: list, end_time: int) -> npt.NDArray:
    ASDR = np.zeros(end_time, dtype=int)
    for channel in data:
        for spike in channel:
            ASDR[int(spike)] += 1

    return ASDR


def calc_B():
    pass


def find_bursts():
    pass
