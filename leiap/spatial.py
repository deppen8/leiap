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


def convert_coordinates(df, x_col='Easting', y_col='Northing', from_epsg='32631', to_epsg='3857'):
    """Transform coordinates from one system to another

    Parameters
    ----------
    df : pandas DataFrame
        Points or artifacts DataFrame with coordinate columns
    x_col, y_col : str
        Columns with x- and y-coordinates
    from_epsg, to_epsg : str
        EPSG coordinate system codes for the input and output coordinates

    Returns
    -------
    df : pandas DataFrame
        Original DataFrame with new columns 'x2' and 'y2'

    Notes
    -----
    Default behavior is to convert UTMs from Zone 31N to Web Mercator
    """
    from functools import partial
    from shapely.ops import transform
    import pyproj

    df['new_coords'] = df.apply(lambda row: transform(partial(pyproj.transform,
                                                              pyproj.Proj(init=f'EPSG:{from_epsg}'),
                                                              pyproj.Proj(init=f'EPSG:{to_epsg}')),
                                                      _Point(row.loc[x_col], row.loc[y_col])), axis=1)
    df['x2'] = df['new_coords'].apply(lambda pt: pt.x)
    df['y2'] = df['new_coords'].apply(lambda pt: pt.y)
    df.drop(columns=['new_coords'], inplace=True)

    return df


#######################################################################################################################
