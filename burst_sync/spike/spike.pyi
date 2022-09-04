# -*- coding: utf-8 -*-

import numpy.typing as npt


def bivariate_spike_distance(t1: npt.NDArray, t2: npt.NDArray, ti: float,
                             te: float,
                             N: int) -> tuple[npt.NDArray, npt.NDArray]: ...


def multivariate_spike_distance(spike_trains: list, ti: float, te: float,
                                N: int) -> tuple[npt.NDArray, npt.NDArray]: ...
