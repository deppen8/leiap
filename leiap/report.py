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


def group_artifacts(artifact_data, col='geo_field'):
    """Create pandas `GroupBy` object of artifacts
    
    Parameters
    ----------
    artifact_data : pandas DataFrame
        DataFrame of artifacts with columns `'geo_field'`,`'Catalan'`, `'EarlyChrono'`, `'LateChrono'`
    col : str, optional
        Column to use for grouping (the default is 'geo_field')
    
    Returns
    -------
    pandas `GroupBy`
        `GroupBy` object that can be iterated over
    """

    data_sub = artifact_data.loc[:, ['geo_field','Catalan', 'EarlyChrono', 'LateChrono']]
    return data_sub.groupby([col])


#######################################################################################################################


def prep_report_data(group):
    """Calculate counts and percentages for each production in a group (usually a `geo_field`)
    
    Parameters
    ----------
    group : pandas DataFrame
        Data from a single group (usually a `geo_field`)
    
    Returns
    -------
    pandas DataFrame
        Same as input DataFrame with new `count` and `pct` columns calculated
    """

    data_group = group.groupby(['Catalan', 'EarlyChrono', 'LateChrono']).count().reset_index().rename(columns={'geo_field':'count'})
    data_group['pct'] = (data_group['count'] / data_group['count'].sum() *100).round(decimals=2)
    
    return data_group


#######################################################################################################################


