"""
Some of the functions check the data entered in the database for errors or incongruities.
"""

from leiap.io import *


#######################################################################################################################


def check_all():
    """Run all check functions with some basic parameters
    
    Returns
    -------
    checks : dict of pandas DataFrames
    """
    checks = dict()
    checks['coords'] = check_coords_in_municipi()
    
    checks['handmade'] = check_handmade()
    
    for measure in ['Length', 'Width', 'Thickness', 'Weight']:
        checks[measure] = check_measurement(measure, 3)
    
    return checks


#######################################################################################################################


def check_coords_in_municipi():
    """Detect Eastings or Northings that do not lie within Son Servera
    """   
    # Son Servera municipality min/max coordinates
    min_easting, max_easting = 527509.3825000008, 537483.8490000003
    min_northing, max_northing = 4383439.635000001, 4391457.568000001
    
    points = load_points()
    bad_coords = points[(points['Easting'] <= min_easting) | (points['Easting'] >= max_easting) |
                        (points['Northing'] <= min_northing) | (points['Northing'] >= max_northing)]
    if bad_coords.shape[0] > 0:
        print('Some problems detected with the Eastings/Northings')
    else:
        print('No problems detected with the Eastings/Northings')
    
    return bad_coords


#######################################################################################################################


def check_handmade():
    """Find any indigenous sherds that are not marked as handmade
    """
    artifacts = load_artifacts(sections=['classify'])
    
    # types that are always handmade (hecho a mano)
    amano_types = ['Bronze Age pottery', 'Talaiotic pottery', 'Post-talaiotic pottery']
    flagged = artifacts[(artifacts['FabricTypeName'].isin(amano_types)) & (artifacts['ManufactureMethod'] != 1)]
    
    if flagged.shape[0] > 0:
        print('Some problems detected with handmade pottery')
    else:
        print('No problems detected with handmade pottery')
    
    return flagged[['SurveyPointId', 'FabricTypeName', 'ManufactureMethod']]


#######################################################################################################################


def check_measurement(measure, sd):
    """Detect outliers
    
    Parameters
    ----------
    measure : {'Length', 'Width', 'Thickness', 'Weight'}
        Measurement column to check
    sd : number
        Cutoff point; number of standard deviations from the mean
    
    Returns
    -------
    outliers : pandas DataFrame
        Outlier artifacts based on input parameters
    """
    from numpy import abs
    df = load_artifacts(sections=['metrics'])
    outliers = df[~(abs(df[measure]-df[measure].mean()) <= (sd*df[measure].std())) &
                  ~(df[measure].isna())].sort_values(measure, ascending=False)
    n = outliers.shape[0]
    if n > 0:
        print('There were '+str(n)+' outliers ('+str(sd)+' SD) detected in '+measure)
    else:
        print('No outliers ('+str(sd)+' SD) detected in '+measure)
    return outliers


#######################################################################################################################
