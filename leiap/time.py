"""
This file contains functions related to survey search time calculations
"""


import pandas as _pd


#######################################################################################################################


def clean_datetimes(df, dt_col='DataDate'):
    """Filter datetimes and correct for timezone issues
    
    Parameters
    ----------
    df : pandas DataFrame
        DataFrame of point observations
    dt_col : str
        Column name for datetime data
    
    Returns
    -------
    df : pandas DataFrame
        Identical to input DataFrame with an added 'dt_adj' column representing datetimes filtered and
        correct (see Notes)
    
    Notes
    -----
    1. Points collected in 2014 did not have their times recorded (only dates); they are assigned a time of 00:00:00
    by the database. In the new `dt_adj` column, they are assigned NaT type. If you want to access just the dates,
    you can do so with the original `dt_col` (`DataDate` by default).
    2. When points are downloaded from handheld GPS devices, their times are converted to the timezone of the laptop on
    which they are downloaded. Before we realized this, a lot of points were uploaded on machines set to U.S. Pacific
    Time. As a result, some times need to be adjusted by 9 hours.
    """
    df['dt_adj'] = df[dt_col].where(df[dt_col].dt.year > 2014)
    df = correct_timezone(df, dt_col)
    return df

#######################################################################################################################


def correct_timezone(df, dt_col='DataDate'):
    """Account for some timezone issues
    
    Parameters
    ----------
    df : pandas DataFrame
        DataFrame of point observations
    dt_col : str
        Column name for datetime data
    
    Returns
    -------
    df : pandas DataFrame
        Identical to input DataFrame with datetimes fixed so that they all range from 06:30:00-21:30:00. In reality,
        the latest times are approx 15:00:00
    """
    df[dt_col] = df[dt_col].where((df[dt_col].dt.time > _pd.Timestamp('06:30:00').time()) &
                                  (df[dt_col].dt.time < _pd.Timestamp('21:30:00').time()),
                                  df[dt_col]+_pd.DateOffset(hours=9))
    return df

#######################################################################################################################


def calc_search_time(df, dt_col='dt_adj', warn='enable'):
    """Calculate search times in seconds
    
    Parameters
    ----------
    df : pandas DataFrame of points
        Must have columns 'FieldNumber', 'SurveyorName', 'SurveyPointId'
    dt_col : str
        Column name for datetime data
    warn : {'enable', 'disable'}
        Specify whether or not you want the generic warning message.
        
    Returns
    -------
    df : pandas DataFrame
        Identical to input DataFrame with added 'search_time' and 'dist' columns representing search time in seconds,
        and distance from previous point in meters
    
    Notes
    -----
    This is a naive calculation that doesn't discard any times. You will want to filter values further before using in
    any interpretively meaningful way.
    """
    import math
    if warn == 'enable':
        import warnings
        warnings.warn('FYI: Search times calculated in a naive way (e.g., including unrealistic values and NaN values).'
                      'Consider further filtering before using `search_time` in calculations.')
    
    pts_ix = df.set_index(['FieldNumber', 'SurveyorName', 'SurveyPointId']).sort_index()  # create multi-index df
    combos = list(set(zip(df['FieldNumber'], df['SurveyorName'])))  # find all unique combos of field and surveyor

    s = []  # list to store series for each surveyor within each field
    for i in range(len(combos)):  # loop through field/surveyor pairs
        field, surveyor = combos[i][0], combos[i][1]
        # create new df subset for that field and surveyor and sort by datetime
        df_fs = pts_ix.loc[field, surveyor].sort_values(dt_col)
        
        df_fs['dist'] = df_fs['dist'] = ((df_fs['Easting']-df_fs['Easting'].shift(1))**2 +
                                         (df_fs['Northing']-df_fs['Northing'].shift(1))**2
                                         ).apply(lambda x: math.sqrt(x))  # calculate distance between consecutive pts
        
        df_fs['search_time'] = df_fs[dt_col].diff().dt.total_seconds()  # calculate differences between consecutive dts
        s.append(df_fs[['search_time', 'dist']])  # append the small series to the list of series

    t = _pd.concat(s)  # concatenate all of the series into one long one (should be of length == n points)
    return df.join(t, on='SurveyPointId')  # join the series to the original points df

#######################################################################################################################


def filter_times(df, t_col='search_time', t_lim=(1, 900), dist_col='dist', dist_lim=(1, 20)):
    """Put time and distance restrictions on the time data.
    
    Parameters
    ----------
    df : pandas DataFrame
        Dataset of points
    t_col : str
        Name of column with time info
    t_lim : tuple
        Min and max limits (inclusive) for time
    dist_col : str
        Name of column with distance info
    dist_lim : tuple
        Min and max limits (inclusive) for distance
        
    Returns
    -------
    filtered : pandas DataFrame
        A subset of the original DataFrame filtered according to the input parameters
    """
    filtered = df[~(df[t_col].isna()) &                             # times not N/A
                  (df[t_col].between(t_lim[0], t_lim[1])) &         # time limits
                  (df[dist_col].between(dist_lim[0], dist_lim[1]))  # distance limits
                  ].sort_values(t_col, ascending=False)             # sort by time
    return filtered

#######################################################################################################################
