import numpy as np
import pandas as pd

from property_anomaly_detector.features.read_df import read_df
from property_anomaly_detector.features.feature_engineer import normalize_features

from sklearn.neighbors import NearestNeighbors


def detect(df: pd.DataFrame, x_variables: list, n_neighbors: int = 50):
    df_ml = normalize_features(df[x_variables].values)

    # If the dataset is smaller than the number of neighbors is necessary to reduce
    # the n_neighbors value, otherwise an exception will be raised
    n_neighbors = min([n_neighbors, len(df)])

    nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(df_ml)
    distances, indices = nbrs.kneighbors(df_ml)

    neighbors_median = np.median(
        df['monthly_rental_price'].iloc[indices.reshape(1, -1)[0]].values.reshape(len(df), n_neighbors),
        axis=1
    ).reshape(-1, 1)

    df['neighbors_median'] = neighbors_median
    df['outlier_score'] = (df['monthly_rental_price'].values.reshape(-1, 1) - neighbors_median) * -1

    return df


def detect_db(filters=None, n_neighbors: int = 50, anomaly_data: dict = None):
    if filters is None:
        filters = {}

    filters['status'] = 'to_rent'

    df = read_df(
        filters,
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
        flatten_attributes=True
    )

    if anomaly_data is not None:
        df = pd.concat([
            pd.DataFrame([anomaly_data]),
            df
        ])

    df = detect(
        df=df,
        x_variables=['latitude', 'longitude', 'num_bedrooms'],
        n_neighbors=n_neighbors
    )

    return df


def classify_property(property: dict, filters: dict):
    df = detect_db(filters, anomaly_data=property)
    property_anomaly_score = df.iloc[-1]['outlier_score']
    highest_anomaly_score = df.sort_values(by="outlier_score", ascending=False).iloc[0]['outlier_score']
    return property_anomaly_score, highest_anomaly_score


if __name__ == "__main__":
    print(detect_db(n_neighbors=5))
