"""
This file contains functions related to I/O from the database
"""

import pandas as _pd
from leiap.time import *


#######################################################################################################################


def get_credentials(credentials_path='credentials.json'):
    """Access database credentials from JSON file

    Parameters
    ----------
    credentials_path : str
        Location of the credentials JSON file

    Returns
    -------
    credentials : dict
        Dictionary containing the database connection details
    """
    import json
    with open(credentials_path, 'r') as f:
        credentials = json.load(f)

    return credentials


#######################################################################################################################


def connect2db(driver='{ODBC Driver 17 for SQL Server}', **kwargs):
    """Open a connection to the database
    
    Parameters
    ----------
    driver : str, optional
        Database driver needed to connect
    **kwargs
        Optional arguments that are passed to get_credentials()

    Returns
    -------
    connection : MS SQL database connection
    """
    import pyodbc
    from sys import platform

    if platform == "darwin" or platform == "linux" or platform == "linux2":
        driver = "libmsodbcsql.17.dylib"  # may not be necessary for all macOS/Linux users

    credentials = get_credentials(**kwargs)

    connection = pyodbc.connect('DRIVER=' + driver +
                                ';SERVER=' + credentials['database']['server_name'] +
                                ';DATABASE=' + credentials['database']['db_name'] +
                                ';UID=' + credentials['database']['user'] +
                                ';PWD=' + credentials['database']['password'])

    return connection


#######################################################################################################################


def db_query(query_text, **kwargs):
    """Send any SQL query to the database
    
    Parameters
    ----------
    query_text : str
        Full SQL query to pass to the database
    **kwargs
        Optional arguments that are passed to get_credentials()

    Returns
    -------
    df : pandas DataFrame
        DataFrame of query results
    """
    conn = connect2db(**kwargs)
    df = _pd.read_sql(query_text, conn)
    conn.close()
    return df


#######################################################################################################################


def load_points(years=None, **kwargs):
    """Get a DataFrame of points

    Parameters
    ----------
    years : list
        List of desired years; can be strings or integers
    **kwargs
        Optional arguments that are passed to get_credentials()

    Returns
    -------
    points_df : pandas DataFrame
        DataFrame of all points
    """
    query = """SELECT SurveyPoint.*, Field.FieldNumber, Surveyor.SurveyorName 
               FROM SurveyPoint 
               LEFT JOIN Field ON SurveyPoint.FieldId=Field.FieldId
               LEFT JOIN Surveyor ON SurveyPoint.SurveyorId=Surveyor.SurveyorId
               """
    points_df = db_query(query, **kwargs)
    points_df = points_df.drop(columns=['SherdCount', 'tempFixIDs'])

    if years:
        points_df = points_df[points_df.DataDate.dt.year.isin(years)]

    return points_df


#######################################################################################################################


def load_points_simple(**kwargs):
    """Get a DataFrame of points with the most typical query

    Parameters
    ----------
    **kwargs
        Optional arguments that are passed to get_credentials()

    Returns
    -------
    points_df : pandas DataFrame
        DataFrame of all points
    """
    import warnings
    warnings.warn(
        """get_points_simple() is no longer preferred. Use get_points() with appropriate parameters instead.""",
        DeprecationWarning)

    query = """SELECT SurveyPoint.*, Field.FieldNumber, Surveyor.SurveyorName 
               FROM SurveyPoint 
               LEFT JOIN Field ON SurveyPoint.FieldId=Field.FieldId
               LEFT JOIN Surveyor ON SurveyPoint.SurveyorId=Surveyor.SurveyorId
               """
    points_df = db_query(query, **kwargs)
    return points_df


#######################################################################################################################


def load_points_by_year(years, **kwargs):
    """Get a DataFrame of points with the most typical query for specified year(s)

    Parameters
    ----------
    years : list
        List of desired years; can be strings or integers
    **kwargs
        Optional arguments that are passed to get_credentials()

    Returns
    -------
    points_df : pandas DataFrame
        DataFrame of all points for specified year(s)
    """
    import warnings
    warnings.warn(
        """get_points_by_year() is no longer preferred. Use get_points() with appropriate parameters instead.""",
        DeprecationWarning)

    points_df = load_points_simple(**kwargs)
    points_df = points_df[points_df.DataDate.dt.year.isin(years)]
    return points_df


#######################################################################################################################


