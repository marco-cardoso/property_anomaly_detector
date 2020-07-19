import pandas as pd
import numpy as np
from pyod.models.knn import KNN

from property_anomaly_detector.features.geospatial import get_districts
from property_anomaly_detector.features.read_df import read_df
from property_anomaly_detector.features.feature_engineer import normalize_features, flatten_rental_prices, \
    convert_numerical_cols


def detect(df: pd.DataFrame, columns: list = None, contamination: float = 0.03, n_neighbors: int = 50):
    """
    It detects the outlier properties over the dataframe using KNN.

    To get the default contamination and n_neighbors method values a simple
    experiment was conducted. 50 outliers were labelled and a manual grid search
    executed.

    :param df: Pandas dataframe
    :param columns: Columns to fit the model, if None then it uses all
    available columns
    :param contamination: KNN contamination value
    :param n_neighbors: KNN n_neighbors value
    :return: A pandas dataframe with the anomalies
    """

    if columns is None:
        columns = df.columns

    clf = KNN(n_neighbors=n_neighbors, contamination=contamination, method="median", metric='euclidean', n_jobs=-1)
    clf.fit(df[columns].copy())

    return clf.decision_scores_

    # # 1 == Outlier 0 == Inlier , check more details on PyOD documentation
    # outliers = df[(clf.labels_ == 1)]
    #
    # return outliers


from sklearn.neighbors import NearestNeighbors


def detect_db(contamination: float = 0.03, n_neighbors: int = 50):
    df = read_df(
        default_filter={'status': 'to_rent', 'furnished_state': 'unfurnished', 'property_type': 'Flat',
                        'rental_prices.shared_occupancy': 'N',
                        'rental_prices.per_month': {'$lt': 2200}},
        projection={'latitude': True, 'longitude': True, 'outcode': True, 'furnished_state': True,
                    'rental_prices.shared_occupancy': True, 'details_url': True,
                    'property_type': True, 'status': True, 'num_bedrooms': True, 'num_bathrooms': True,
                    'rental_prices.per_month': True}
    )
    df = flatten_rental_prices(df)
    df = convert_numerical_cols(df)

    df['shared_occupancy'] = df['shared_occupancy'].map({'Y': 1, 'N': 0})

    cum_sum = df['outcode'].value_counts(normalize=True).cumsum()
    mask = cum_sum < 0.99

    df = df[df['outcode'].isin(cum_sum[mask].index.values)]

    df = df.append({
        'latitude': 51.540285,
        'longitude': -0.132809,
        'num_bedrooms': 1,
        'monthly_rental_price': 350
    }, ignore_index=True)

    normalize_mask = ['latitude', 'longitude', 'num_bedrooms']

    df[normalize_mask] = normalize_features(df[normalize_mask].values)

    nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(df[normalize_mask])
    distances, indices = nbrs.kneighbors(df[normalize_mask])

    df['outlier_score'] = df['monthly_rental_price'].values.reshape(-1, 1) - np.median(
        df['monthly_rental_price'].iloc[indices.reshape(1, -1)[0]].values.reshape(len(df), n_neighbors),
        axis=1
    ).reshape(-1, 1)

    return df


if __name__ == "__main__":
    print(detect_db(n_neighbors=5))
