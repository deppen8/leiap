"""
This file contains functions related to the annual report
"""


import pandas as _pd
# import numpy as _np
# import altair as _alt


#######################################################################################################################


def fields_summary_table(points, artifacts, fid_col='geo_field',
                         save_excel=False, excel_file='field_counts.xlsx', excel_sheet='field_data'):
    """Create table (in Spanish) with basic stats by field
        
    Parameters
    ----------
    points : DataFrame
        pandas DataFrame of survey points
    artifacts : DataFrame
        pandas DataFrame of artifacts
    fid_col: str, optional
        Column containing the field identifier to use for grouping
    save_excel : bool, optional
        Specify whether to write DataFrame to an Excel sheet
    excel_file : str, optional
        Filename for Excel
    excel_sheet : str, optional
        Sheet name for Excel
        
    Returns
    -------
    fields_data : DataFrame
        DataFrame version of the created table
        
    Notes
    -----
    The table is in the form:
    
    | Polígono | Parcela | Subparcela |   Id   | Núm. Pts. | Núm. Frags. | Pos. Pts. |
    | -------- | ------- | ---------- | ------ | --------- | ----------- | --------- |
    |    03    |   027   |      0     | 030270 |    351    |     39      |     26    |
    |    16    |   092   |      a     | 16092a |    105    |     58      |     51    |

    """
    # count number of points per geographic field
    fields = points_per_group(points, grouper_col=fid_col, ct_col='Núm. Pts.')

    # count number of artifacts per field
    artifact_cts = artifacts_per_group(artifacts, grouper_col=fid_col, ct_col='Núm. Frags.')

    # count number of points with artifacts per field
    pos_pts = pos_points_per_group(artifacts, grouper_col=fid_col, pt_id_col='SurveyPointId', ct_col='Pos. Pts.')

    # concatenate the three dataframes created above with an outer join
    fields_data = _pd.concat([fields, artifact_cts, pos_pts], axis=1).fillna(0)
    fields_data.reset_index(inplace=True)
    fields_data.rename(columns={'index': 'Id'}, inplace=True)

    # set counts columns to proper integer datatypes
    fields_data[['Núm. Pts.', 'Núm. Frags.', 'Pos. Pts.']] = fields_data[
        ['Núm. Pts.', 'Núm. Frags.', 'Pos. Pts.']].astype(int)
    
    # split up the `Id` column into various components
    fields_data['Polígono'] = fields_data['Id'].str[0:2]
    fields_data['Parcela'] = fields_data['Id'].str[2:5]
    fields_data['Subparcela'] = fields_data['Id'].str[5]

    # reorder columns
    fields_data = fields_data[['Polígono', 'Parcela', 'Subparcela', 'Id', 'Núm. Pts.', 'Núm. Frags.', 'Pos. Pts.']]
    
    if save_excel:
        # save to Excel sheet
        fields_data.to_excel(excel_file, sheet_name=excel_sheet)
        
    return fields_data


#######################################################################################################################


def points_per_group(points, grouper_col, ct_col='Núm. Pts.'):
    """Count the points in the given group
    
    Parameters
    ----------
    points : pandas DataFrame
        Point observations
    grouper_col : str
        Column in `points` that you want to use to group, usually 'geo_field' or similar
    ct_col : str, optional
        Name to give the new column
    
    Returns
    -------
    df : pandas DataFrame
        Points grouped and counted according to the grouper_col    
    """
    df = points.groupby(grouper_col).size().reset_index(name=ct_col).set_index(grouper_col)
    df.index.rename('Id', inplace=True)
    return df


#######################################################################################################################


def artifacts_per_group(artifacts, grouper_col, ct_col='Núm. Frags.'):
    """Count the artifacts in the given group

    Parameters
    ----------
    artifacts : pandas DataFrame
        Artifact observations
    grouper_col : str
        Column in `artifacts` that you want to use to group, usually 'geo_field' or similar
    ct_col : str, optional
        Name to give the new column

    Returns
    -------
    df : pandas DataFrame
        Artifacts grouped and counted according to the grouper_col
    """
    df = artifacts.groupby(grouper_col).size().reset_index(name=ct_col).set_index(grouper_col)
    return df

#######################################################################################################################


