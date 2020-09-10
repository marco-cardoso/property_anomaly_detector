import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def flatten_rental_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    It flattens the dictionary stored in the rental_prices column of the dataframe
    :param df: A pandas dataframe
    :return: The pandas dataframe with the right attributes
    """
    features_to_cnvt = ['per_month', 'shared_occupancy']
    new_feature_names = ['monthly_rental_price', 'shared_occupancy']

    for original_name, new_name in zip(features_to_cnvt, new_feature_names):

        try:
            df[new_name] = df['rental_prices'].apply(lambda x: x[original_name])
        except KeyError:
            pass

    del df['rental_prices']
    return df


def convert_numerical_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    It converts all numerical columns in the dataframe to float
    :param df: A pandas dataframe
    :return: The pandas dataframe with the converted columns
    """
    numerical_columns = [
        'monthly_rental_price',
        'num_floors',
        'num_bedrooms',
        'num_bathrooms',
        'num_recepts',
        'latitude',
        'longitude'
    ]

    for col in numerical_columns:
        if col in df:
            df[col] = df[col].astype(float)
    return df


def normalize_features(df: pd.DataFrame):
    """
    It normalizes the features of a dataset using MinMaxScaler
    :param df: A pandas dataframe
    :return: The pandas dataframe with normalized features
    """
    mm = MinMaxScaler()
    return mm.fit_transform(df)
