import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from property_anomaly_detector.features.feature_engineer import normalize_features
from property_anomaly_detector.features.read_df import read_df
from property_anomaly_detector.database import database


def detect(df) -> pd.DataFrame:
    """

    Calculate the outlier score for each property in the given dataset. The higher
    the score the higher is the probability of being a scam. Scams are usually
    advertisements of properties with a relatively small price when comparing to
    similar ones.

    The most important attributes to calculate the score are : The property_type,
    shared_occupancy, latitude, longitude, num_bedrooms, num_recepts.

    Since properties with different types and shared_occupancy have very distinct distributions
    it was decided to perform a group by in the dataset using them. Using a distance based approach
    to calculate the outlier scores with the property type variable is not a good idea. First, to do
    it is necessary to use the OneHotEncoder and this will produce a dataset with a lot of variables.
    Consequently increasing the processing time. If a given property type does not have a lot of properties
    the algorithm will use properties of other types changing the monthly rental price dramatically when
    calculating it.

    The algorithm uses a group by operation on the property_type and shared_occupancy and then
    applies the KNearestNeighbors using the latitude, longitude, num_bedrooms and num_recepts. This will
    get the near property neighbors with a similar amount of bedrooms and receipts. Finally it calculates
    the median monthly_rental_price of the N neighbors and subtract with the property monthly_rental_price.


    :param df: A pandas dataframe with the properties
    :return: The same given dataframe but with the follow additional columns :

        -   Neighbors_median
            The monthly_rental_price median of the N property neighbors
        -   Outlier_score
            The difference between the property monthly_rental_price and
            the its neighbors monthly_rental_price median multiplied by
            -1.

    """
    groups = []
    # The config problem of grouping by districts is that a few districts
    # do not have enough amount of properties.
    for name, group in df.groupby(['property_type', 'shared_occupancy']):
        features = ['latitude', 'longitude', 'num_bedrooms', 'num_recepts']
        df_ml = normalize_features(group[features].values)

        # If the dataset is smaller than the number of neighbors is necessary to reduce
        # the n_neighbors value, otherwise an exception will be raised
        n_neighbors = min([20, len(df_ml)])

        nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(df_ml)
        distances, indices = nbrs.kneighbors(df_ml)

        neighbors_median = np.median(
            group['monthly_rental_price'].iloc[indices.reshape(1, -1)[0]].values.reshape(len(df_ml), n_neighbors),
            axis=1
        ).reshape(-1, 1)

        group['neighbors_median'] = neighbors_median

        # Calculate the deviation
        group['outlier_score'] = (group['monthly_rental_price'].values.reshape(-1, 1) - neighbors_median)
        # Since we care more about the lowest values it's necessary to invert the signals
        # this way makes more intuitive for stakeholders
        group['outlier_score'] *= -1

        groups.append(group)

    return pd.concat(groups)


def detect_db(property: dict = None, save_results=False):
    """

    Read the properties stored in the database and apply calculate the outlier scores
    of them.

    :param property: A dictionary with a property data for the case of which you want to
    calculate the score of an individual property.
    :param save_results: A boolean, if true then it saves the result dataframe in a Mongo
    collection called anomalies

    :return: A pandas dataframe with the database properties and the follow columns :

        -   Neighbors_median
            The monthly_rental_price median of the N property neighbors
        -   Outlier_score
            The difference between the property monthly_rental_price and
            the its neighbors monthly_rental_price median multiplied by
            -1.
    """

    df = read_df(
        {},
        projection={
            'latitude': True,
            'longitude': True,
            'outcode': True,
            'furnished_state': True,
            'rental_prices.shared_occupancy': True,
            'details_url': True,
            'property_type': True,
            'status': True,
            'num_bedrooms': True,
            'num_bathrooms': True,
            'num_floors': True,
            'num_recepts': True,
            'rental_prices.per_month': True
        },
        flatten_attributes=True,
        drop_outliers=True
    )

    # Insert the given property as the first value of the dataframe
    # since this is not sorted is possible to retrieve later
    # using pandas iloc function
    if property is not None:
        property['_id'] = 'property'
        property['shared_occupancy'] = 0 if property['shared_occupancy'] == 'N' else 1
        df = pd.concat([
            pd.DataFrame([property]),
            df
        ])

    df = detect(
        df=df
    )

    if save_results:
        database.save_top_outliers(df.sort_values(by="outlier_score", ascending=False)[:100])

    return df


def classify_property(property: dict):
    """
    Calculate the score of the given property data
    :param property: A dictionary with the property data
    :return: A tuple with the given property anomaly score and the
    highest outlier found when applying the calculation for comparison.
    """
    df = detect_db(property=property)
    property_anomaly_score = df.query("_id == 'property'").iloc[0]['outlier_score']
    highest_anomaly_score = df.sort_values(by="outlier_score", ascending=False).iloc[0]['outlier_score']
    return property_anomaly_score, highest_anomaly_score


if __name__ == "__main__":
    print(detect_db(save_results=True))
