"""
This file contains functions for making maps
"""


from .spatial import *
from .report import *

# import cartopy.crs as _ccrs
import matplotlib.pyplot as _plt


#######################################################################################################################


def field_explorer(artifacts, points, fields_shp_path, html_file_out=""):
    """Create bokeh map with summary information about all fields
    
    Parameters
    ----------
    artifacts, points : pandas DataFrames
    fields_shp_path : str
        Path to the shapefile of fields
    html_file_out : str
        Path to save the output file
    
    Returns
    -------
    None
    
    Notes
    -----
    If you want to print the output in a Jupyter notebook, use
    
    `from bokeh.io import output_notebook; output_notebook()`
    
    before running the function.
    """
    from bokeh.io import show
    from bokeh.plotting import figure, output_file
    from bokeh.models import (
        GeoJSONDataSource,
        HoverTool,
        PanTool,
        WheelZoomTool,
        BoxZoomTool,
        ResetTool,
        NumeralTickFormatter,
    )

    geo_artifacts = find_geo_field(
        artifacts, fields_shp_path
    )  # find geofield for artifacts
    geo_points = find_geo_field(points, fields_shp_path)  # find geofield for points

    fields_sum = fields_summary_table(
        geo_points, geo_artifacts
    )  # summarize artifacts by geofield
    fields_shp = read_fields_shp(
        fields_shp_path
    )  # get fields shapefile as geodataframe

    # attach artifact summaries to fields geodataframe
    fields_merge = fields_shp.merge(
        fields_sum, how="left", left_on="fid", right_on="Id"
    )
    fields_merge = fields_merge.rename(
        columns={  # renaming columns makes them usable
            "Polígono": "polygon",  # as tooltips in the bokeh plot
            "Parcela": "parcel",
            "Subparcela": "subparcel",
            "Id": "id",
            "Núm. Pts.": "n_pts",
            "Núm. Frags.": "n_frags",
            "Pos. Pts.": "pos_pts",
        }
    )

    surveyed = fields_merge[
        ~fields_merge["n_pts"].isna()
    ]  # get separate dataframes for
    unsurveyed = fields_merge[
        fields_merge["n_pts"].isna()
    ]  # surveyed and unsurveyed fields
    surveyed_geojson = surveyed.to_json()  # convert both to geo_json
    unsurveyed_geojson = unsurveyed.to_json()

    surveyed_source = GeoJSONDataSource(geojson=surveyed_geojson)  # convert JSON to
    unsurveyed_source = GeoJSONDataSource(
        geojson=unsurveyed_geojson
    )  # bokeh GeoJSONDataSource

    output_file(html_file_out)

    surveyed_hover = [
        ("Status", "surveyed"),
        ("Campo", "@fid"),
        ("Núm. Pts.", "@n_pts"),
        ("Pos. Pts.", "@pos_pts"),
        ("Núm. Frags.", "@n_frags"),
    ]

    unsurveyed_hover = [("Status", "not surveyed"), ("Campo", "@fid")]

    p = figure(
        plot_width=600,
        plot_height=450,
        tools=[PanTool(), WheelZoomTool(), BoxZoomTool(), ResetTool()],
    )
    p.xaxis[0].formatter = NumeralTickFormatter(format="0")
    p.yaxis[0].formatter = NumeralTickFormatter(format="0")

    s = p.patches(
        xs="xs",
        ys="ys",
        source=surveyed_source,
        line_color="gray",
        fill_color="lightgreen",
    )
    p.add_tools(HoverTool(renderers=[s], tooltips=surveyed_hover))

    u = p.patches(
        xs="xs",
        ys="ys",
        source=unsurveyed_source,
        line_color="gray",
        fill_color="seashell",
    )
    p.add_tools(HoverTool(renderers=[u], tooltips=unsurveyed_hover))

    show(p)


#######################################################################################################################


def single_field_map(field, fields_gdf, axis_len=500, save_path=None):
    """Make a map centered on a specified field

    Parameters
    ----------
    field : str
        Survey field ID for field of interest
    fields_gdf : geopandas GeoDataFrame
        geopandas GeoDataFrame of all fields
    axis_len : int, optional
        Length of both x and y axes
    save_path : str, optional
        If not None, location and filename for output

    Returns
    -------
    field_map : matplotlib Figure
        Styled map of desired field

    """
    selected = fields_gdf[fields_gdf["fid"] == field]  # isolate desired field as a gdf
    unselected = fields_gdf[fields_gdf["fid"] != field]  # get all other fields as a gdf

    bounds = (
        selected.bounds
    )  # find bounding box of selected field and extract mins and maxs
    minx, maxx, miny, maxy = (
        bounds.minx.iloc[0],
        bounds.maxx.iloc[0],
        bounds.miny.iloc[0],
        bounds.maxy.iloc[0],
    )

    h_mid = minx + (
        (maxx - minx) / 2
    )  # find horizontal midpoint of selected field's bounding box
    v_mid = miny + ((maxy - miny) / 2)  # find vertical midpoint

    xax_min = h_mid - axis_len / 2  # find min/max dimensions from midpoints
    xax_max = h_mid + axis_len / 2
    yax_min = v_mid - axis_len / 2
    yax_max = v_mid + axis_len / 2

    field_map = draw_single_field_map(
        selected, unselected, xlim=(xax_min, xax_max), ylim=(yax_min, yax_max)
    )

    if save_path:  # save, if desired
        field_map.savefig(save_path)

    _plt.close("all")

    return field_map


#######################################################################################################################


# def draw_single_field_map(target_field_gdf, other_fields_gdf, xlim, ylim):
#     """Create map image for single field
#
#     Parameters
#     ----------
#     target_field_gdf : geopandas GeoDataFrame
#         A GeoDataFrame of one row with the survey field of interest
#     other_fields_gdf : geopandas GeoDataFrame
#         All other fields
#     xlim : two-member list or tuple of floats
#         x axis min and max
#     ylim : two-member list or tuple of floats
#         y axis min and max
#
#     Returns
#     -------
#     fig : matplotlib Figure
#         Figure object that can be printed or saved
#
#     Notes
#     -----
#     This function is defined separately from `single_field_map()` so that all of the cartographic/design elements of the plot are conveniently grouped in one function
#
#     """
#
#     fig = _plt.figure(figsize=(5, 5))  # create empty figure
#     ax = fig.add_subplot(1, 1, 1, projection=_ccrs.UTM('31S'))  # create ax to plot on
#     ax.set_extent((xlim[0], xlim[1], ylim[0], ylim[1]), crs=_ccrs.UTM('31S'))
#     ax.add_geometries(other_fields_gdf.geometry, crs=_ccrs.UTM('31S'), facecolor='gray')  # add 'other' fields
#     ax.add_geometries(target_field_gdf.geometry, crs=_ccrs.UTM('31S'), facecolor='green')  # add central field
#
#     return fig


#######################################################################################################################