def load_artifacts(sections=['base'], years=None, include_discards=False, **kwargs):
    """Get a DataFrame of artifacts

    Parameters
    ----------
    sections : list of some set of
        {'all', 'base', 'metrics', 'classify', 'production', 'tile_brick', 'waretypes', 'vesselparts', 'macro_fabric'}
        Sections to include in the output DataFrame. Each section refers to a group of column names.
    years : list
        List of desired years; can be strings or integers
    include_discards : bool
        If True, return all records, even artifacts marked as Discarded.
    **kwargs
        Optional arguments that are passed to get_credentials()

    Returns
    -------
    artifacts_df : pandas DataFrame
        DataFrame of all artifacts

    """
    if 'base' in sections:
        sections.remove('base')
    if 'all' in sections:
        sections = ['metrics', 'classify', 'production', 'tile_brick', 'waretypes', 'vesselparts', 'macro_fabric']

    base = ['SherdId', 'FieldId', 'SurveyorId', 'PointId', 'SherdNum', 'SurveyPointId',
            'ChangedDate', 'FieldNumber', 'Northing', 'Easting', 'SurveyorName']

    col_grps = {'metrics': ['Length', 'Width', 'Thickness', 'Weight'],
                'classify': ['MaterialTypeName', 'ManufactureName', 'FabricTypeName', 'Form', 'Note',
                             'VesselPartOther', 'WareTypeOther'],
                'production': ['Chronology', 'CultureOther', 'RegionOther', 'EnteredDate', 'EarlyChrono',
                               'LateChrono', 'Catalan'],
                'tile_brick': ['TileType', 'TileIsStamped', 'TileIsCurved', 'BrickIsStamped'],
                'macro_fabric': ['SherdCondition', 'SurfaceTexture', 'SurfTextureOther', 'SurfaceCondition',
                                 'SurvCondOther', 'SurfaceTreatExt', 'STEOther', 'SurfaceTreatInt', 'STIOther',
                                 'HardnessSurface', 'HardnessCore', 'FiringCore', 'ColorExt', 'ColorInt',
                                 'ColorCore', 'InclusionOther', 'DomInclusion', 'DomInclusionOther',
                                 'InclusionSorting', 'InclusionShape', 'InclusionDensity', 'InclusionSize',
                                 'InclusionLargestSize', 'InclusionTexture']
            }

    query = """SELECT Sherd.*, FabricType.*, Field.FieldNumber, SurveyPoint.Northing, SurveyPoint.Easting, 
                      Surveyor.SurveyorName, ManufactureMethod.ManufactureName
               FROM Sherd
               LEFT JOIN Field ON Sherd.FieldId=Field.FieldId
               LEFT JOIN FabricType ON Sherd.FabricType=FabricType.FabricTypeId
               LEFT JOIN SurveyPoint ON SurveyPoint.SurveyPointId = Sherd.SurveyPointId
               LEFT JOIN Surveyor ON SurveyPoint.SurveyorId=Surveyor.SurveyorId
               LEFT JOIN ManufactureMethod ON Sherd.ManufactureMethod=ManufactureMethod.ManufactureID
               """
    artifacts_df = db_query(query, **kwargs)

    if include_discards is False:
        artifacts_df = artifacts_df[artifacts_df['FabricTypeName'] != 'Discarded']

    cols = base
    for s in sections:
        if s in col_grps.keys():
            cols += col_grps[s]

    artifacts_df = artifacts_df[cols]

    if 'waretypes' in sections:
        waretypes = db_query("""SELECT swt.SherdId, wt.WareTypeName
                                     FROM SherdWareType AS swt
                                     LEFT JOIN WareType AS wt ON swt.WareTypeId=wt.WareTypeId
                                     LEFT JOIN Sherd ON Sherd.SherdId=swt.SherdId
                                     """)

        dummies = _pd.get_dummies(waretypes['WareTypeName']).rename(  # one hot encoding
            columns={'other': 'other_waretype', 'unknown': 'unknown_waretype'})
        waretypes = waretypes.merge(dummies, how='left', left_index=True, right_index=True)  # attach to original
        waretypes = waretypes.groupby('SherdId').sum()  # groupby to collapse duplicate SherdIds
        artifacts_df = artifacts_df.merge(waretypes, how='left', left_on='SherdId', right_index=True)  # merge with df

    if 'vesselparts' in sections:
        vessel_parts = db_query("""SELECT svp.SherdId, vp.VesselPartName
                                     FROM SherdVesselPart AS svp
                                     LEFT JOIN VesselPart AS vp ON svp.VesselPartId=vp.VesselPartId
                                     LEFT JOIN Sherd ON Sherd.SherdId=svp.SherdId
                                     """)

        dummies = _pd.get_dummies(vessel_parts['VesselPartName']).rename(
            columns={'other': 'other_vesselpart', 'unknown': 'unknown_vesselpart'})  # one hot encoding
        vessel_parts = vessel_parts.merge(dummies, how='left', left_index=True, right_index=True)  # attach to original
        vessel_parts = vessel_parts.groupby('SherdId').sum()  # groupby to collapse duplicate SherdIds
        artifacts_df = artifacts_df.merge(vessel_parts, how='left', left_on='SherdId',
                                          right_index=True)  # merge with df

    if years:
        artifacts_df = artifacts_df[artifacts_df.ChangedDate.dt.year.isin(years)]

    return artifacts_df


#######################################################################################################################


