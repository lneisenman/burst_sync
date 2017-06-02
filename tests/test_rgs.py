# -*- coding: utf-8 -*-
"""
This test module demonstrates that the python code produces the same results
as the demo code included in the supplementary material posted on the
J Neurosci Methods website along with the article by Ko et al.
"""

from __future__ import (print_function, division,
                        unicode_literals, absolute_import)


import pandas as pd
import numpy as np

from burst_sync import rgs


def assert_df_equal(df1, df2):
    ''' compare two data frames column by column '''
    for col in df1:
        np.testing.assert_allclose(df1[col], df2[col], rtol=0, atol=1e-6)


def test_rgs():
    # read data
    data1 = pd.read_csv('tests/testdata1.csv')
    data2 = pd.read_csv('tests/testdata2.csv')
    data3 = pd.read_csv('tests/testdata3.csv')
    data = [data1, data2, data3]
    bursts1 = pd.read_csv('tests/output_b1.csv')
    pauses1 = pd.read_csv('tests/output_p1.csv')
    bursts2 = pd.read_csv('tests/output_b2.csv')
    pauses2 = pd.read_csv('tests/output_p2.csv')
    bursts3 = pd.read_csv('tests/output_b3.csv')
    pauses3 = pd.read_csv('tests/output_p3.csv')
    bursts = [bursts1, bursts2, bursts3]
    pauses = [pauses1, pauses2, pauses3]

    results = rgs.bp_summary(data, p_thresh=0.001)

    for i, (r, b) in enumerate(zip(results[0], bursts)):
        if i < 2:   # can't compare empty dataframes using equals
            assert r.empty
        else:
            assert_df_equal(r, b)

    for i, (r, p) in enumerate(zip(results[1], pauses)):
        if i == 0:
            assert r.empty
        else:
            assert_df_equal(r, p)


if __name__ == '__main__':
    test_rgs()
