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
    artifact_cts = artifacts_per_group(
        artifacts, grouper_col=fid_col, ct_col='Núm. Frags.')

    # count number of points with artifacts per field
    pos_pts = pos_points_per_group(
        artifacts, grouper_col=fid_col, pt_id_col='SurveyPointId', ct_col='Pos. Pts.')

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
    fields_data = fields_data[[
        'Polígono', 'Parcela', 'Subparcela', 'Id', 'Núm. Pts.', 'Núm. Frags.', 'Pos. Pts.']]

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
    df = points.groupby(grouper_col).size().reset_index(
        name=ct_col).set_index(grouper_col)
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
    df = artifacts.groupby(grouper_col).size().reset_index(
        name=ct_col).set_index(grouper_col)
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
    df = artifacts.groupby([grouper_col, pt_id_col]).size(
    ).reset_index().set_index(grouper_col)
    df = df.groupby(grouper_col).size().reset_index(
        name=ct_col).set_index(grouper_col)
    return df

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
    LW_BINS = [0, 10, 25, 50, 75, 90, 100]  # bins for line width
    LW_LABELS = [3, 6, 9, 12, 15, 18]  # line widths

    # convert percentages to line widths based on bin values
    data['lw'] = _pd.cut(data['pct'], bins=LW_BINS, labels=LW_LABELS)
    data['lw'] = _pd.to_numeric(data['lw'])

    # lines for each production with linewidths as determined above
    lc = mc.LineCollection(field_lines, color='black',
                           linewidths=list(data['lw']))

    # start and end values for x-axis (negative = BC, positive = AD)
    START = -1600
    END = 2001

    # create thin gray lines that stretch horizontally across the whole plot
    data['gray_start'] = START
    data['gray_end'] = END
    data['gray_start_pt'] = list(zip(data['gray_start'], data['order_y']))
    data['gray_end_pt'] = list(zip(data['gray_end'], data['order_y']))
    gray_lines = [list(B)
                  for B in zip(data['gray_start_pt'], data['gray_end_pt'])]

    # horizontal gray lines
    lc2 = mc.LineCollection(gray_lines, color='gray', linewidth=0.5)

    # units for plot creation; t='top', b='bottom'
    HEIGHT_UNIT = 0.15
    T = 1.0
    B = 0.7  # inch

    # x-ticks
    INTERVAL = 400  # x-axis tick interval
    xticks = [x for x in range(START, END, INTERVAL)]  # create ticks

    # x-values for vertical lines to be added representing time period boundaries
    VERT_LINES = [-850, -550, -123, 455, 533, 902, 1229, 1492, 1789]

    # time period labels
    # pos = abs(start-val)/float(abs(end-start))
    TLABEL_V = 1.01
    TLABEL_ANG = 90
    PERIOD_LABELS = {'Navetiforme': [abs(START-(-1225))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                     'Talaiòtic': [abs(START-(-700))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                     'Posttalaiòtic': [abs(START-(-336.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                     'Romana': [abs(START-(166))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                     'Vàndala': [abs(START-(500))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                     'Bizantina': [abs(START-(717.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                     'Àndalusina': [abs(START-(1065.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                     'Medieval\nCristiana': [abs(START-(1360.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                     'Moderna': [abs(START-(1640.5))/float(abs(END-START)), TLABEL_V, TLABEL_ANG],
                     'Contemporània': [abs(START-(2000))/float(abs(END-START)), TLABEL_V, TLABEL_ANG]}

    # create plot and set properties
    sns.set(style="ticks")
    sns.set_context("notebook")

    height = HEIGHT_UNIT*(data.shape[0]+1)+T+B
    fig = plt.figure(figsize=(6.5, height))
    ax = fig.add_subplot(111)
    ax.set_ylim(0, data.shape[0]+0.5)
    fig.subplots_adjust(bottom=B/height, top=1-T/height, left=0.45, right=0.95)

    ax.add_collection(lc2)
    ax.add_collection(lc)

    ax.set_xlim(left=START, right=END)
    ax.set_xticks(xticks)
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(axis='x', labelsize=8)

    sns.despine(left=True)

    ax.set_yticks(data['order_y'])
    ax.set(yticklabels=data['ylabel'])
    ax.tick_params(axis='y', length=0, labelsize=8)

    # place time period vertical lines from list of x values
    for vline in VERT_LINES:
        plt.axvline(x=vline, ls='dashed', lw=0.5, color='gray')

    # place time period labels
    for period, val in PERIOD_LABELS.items():
        ax.text(x=val[0], y=val[1], s=period, color='gray', fontsize=8, horizontalalignment='center', verticalalignment='bottom',
                rotation=val[2], transform=ax.transAxes)

    # legend
    proxies = [make_proxy(item, lc, linewidth=item) for item in LW_LABELS]
    leg = ax.legend(proxies, ['0-10%', '10-25%', '25-50%', '50-75%', '75-90%', '90-100%'], bbox_to_anchor=(0.05, 0.0),
                    bbox_transform=fig.transFigure, loc='lower left', ncol=6, labelspacing=3.0, handlelength=4.0, handletextpad=0.5, markerfirst=False,
                    columnspacing=0.5, frameon=False, fontsize=8)

    for txt in leg.get_texts():
        txt.set_ha("left")  # horizontal alignment of text item
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

    table_data = data.loc[:, ['Catalan', 'count', 'pct']].rename(
        columns={'Catalan': 'Producció', 'count': 'Núm', 'pct': '%'})
    MAX_LEN = 40
    table_data.to_excel(writer, sheet_name=str(
        unit), index=False, startrow=1, header=False)

    workbook = writer.book
    worksheet = writer.sheets[str(unit)]

    # header
    header_format = workbook.add_format(
        {'bold': True, 'align': 'center', 'font_name': 'Arial', 'font_size': 10, 'bottom': 2})
    for col_num, value in enumerate(table_data.columns.values):
        worksheet.write(0, col_num, value, header_format)

    header_format2 = workbook.add_format(
        {'bold': True, 'align': 'right', 'font_name': 'Arial', 'font_size': 10, 'bottom': 2})
    worksheet.write(0, 0, 'Producció', header_format2)

    colA_format = workbook.add_format(
        {'align': 'right', 'font_name': 'Arial', 'font_size': 10})
    worksheet.set_column('A:A', MAX_LEN, colA_format)

    colB_format = workbook.add_format(
        {'align': 'center', 'font_name': 'Arial', 'font_size': 10})
    worksheet.set_column('B:B', None, colB_format)

    colC_format = workbook.add_format(
        {'align': 'center', 'num_format': '0.0', 'font_name': 'Arial', 'font_size': 10})
    worksheet.set_column('C:C', None, colC_format)


#######################################################################################################################


def make_report_tables(artifacts, group_col, output_folder, fname='field_tables.xlsx'):
    """Create and save Excel file with a Sheet for each group in `groups`

    Parameters
    ----------
    artifacts : pandas `DataFrame`

    group_col : str
        Name of column that contains group info
    output_folder : str
        Folder to save the final Excel
    fname : str, optional
        Name of the Excel file (the default is 'field_tables.xlsx')

    Returns
    -------
    None
    """

    from .constants import get_misc_types

    # where no Catalan name exists, map the Catalan value from the misc dictionary to the MaterialTypeName
    # e.g., 'brick' --> 'maó', 'tile' --> 'teula'
    misc = get_misc_types(lang='both')
    artifacts['Catalan'] = artifacts['Catalan'].where(~artifacts['Catalan'].isnull(),
                                                      artifacts['MaterialTypeName'].map(misc).where(
        artifacts['TileType'].isnull(),
        artifacts['TileType']))

    artifacts['Catalan'] = artifacts['Catalan'].where(
        ~((artifacts['Note'].str.contains('signinum')) |
          (artifacts['Note'].str.contains('Signinum'))),
        'Opus signinum')

    artifacts_sub = artifacts.loc[:, [group_col, 'Catalan']]
    groups = artifacts_sub.groupby([group_col])

    writer = _pd.ExcelWriter(f'{output_folder}{fname}', engine='xlsxwriter')
    for unit, data in groups:
        table_group = data.groupby(['Catalan'])['Catalan'].count().rename(
            columns={'Catalan': 'count'}).reset_index().rename(columns={0: 'count'})
        table_group['pct'] = (
            table_group['count'] / table_group['count'].sum() * 100).round(decimals=2)
        table_group = table_group.sort_values(by='count', ascending=False)
        write_excel_table(unit, table_group, writer)

    writer.save()
    print(f'Excel file saved to {output_folder}{fname}')


#######################################################################################################################

def make_report_span_charts(artifacts, group_col, output_folder, file_prefix=''):
    # def make_report_span_charts(groups, group_col, output_folder, file_prefix=''):
    """Create and save production span charts

    Parameters
    ----------
    artifacts : pandas `DataFrame`

    group_col : str
        Name of column that contains group info
    output_folder : str
        Folder to save the final image
    file_prefix : str, optional
        Extra text to add to the beginning of the file name (the default is an empty string `''`, which adds no text). All file names will end with the `unit` from `groups` (e.g., the field number)

    Returns
    -------
    None    
    """

    import matplotlib.pyplot as plt
    from .constants import get_misc_types

    # where no Catalan name exists, map the Catalan value from the misc dictionary to the MaterialTypeName
    # e.g., 'brick' --> 'maó', 'tile' --> 'teula'
    misc = get_misc_types(lang='both')
    artifacts['Catalan'] = artifacts['Catalan'].where(~artifacts['Catalan'].isnull(),
                                                      artifacts['MaterialTypeName'].map(misc).where(
        artifacts['TileType'].isnull(),
        artifacts['TileType']))

    artifacts['Catalan'] = artifacts['Catalan'].where(
        ~((artifacts['Note'].str.contains('signinum')) |
          (artifacts['Note'].str.contains('Signinum'))),
        'Opus signinum')

    artifacts_sub = artifacts.loc[:, [group_col,
                                      'Catalan', 'EarlyChrono', 'LateChrono']]
    groups = artifacts_sub.groupby([group_col])

    for unit, data in groups:
        span_group = data.groupby(['Catalan', 'EarlyChrono', 'LateChrono'])['Catalan'].count().rename(columns={'Catalan': 'count'}).reset_index(
        ).rename(columns={0: 'count'})
        span_group['pct'] = (span_group['count'] /
                             span_group['count'].sum() * 100).round(decimals=2)

        time_span_chart(span_group)
        plt.savefig(f'{output_folder}{file_prefix}{unit}.png', dpi=300)
        print(f'{file_prefix}{unit}.png saved')

    plt.close('all')
    print(f'{len(groups)} image file(s) saved to {output_folder}')
