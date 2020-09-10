import pandas as pd
from property_anomaly_detector.database import database
from property_anomaly_detector.features.feature_engineer import flatten_rental_prices, \
    convert_numerical_cols

default_projection = {
    '_id': False,
    'rental_prices.shared_occupancy': 1,
    'num_floors': 1,
    'num_bedrooms': 1,
    'num_bathrooms': 1,
    'furnished_state': 1,
    'category': 1,
    'property_type': 1,
    'num_recepts': 1,
    'latitude': 1,
    'longitude': 1,
    'rental_prices.per_month': 1,
    'outcode': 1,
    'details_url': 1
}


def read_df(
        filters=None,
        flatten_attributes=False,
        drop_outliers=False,
        projection=None
    ) -> pd.DataFrame:
    """
    It reads the data from the database and convert into a pandas dataframe
    :param drop_outliers: If true then drops outliers based on z-score using price.
    This only works with extremely high values
    :param flatten_attributes: It flattens the rental_prices attributes
    :param filters: A dictionary with the filters to use with MongoDB
    :param projection: Dictionary with the projection to use
    :return: A pandas dataframe with the data
    """

    if projection is None:
        projection = default_projection
    if filters is None:
        filters = {}
    if drop_outliers:
        filters['rental_prices.per_month'] = {'$lt': 2200}

    properties = database.get_properties(
        default_filter=filters,
        projection=projection
    )

    df = pd.DataFrame(properties)

    if flatten_attributes:
        df = flatten_rental_prices(df)

    df.drop_duplicates(inplace=True)
    df = convert_numerical_cols(df)

    df['shared_occupancy'] = df['shared_occupancy'].map({'Y': 1, 'N': 0})

    return df