def time_span_chart(data):
    """Create a chart showing all productions, their counts, their percentages, and their time spans
    
    Parameters
    ----------
    data : pandas DataFrame
        Data containing columns `['Catalan', 'EarlyChrono', 'LateChrono', 'count', 'pct']`
    
    Returns
    -------
    fig: matplotlib Figure
    """

    import matplotlib.pyplot as plt
    from matplotlib import collections as mc
    from matplotlib.lines import Line2D
    import seaborn as sns
    
    def make_proxy(zvalue, scalar_mappable, **kwargs):
        """Helper function for creating the legend
        """
        COLOR = 'black'
        return Line2D([0, 1], [0, 1], color=COLOR, solid_capstyle='butt', **kwargs)

    data = data.sort_values(by='EarlyChrono', ascending=False)
    data = data.assign(order_y=[i+1 for i in range(data.shape[0])])
    
    # create tuples of the form (x_start, order_y) and (x_end, order_y)] for each production
    data['start_pt'] = list(zip(data['EarlyChrono'], data['order_y']))
    data['end_pt'] = list(zip(data['LateChrono'], data['order_y']))

    # create label for production type and count (Catalan)
    data['ylabel'] = data['Catalan'].map(str) + ' - ' + data['count'].map(str)

    # make list of lists of coordinates
    field_lines = [list(a) for a in zip(data['start_pt'], data['end_pt'])]    

    # items needed for legend construction
    LW_BINS = [0,10,25,50,75,90,100] # bins for line width
    LW_LABELS = [3,6,9,12,15,18] # line widths
    
    # convert percentages to line widths based on bin values
    data['lw'] = _pd.cut(data['pct'], bins=LW_BINS, labels=LW_LABELS)
    data['lw'] = _pd.to_numeric(data['lw'])

    # lines for each production with linewidths as determined above
    lc = mc.LineCollection(field_lines, color='black', linewidths=list(data['lw']))

    # start and end values for x-axis (negative = BC, positive = AD)
    START = -1600
    END = 2001
    
    # create thin gray lines that stretch horizontally across the whole plot
    data['gray_start'] = START
    data['gray_end'] = END
    data['gray_start_pt'] = list(zip(data['gray_start'], data['order_y']))
    data['gray_end_pt'] = list(zip(data['gray_end'], data['order_y']))
    gray_lines = [list(B) for B in zip(data['gray_start_pt'], data['gray_end_pt'])]
    
    # horizontal gray lines
    lc2 = mc.LineCollection(gray_lines, color='gray', linewidth=0.5)
    
    
    # units for plot creation; t='top', b='bottom'
    HEIGHT_UNIT = 0.25
    T = 1.5; B = 1.0  #inch

    # x-ticks
    INTERVAL = 400 # x-axis tick interval
    xticks = [x for x in range(START, END, INTERVAL)] # create ticks

    # x-values for vertical lines to be added representing time period boundaries
    VERT_LINES = [-850, -550, -123, 455, 533, 902, 1229, 1492, 1789]

    # time period labels
    # pos = abs(start-val)/float(abs(end-start))
    TLABEL_V = 1.05; TLABEL_ANG = 90
    PERIOD_LABELS = {'Navetiforme':[abs(START-(-1225))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                    'Talaiòtic':[abs(START-(-700))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                    'Posttalaiòtic':[abs(START-(-336.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                    'Romana':[abs(START-(166))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                    'Vàndala':[abs(START-(500))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                    'Bizantina':[abs(START-(717.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                    'Àndalusina':[abs(START-(1065.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                    'Medieval\nCristiana':[abs(START-(1360.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                    'Moderna':[abs(START-(1640.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                    'Contemporània':[abs(START-(2000))/float(abs(END-START)), TLABEL_V, TLABEL_ANG]}

    
    # create plot and set properties
    sns.set(style="ticks")
    sns.set_context("notebook")

    height = HEIGHT_UNIT*(data.shape[0]+1)+T+B
    fig = plt.figure(figsize=(11, height))
    ax = fig.add_subplot(111)
    ax.set_ylim(0, data.shape[0]+1.0)
    fig.subplots_adjust(bottom=B/height, top=1-T/height, left=0.3, right=1.0)

    ax.add_collection(lc2)
    ax.add_collection(lc)

    ax.set_xlim(left=START, right=END)
    ax.set_xticks(xticks)
    ax.xaxis.set_ticks_position('bottom')

    sns.despine(left=True)

    ax.set_yticks(data['order_y'])
    ax.set(yticklabels=data['ylabel'])
    ax.tick_params(axis='y', length=0)

    # place time period vertical lines from list of x values
    for vline in VERT_LINES:
        plt.axvline(x=vline, ls='dashed', lw=0.5, color='gray')

    # place time period labels
    for period, val in PERIOD_LABELS.items():
        ax.text(x=val[0], y=val[1], s=period, color='gray', fontsize=10, horizontalalignment='center', verticalalignment='bottom',
               rotation=val[2], transform=ax.transAxes)

    # legend
    proxies = [make_proxy(item, lc, linewidth=item) for item in LW_LABELS]
    leg = ax.legend(proxies, ['0-10%', '10-25%', '25-50%', '50-75%', '75-90%', '90-100%'], bbox_to_anchor=(0.2, 0.0), 
                    bbox_transform=fig.transFigure, loc='lower left', ncol=6, labelspacing=3.0, handlelength=4.0, handletextpad=0.5, markerfirst=False, 
                    columnspacing=1.0, frameon=False)

    for txt in leg.get_texts():
        txt.set_ha("left") # horizontal alignment of text item
#         txt.set_x(0) # x-position
#         txt.set_y() # y-position
    
    return fig


#######################################################################################################################


def write_excel_table(unit, data, writer):
    """Format data and add as worksheet to Excel output
    
    Parameters
    ----------
    unit : str
        Name of field or other data group; will be used as Sheet name in Excel
    data : pandas `DataFrame`
        Data to write to the file
    writer : `ExcelWriter`
        Excel file
    
    Returns
    -------
    None
    """

    table_data = data.loc[:,['Catalan', 'count', 'pct']].rename(columns={'Catalan':'Producció', 'count':'Núm', 'pct':'%'})
    MAX_LEN = 40
    table_data.to_excel(writer, sheet_name=str(unit), index=False, startrow=1, header=False)

    workbook  = writer.book
    worksheet = writer.sheets[str(unit)]

    #header
    header_format = workbook.add_format({'bold': True, 'align':'center', 'font_name':'Arial', 'font_size':10, 'bottom':2})
    for col_num, value in enumerate(table_data.columns.values):
        worksheet.write(0, col_num, value, header_format)

    header_format2 = workbook.add_format({'bold': True, 'align':'right', 'font_name':'Arial', 'font_size':10, 'bottom':2})
    worksheet.write(0, 0, 'Producció', header_format2)

    colA_format = workbook.add_format({'align':'right', 'font_name':'Arial', 'font_size':10})
    worksheet.set_column('A:A', MAX_LEN, colA_format)

    colB_format = workbook.add_format({'align':'center', 'font_name':'Arial', 'font_size':10})
    worksheet.set_column('B:B', None, colB_format)

    colC_format = workbook.add_format({'align':'center', 'num_format':'0.0', 'font_name':'Arial', 'font_size':10})
    worksheet.set_column('C:C', None, colC_format)


#######################################################################################################################


def make_report_tables(groups, output_folder, fname='field_tables.xlsx'):
    """Create and save Excel file with a Sheet for each group in `groups`
    
    Parameters
    ----------
    groups : pandas `GroupBy`
        `GroupBy` object like those returned by `group_artifacts()`
    output_folder : str
        Folder to save the final Excel
    fname : str, optional
        Name of the Excel file (the default is 'field_tables.xlsx')
    
    Returns
    -------
    None
    """

    writer = _pd.ExcelWriter(f'{output_folder}{fname}', engine='xlsxwriter')
    for unit, data in groups:
        print(type(data))
        d = prep_report_data(data)
        write_excel_table(unit, d, writer)
   
    writer.save()
    print(f'Excel file saved to {output_folder}{fname}')


#######################################################################################################################


def make_report_span_charts(groups, output_folder, file_prefix=''):
    """Create and save production span charts
    
    Parameters
    ----------
    groups : pandas `GroupBy`
        `GroupBy` object like those returned by `group_artifacts()`
    output_folder : str
        Folder to save the final image
    file_prefix : str, optional
        Extra text to add to the beginning of the file name (the default is an empty string `''`, which adds no text). All file names will end with the `unit` from `groups` (e.g., the field number)

    Returns
    -------
    None    
    """

    import matplotlib.pyplot as plt
    for unit, data in groups:
        d = prep_report_data(data)
        time_span_chart(d)
        plt.savefig(f'{output_folder}{file_prefix}{unit}.png', dpi=300)
    
    plt.close('all')
    print(f'Image file(s) saved to {output_folder}')
