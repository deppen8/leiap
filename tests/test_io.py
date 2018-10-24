#######################################################################

import leiap
import pandas as pd

#######################################################################

def test_connect2db_is_Connection():
    import pyodbc
    c = leiap.connect2db()
    assert isinstance(c, pyodbc.Connection)

#######################################################################

def test_db_query_return_df():
    df = leiap.db_query("SELECT * FROM Sherd")
    assert isinstance(df, pd.DataFrame)
    
#######################################################################

def test_load_points_simple_return_df():
    df = leiap.load_points_simple()
    assert isinstance(df, pd.DataFrame)

def test_load_points_simple_length():
    """Row length should be greater than 0"""
    df = leiap.load_points_simple()
    assert df.shape[0] > 0
    
#######################################################################

def test_load_points_by_year_return_df():
    years = ['2014','2015','2016','2017','2018']
    for year in years:
        df = leiap.load_points_by_year([year])
        assert isinstance(df, pd.DataFrame)

def test_load_points_by_year_length():
    """Row length should be greater than 0"""
    years = ['2014','2015','2016','2017','2018']
    for year in years:
        df = leiap.load_points_by_year([year])
        assert df.shape[0] > 0

#######################################################################

def test_load_artifacts_simple_return_df():
    df = leiap.load_artifacts_simple()
    assert isinstance(df, pd.DataFrame)

def test_load_artifacts_simple_length():
    """Row length should be greater than 0"""
    df = leiap.load_artifacts_simple()
    assert df.shape[0] > 0
    
#######################################################################

def test_load_artifacts_by_year_return_df():
    years = ['2015','2016','2017','2018']
    for year in years:
        df = leiap.load_artifacts_by_year([year])
        assert isinstance(df, pd.DataFrame)

def test_load_artifacts_by_year_length():
    """Row length should be greater than 0"""
    years = ['2015','2016','2017','2018']
    for year in years:
        df = leiap.load_artifacts_by_year([year])
        assert df.shape[0] > 0

#######################################################################

def test_load_productions_simple_return_df():
    df = leiap.load_productions_simple()
    assert isinstance(df, pd.DataFrame)

def test_load_productions_simple_length():
    """Row length should be greater than 0"""
    df = leiap.load_productions_simple()
    assert df.shape[0] > 0
    
#######################################################################

def test_load_production_cts_wts_return_df():
    df = leiap.load_production_cts_wts()
    assert isinstance(df, pd.DataFrame)

def test_load_production_cts_wts_length():
    """Row length should be greater than 0"""
    df = leiap.load_production_cts_wts()
    assert df.shape[0] > 0

#######################################################################

def test_load_points_times_return_df():
    df = leiap.load_points_times(warn='disable')
    assert isinstance(df, pd.DataFrame)

def test_load_points_times_length():
    """Row length should be greater than 0"""
    df = leiap.load_points_times(warn='disable')
    assert df.shape[0] > 0

def test_load_points_times_columns():
    """Must have 'search_time' and 'dist' columns"""
    cols = leiap.load_points_times(warn='disable').columns.tolist()
    assert 'search_time' in cols
    assert 'dist' in cols
    
#######################################################################