from property_anomaly_detector.features import read_df, feature_engineer, geospatial


def get_df():
    df = read_df()
    df = feature_engineer.flatten_rental_prices(df)
    df = feature_engineer.convert_numerical_cols(df)

    df.rename(columns={
        'rental_prices': 'monthly_rental_price',
        'outcode': 'district'
    }, inplace=True)

    df = geospatial.get_districts(df)

    return df
