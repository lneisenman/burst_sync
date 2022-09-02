# -*- coding: utf-8 -*-
"""
This test module demonstrates that the python code produces the same results
as the demo code included in the supplementary material posted on the
J Neurosci Methods website along with the article by Ko et al.
"""


import pandas as pd
import numpy as np

from burst_sync import rgs


# def df_equal(df1, df2):
#     """
#     compare two data frames column by column
#     """
#     for col in df1:
#         if not np.allclose(df1[col], df2[col]):
#             return False

#     return True


def test_rgs(rgs_data, rgs_bursts, rgs_pauses):
    results = rgs.bp_summary(rgs_data, p_thresh=0.001)

    for i, (r, b) in enumerate(zip(results[0], rgs_bursts)):
        if i < 2:
            assert r.empty
        else:
            pd.testing.assert_frame_equal(r, b)

    for i, (r, p) in enumerate(zip(results[1], rgs_pauses)):
        if i == 0:
            assert r.empty
        else:
            pd.testing.assert_frame_equal(r, p)
