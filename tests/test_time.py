#######################################################################

import leiap
import pandas as pd

#######################################################################

def test_clean_datetimes_return_df():
    pts = leiap.load_points_simple()
    df = leiap.clean_datetimes(pts)
    assert isinstance(df, pd.DataFrame)

def test_clean_datetimes_length():
    """Row length should be greater than 0"""
    pts = leiap.load_points_simple()
    df = leiap.clean_datetimes(pts)
    assert df.shape[0] > 0

def test_clean_datetimes_columns():
    """Must have 'dt_adj' column"""
    pts = leiap.load_points_simple()
    cols = leiap.clean_datetimes(pts).columns.tolist()
    assert 'dt_adj' in cols
    
def test_clean_datetimes_dt_col_type():
    pass

#######################################################################
