# -*- coding: utf-8 -*-

from __future__ import print_function, division


import numpy as np
import pandas as pd


from burst_sync import sttc


def test_multivariate_sttc():
    """ Use Kreuz 2012 test data to test multivariate_sttc which uses
    bivariate_sttc"""

    test_data = pd.read_csv('tests/data/test_data.csv')
    result = pd.read_csv('tests/sttc_result.csv')
    print(result.head())
    test_data_list = [np.asarray(test_data[str(i)]) for i in range(50)]
    mv_sttc = sttc.multivariate_sttc(test_data_list, 0.05, 0, 4000)
    assert np.allclose(np.triu(mv_sttc), np.triu(result.values))