def pos_points_per_group(artifacts, grouper_col, pt_id_col='SurveyPointId', ct_col='Pos. Pts.'):
    """Count the number of points with artifacts in the given group

    Parameters
    ----------
    artifacts : pandas DataFrame
        Artifact observations
    grouper_col : str
        Column in `artifacts` that you want to use to group, usually 'geo_field' or similar
    pt_id_col : str, optional
        Column that contains unique point identifier, usually 'SurveyPointId'
    ct_col : str, optional
        Name to give the new column

    Returns
    -------
    df : pandas DataFrame
        Number of points with artifacts grouped and counted according to the grouper_col
    """
    df = artifacts.groupby([grouper_col, pt_id_col]).size().reset_index().set_index(grouper_col)
    df = df.groupby(grouper_col).size().reset_index(name=ct_col).set_index(grouper_col)
    return df

#######################################################################################################################


# def time_span_chart(artifacts, prod_col, start='EarlyChrono', end='LateChrono', out_file='time_span_chart.png'):
#     """Make time span chart for productions
#
#     Notes
#     -----
#     1. Proportion groups not even
#     """
#     _alt.data_transformers.enable('json')
#
#     # work with smaller subset of data
#     df = artifacts[['EarlyChrono', 'LateChrono', 'Catalan']][~artifacts['EarlyChrono'].isnull()]
#
#     prods = df.iloc[0:5].groupby(['Catalan', 'EarlyChrono', 'LateChrono']
#                                 ).size().reset_index().rename(columns={0:'count'})  # frequency counts
#     prods['freq'] = 100*prods['count'] / prods['count'].sum()  # proportions
#
#     conditions = [                                # condition used to group proportions
#         prods['freq']<=10,
#         (prods['freq']>10) & (prods['freq']<=25),
#         (prods['freq']>25) & (prods['freq']<=50),
#         (prods['freq']>50) & (prods['freq']<=75),
#         (prods['freq']>75) & (prods['freq']<=90),
#         (prods['freq']>90) & (prods['freq']<=100)
#     ]
#
#     groups = ['<10%', '10-25%', '25-50%', '50-75%', '75-90%', '>90%']  # group names
#     prods['group'] = _np.select(conditions, groups)  # apply conditions
#
#     periods = _pd.DataFrame({'name':['Navetiforme','Talaiòtic','Postalaiòtic','Romana','Vàndala','Bizantina',
#                                      'Àndalusina','Medieval Cristiana','Moderna','Contemporània'],
#                             'end':[-850, -550, -123, 455, 533, 902, 1229, 1492, 1789, 1900],
#                             'label_loc':[-1325.0, -700.0, -336.5, 166.0, 494.0, 717.5, 1065.5, 1360.5, 1640.5, 1844.5]
#
#                            })
#
#     chart = _alt.Chart(prods).mark_bar().encode(       # make chart with altair
#         x=_alt.X('EarlyChrono:Q',
#                 axis=_alt.Axis(title='Anys', grid=False)),
#         x2=_alt.X('LateChrono:Q'),
#         y=_alt.Y('Catalan:N',
#                 sort=_alt.SortField(field='EarlyChrono', op='mean', order='ascending'),
#                 axis=_alt.Axis(title='Producció'),
#                 scale=_alt.Scale(type='point')
#                ),
# #         size='freq:Q',
#         size=_alt.Size('group:N', scale=_alt.Scale(domain=groups,
#                                                  range=[10,30,50,70,90,110]
#                                                 )),
#         color=_alt.Color('group:N',
#             legend=_alt.Legend(title='Proporció'),
#             scale=_alt.Scale(
#                 domain=groups,
#                 range=['#f7f7f7','#d9d9d9','#bdbdbd','#969696','#636363','#252525']))  # gradient of grays to black
#     )
#
#
#     rules = _alt.Chart(periods).mark_rule(color='#d9d9d9', opacity=0.5, strokeDash=[5,10]).encode(
#         x='end',
#     )
#
#     rule_labels = _alt.Chart(periods).mark_text(align='center',baseline='middle', angle=270,color='#bdbdbd').encode(
#         text='name',
#         x='label_loc'
#     )
#
#     return chart + rules + rule_labels
#
# #######################################################################################################################
