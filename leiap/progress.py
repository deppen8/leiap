"""
This file contains functions to generate progress reports
"""


from leiap.io import *
import datetime as _datetime


#######################################################################################################################


def get_measuring_progress(year, measure_col='Weight'):
    """Get a quick estimate of the amount of measuring left to do.
    
    Parameters
    ----------
    year : str or int
        The specific year of interest
    measure_col : str
        Column to use to judge whether an artifact is complete or not.
    
    Returns
    -------
    (dt, not_done) : tuple of datetime and int
        dt is the current datetime; not_done is the number of sherds remaining to measure.

    Notes
    -----
    1. The function also prints a human-readable summary statement.
    2. The calculation is based on the number of artifacts that have been classified but not yet had a weight recorded.

    This is very much an imperfect measure, but it helps to give a rough guide to progress.
    """
    artifacts_df = get_artifacts(sections=['metrics'], years=[year])
    dt = _datetime.datetime.now()
    done = len(artifacts_df[(artifacts_df[measure_col].notna())])
    not_done = len(artifacts_df[(artifacts_df[measure_col].isna())])
    pct_remain = not_done / (not_done + done) * 100
    
    print(f'At {dt}, there are {round(pct_remain, 1)}% remaining ({not_done}/{done+not_done}) to be measured')
    return dt, not_done


#######################################################################################################################


def get_classification_progress(year, bags_col='NumBags'):
    """Get a rough estimate of the number of bags left to classify.
    
    Parameters
    ----------
    year : str or int
        The specific year of interest
    bags_col : str
        Column containing the count of bags per point
    
    Returns
    -------
    (dt, bags_remain) : tuple of datetime and int
        dt is the current datetime; bags_remain is the number of bags remaining to classify.

    Notes
    -----
    1. The function also prints a human-readable summary statement.
    2. The calculation is based on the number of points recorded as having a bag. This is very much an imperfect measure, but it helps to give a rough guide to progress.

    Some reasons why the count might not reach 0:
    - Problem bags
    - Points that were accidentally assigned with bags = 1 during GPS data upload.
    - Points that should have been changed to -1 bags (i.e., all artifacts discarded during preliminary sort) but were not, for whatever reason, changed.

    """
    points_df = get_points(years=[year])
    artifacts_df = get_artifacts(years=[year], discards=True)
    
    pts_w_bags = points_df[points_df[bags_col] > 0].shape[0]
    pts_classified = artifacts_df.groupby(['SurveyPointId']).size().shape[0]
    
    bags_remain = pts_w_bags - pts_classified
    pct_remain = bags_remain / pts_w_bags * 100

    dt = _datetime.datetime.now()

    print(f'At {dt} there are {round(pct_remain, 1)}% of bags remaining ({bags_remain}/{pts_w_bags}) to be classified.')
    return dt, bags_remain

#######################################################################################################################
