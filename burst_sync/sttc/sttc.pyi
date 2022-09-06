# -*- coding: utf-8 -*-

from dbm import ndbm
import numpy.typing as npt


def sttc(t1: npt.NDArray, t2: npt.NDArray, dt: float,
         start: float, end: float) -> float: ...


def multivariate_sttc(spike_trains: list, dt: float,
                      start: float, end: float) -> npt.NDArray: ...
