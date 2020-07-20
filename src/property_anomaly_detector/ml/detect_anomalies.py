import numpy as np
from property_anomaly_detector.features.feature_engineer import normalize_features, flatten_rental_prices, \
    convert_numerical_cols
from property_anomaly_detector.features.read_df import read_df
from sklearn.neighbors import NearestNeighbors


def detect_db(filters={}, n_neighbors: int = 50):
    filters['status'] = 'to_rent'
    filters['rental_prices.per_month'] = {'$lt': 2200}

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
            'num_floors' : True,
            'num_recepts' : True,
            'rental_prices.per_month': True
        }
    )
    df = flatten_rental_prices(df)
    df = convert_numerical_cols(df)

    dataset_median = df['monthly_rental_price'].median()

    df['shared_occupancy'] = df['shared_occupancy'].map({'Y': 1, 'N': 0})

    cum_sum = df['outcode'].value_counts(normalize=True).cumsum()
    mask = cum_sum < 0.99

    df = df[df['outcode'].isin(cum_sum[mask].index.values)]

    # df = df.append({
    #     'latitude': 51.540285,
    #     'longitude': -0.132809,
    #     'num_bedrooms': 1,
    #     'monthly_rental_price': 350
    # }, ignore_index=True)

    normalize_mask = ['latitude', 'longitude', 'num_bedrooms']

    df_ml = normalize_features(df[normalize_mask].values)

    nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(df_ml)
    distances, indices = nbrs.kneighbors(df_ml)

    df['outlier_score'] = df['monthly_rental_price'].values.reshape(-1, 1) - np.median(
        df['monthly_rental_price'].iloc[indices.reshape(1, -1)[0]].values.reshape(len(df), n_neighbors),
        axis=1
    ).reshape(-1, 1)

    return df, dataset_median


if __name__ == "__main__":
    print(detect_db(n_neighbors=5))
