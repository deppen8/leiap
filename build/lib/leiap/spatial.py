"""
This file contains functions related to spatial data operations
"""


import pandas as _pd
import geopandas as _gpd
from shapely.geometry import Point as _Point


#######################################################################################################################


def find_geo_field(df, fields_shp_path):
    """Find the identifier for the field where the point or artifact lies geographically.
    
    Parameters
    ----------
    df : pandas DataFrame
        Points or Artifacts DataFrame; must contain 'Easting' and 'Northing' columns
    fields_shp_path : str
        Path to the shapefile (.shp) containing the fields
        
    Returns
    -------
    joined_df : pandas DataFrame
        Identical to the input points DataFrame with an added 'geo_field' column
        
    Notes
    -----
    """

    fields = _gpd.read_file(fields_shp_path)  # load all fields
    fields['fid'] = fields['MASA'].str[-2:] + fields['PARCELA'].str[-3:] + fields['SUBPARCE'].str[0:]
    fields = fields[['fid', 'geometry']]  # get only columns we need
    
    geometry = [_Point(xy) for xy in zip(df['Easting'].fillna(0),  # make coords into shapely Points
                                         df['Northing'].fillna(0))]
    pts_gdf = _gpd.GeoDataFrame(df, geometry=geometry)  # make Points into GeoDataFrame 
    pts_gdf.crs = fields.crs  # make coordinate systems equivalent
    
    joined_df = _gpd.sjoin(pts_gdf,
                           fields,
                           how='inner',
                           op='intersects')  # do a spatial join to find the ACTUAL fields that intersect locations
    joined_df = joined_df.rename(columns={'fid': 'geo_field'})  # returns the geo_field for every record
    
    return joined_df


#######################################################################################################################


def find_artifact_coords(artifacts, points, join_col='SurveyPointId'):
    """Add Easting and Northing to artifacts
    
    Parameters
    ----------
    artifacts : pandas DataFrame
        DataFrame of artifact records
    points : pandas DataFrame
        DataFrame of points; must have 'Easting', 'Northing', and <join_col> columns
    join_col : str
        Column on which to join artifacts and points
        
    Returns
    -------
    artifacts : pandas DataFrame
        Identical to artifacts input DataFrame with 'Easting', 'Northing' columns added
    """
    points = points[['Easting', 'Northing', join_col]]
    artifacts = _pd.merge(artifacts, points, how='left', on=join_col)
    return artifacts


#######################################################################################################################


def read_fields_shp(path):
    """Load and clean up the Survey_Fields_Master.shp file
    
    Notes
    -----
    Not meant to be a generic load function! Designed to work specifically with the file we have been using.
    """
    fields = _gpd.read_file(path)  # load all fields
    fields['fid'] = fields['MASA'].str[-2:] + fields['PARCELA'].str[-3:] + fields['SUBPARCE'].str[0:]
    fields = fields[['fid', 'geometry']]  # get only columns we need
    return fields


#######################################################################################################################
