import pandas as pd
from property_anomaly_detector.database import Database

database = Database("zoopla")
default_projection = {
            '_id': False,
            'rental_prices.shared_occupancy' : 1,
            'num_floors' : 1,
            'num_bedrooms' : 1,
            'num_bathrooms' : 1,
            'furnished_state' : 1,
            'category' : 1,
            'property_type' : 1,
            'num_recepts' : 1,
            'latitude': 1,
            'longitude': 1,
            'rental_prices.per_month': 1,
            'outcode': 1,
            'details_url' : 1
}


def read_df(default_filter={}, projection=default_projection) -> pd.DataFrame:
    """
    It reads the data from the database and convert into a pandas dataframe
    :param projection: Dictionary with the projection to use
    :return: A pandas dataframe with the data
    """

    properties = database.get_properties(
        default_filter=default_filter,
        projection=projection
    )

    return pd.DataFrame(properties)



