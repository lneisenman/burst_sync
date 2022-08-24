# -*- coding: utf-8 -*-

import pandas as pd
import pytest

import burst_sync


@pytest.fixture
def baseline():
    data = pd.DataFrame()
    files = ['tests/baseline/ch_1.txt', 'tests/baseline/ch_2.txt',
             'tests/baseline/ch_3.txt', 'tests/baseline/ch_4.txt',
             'tests/baseline/ch_5.txt', 'tests/baseline/ch_6.txt',
             'tests/baseline/ch_7.txt', 'tests/baseline/ch_8.txt']
    for fn in files:
        df = pd.read_table(fn)
        data = pd.concat([data, df], axis=1, ignore_index=True)

    names = data.columns.values.tolist()
    return [data[col].dropna().values for col in names]
