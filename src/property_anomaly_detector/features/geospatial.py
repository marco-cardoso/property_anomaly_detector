from os import path

import geopandas as gpd
import numpy as np
import pandas as pd
import property_anomaly_detector


def get_london_geojson() -> gpd.GeoDataFrame:
    """
    It loads the geojson with the london districts
    :return: A geopandas dataframe with the london districts
    """
    root_path = path.dirname(property_anomaly_detector.__file__)
    geojson_path = path.join(root_path, "datasets", "london.geojson")
    london = gpd.read_file(geojson_path)
    return london


def get_districts(df: pd.DataFrame):
    root_path = path.dirname(property_anomaly_detector.__file__)

    maping_df_path = path.join(root_path, "datasets", "uk_postcodes", "postcodes.csv")
    maping_df = pd.read_csv(maping_df_path).iloc[:, 1:3]

    df['district_code'] = df['outcode'].str.replace("[0-9]", "")

    df = df.merge(maping_df, left_on="district_code", right_on="postcode")

    del df['district_code']
    return df


def get_properties_gdf(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    It converts a pandas dataframe with latitude and longitude into a geopandas dataframe
    :param df: A pandas dataframe with at least three columns : 'latitude', 'longitude' and 'monthly_rental_price'
    :return: A geopandas dataframe
    """
    properties_gpd = gpd.GeoDataFrame(
        df[['latitude', 'longitude', 'monthly_rental_price']],
        geometry=gpd.points_from_xy(df['longitude'], df['latitude'])
    )
    properties_gpd.crs = {'init': 'epsg:4326'}
    return properties_gpd


def plot_london_layer():
    """
    It plots the london districts.
    :return: The plot axis
    """
    ax = london.plot()
    ax.set_axis_off()
    return ax


def plot_geospatial_layer(df: pd.DataFrame, func=np.median, orientation="vertical", title=None, **kwargs):
    """

    It uses geopandas to plot a geospatial layer

    :param df: A pandas dataframe with at least three columns : latitude, longitude and monthly_rental_price
    :param func: A numpy function to aggregate the pandas dataframe observations
    :param orientation: The legend orientation. Options available : 'horizontal' and 'vertical'
    :param title: The plot title
    :param kwargs: Arguments to customize the matplotlib plot
    :return: A dataframe with the aggregation result
    """
    properties_gdf = get_properties_gdf(df)

    join = gpd.sjoin(london, properties_gdf, how="inner")

    district_median_price_agg = join.groupby(['name'], as_index=False).agg(
        {'monthly_rental_price': func, 'geometry': 'first'})

    district_median_price = gpd.GeoDataFrame(
        district_median_price_agg[['name', 'monthly_rental_price']],
        geometry=district_median_price_agg['geometry']
    )

    # ax = district_median_price.plot( alpha=0.5, edgecolor='k')
    ax = district_median_price.plot(
        "monthly_rental_price",
        alpha=0.8,
        edgecolor='k',
        legend=True,
        legend_kwds={
            "label": "Monthly median rental price",
            "orientation": orientation
        },
        cmap="plasma",
        **kwargs
    )

    ax.set_title(title)
    ax.set_axis_off()
    return district_median_price_agg


london = get_london_geojson()
