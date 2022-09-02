# -*- coding: utf-8 -*-
"""
python translation of Meaney lab Matlab code
"""

import typing

import numpy as np
import numpy.typing as npt


def get_phase_spikes(spikes: typing.Sequence, tfinal: float) -> npt.NDArray:
    """
    calculate spike phase as defined in Patel 2012
    """
    phase: npt.NDArray = 2 * np.pi * np.random.rand(tfinal)   # type: ignore
    k = 0
    numspikes = len(spikes)
    for t in range(1, tfinal+1):    # type: ignore
        while (k < numspikes) and (t >= spikes[k]):
            k += 1

        if k == 0:
            phase[t-1] = 2 * np.pi * (t - spikes[0])/spikes[0]
        elif k == numspikes:
            # phase[t-1] = 0
            pass
        else:
            phase[t-1] = (2 * np.pi * (t - spikes[k-1]) /
                          (spikes[k] - spikes[k-1])) + (2 * np.pi * k)

    return phase


def calc_phase_sync_matrix(spike_list: list,
                           tfinal: float) -> tuple[npt.NDArray, list]:
    """
    calculate the correlation matrix using spike phase
    """
    phase_list = list()
    for spikes in spike_list:
        phase = get_phase_spikes(spikes, tfinal)
        phase_list.append(phase)

    M = len(spike_list)
    C = np.zeros((M, M))
    for i in range(M):
        for j in range(i, M):
            if not ((len(spike_list[i]) == 0) or (len(spike_list[j]) == 0)):
                delta_phi = np.mod(phase_list[i] - phase_list[j], 2*np.pi)
                C[i, j] = np.sqrt(np.square(np.mean(np.cos(delta_phi))) +
                                  np.square(np.mean(np.sin(delta_phi))))
                C[j, i] = C[i, j]

    return C, phase_list


def calc_global_sync(spike_list: list, tfinal: float) -> float:
    C, __ = calc_phase_sync_matrix(spike_list, tfinal)
    (D, V) = np.linalg.eig(C)
    order = np.argsort(D)

    eigenvals = D[order].copy()
    M = len(spike_list)
    index: float = (np.max(eigenvals) - 1)/(M - 1)
    return index