def load_artifacts_simple(include_discards=False, **kwargs):
    """Get a DataFrame of artifacts with the most typical query
    
    Parameters
    ----------
    include_discards : bool
        If True, return all records, even artifacts marked as Discarded.
    **kwargs
        Optional arguments that are passed to get_credentials()
    
    Returns
    -------
    artifacts_df : pandas DataFrame
        DataFrame of all artifacts

    """
    import warnings
    warnings.warn(
        """get_artifacts_simple() is no longer preferred. Use get_artifacts() with appropriate parameters instead.""", DeprecationWarning)
    query = """SELECT Sherd.*, FabricType.*, Field.FieldNumber, SurveyPoint.Northing, SurveyPoint.Easting, 
                      Surveyor.SurveyorName 
               FROM Sherd
               LEFT JOIN Field ON Sherd.FieldId=Field.FieldId
               LEFT JOIN FabricType ON Sherd.FabricType=FabricType.FabricTypeId
               LEFT JOIN SurveyPoint ON SurveyPoint.SurveyPointId = Sherd.SurveyPointId
               LEFT JOIN Surveyor ON SurveyPoint.SurveyorId=Surveyor.SurveyorId
               LEFT JOIN ManufactureMethod ON Sherd.ManufactureMethod=ManufactureMethod.ManufactureID
               """
    artifacts_df = db_query(query, **kwargs)
    if include_discards is False:
        artifacts_df = artifacts_df[artifacts_df['FabricTypeName'] != 'Discarded']

    return artifacts_df


#######################################################################################################################


def load_artifacts_by_year(years, discards=False, **kwargs):
    """Get a DataFrame of artifacts with the most typical query for specified year(s)
    
    Parameters
    ----------
    years : list
        List of desired years; can be strings or integers
    discards : bool
        If True, return all records, even artifacts marked as Discarded.    
    **kwargs
        Optional arguments that are passed to get_credentials()

    Returns
    -------
    artifacts_df : pandas DataFrame
        DataFrame of all artifacts for specified year(s)
        
    """
    import warnings
    warnings.warn(
        """get_artifacts_by_year() is no longer preferred. Use get_artifacts() with appropriate parameters instead.""",
        DeprecationWarning)
    artifacts_df = load_artifacts_simple(include_discards=discards, **kwargs)
    artifacts_df = artifacts_df[artifacts_df.ChangedDate.dt.year.isin(years)]
    return artifacts_df


#######################################################################################################################


def load_productions_simple(**kwargs):
    """Get a DataFrame of productions with the most typical query

    Parameters
    ----------
    **kwargs
        Optional arguments that are passed to get_credentials()

    Returns
    -------
    prods_df : pandas DataFrame
        DataFrame of all productions
    """
    query = """SELECT *
               FROM FabricType
               """
    prods_df = db_query(query, **kwargs)
    return prods_df


#######################################################################################################################


def load_production_cts_wts(**kwargs):
    """Create a DataFrame of all points with columns for counts and weights of all productions

    Parameters
    ----------
    **kwargs
        Optional arguments that are passed to get_credentials()

    Returns
    -------
    cts_wts : pandas DataFrame
        DataFrame of all points with counts and weights for all productions
        
    Notes
    -----
    Also pulls in some non-vessel artifact types (e.g., tile, brick, other construction material)
    
    """
    artifacts = load_artifacts(sections=['metrics', 'classify', 'production', 'tile_brick'], **kwargs)
    points = load_points(**kwargs)
    
    # For artifacts without a Production (i.e., tiles, bricks, etc), use their MaterialType as their Production. If
    # MaterialType is Tile, use TileType ('Tegula' or 'Imbrex')
    artifacts['Production'] = artifacts['FabricTypeName'].where(~artifacts['FabricTypeName'].isnull(),
                                                                artifacts['MaterialTypeName'].where(
                                                                    artifacts['TileType'].isnull(),
                                                                    artifacts['TileType']))

    artifacts['Production'] = artifacts['Production'].where(
        ~((artifacts.Note.str.contains('signinum')) | (artifacts.Note.str.contains('Signinum'))),
        'Opus signinum')

    # summarize artifacts by point
    art_cts = artifacts.groupby(['SurveyPointId', 'Production']).agg({'Production': 'size', 'Weight': 'sum'}).unstack()
    
    # merge Production (counts) and Weight (weights) with the points df
    # do this in two steps so that we can append the _ct and _wt suffixes to columns
    cts = _pd.merge(points, art_cts['Production'], how='left', left_on='SurveyPointId', right_index=True)
    cts_wts = _pd.merge(cts, art_cts['Weight'], how='left', left_on='SurveyPointId', right_index=True,
                        suffixes=('_ct', '_wt'))
    return cts_wts


#######################################################################################################################


def load_points_times(warn='enable', **kwargs):
    """Get a DataFrame of points with datetimes cleaned and search times calculated
    
    Parameters
    ----------
    warn : {'enable', 'disable'}
        Argument passed to the `calc_search_time()` function specifying whether or to print a generic warning message.
    **kwargs
        Optional arguments that are passed to get_credentials()
    
    Returns
    -------
    pts : pandas DataFrame
        DataFrame of all points with adjusted datetimes and search times
    """
    pts = calc_search_time(clean_datetimes(load_points(**kwargs)), warn=warn)
    return pts


#######################################################################################################################
