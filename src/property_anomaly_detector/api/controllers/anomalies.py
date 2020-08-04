from flask import request
from property_anomaly_detector.ml import detect_anomalies
from property_anomaly_detector.api.controllers.properties import generate_filter_dict


def get_anomalies():
    ppts_limits = 50
    if request.method == 'GET':
        filters = generate_filter_dict(request.args)
        anomalies, df_median = detect_anomalies.detect_db(filters)

        anomalies.drop('_id', axis=1, inplace=True)
        anomalies.sort_values(by='outlier_score', ascending=False, inplace=True)

        response = {
            'anomalies': anomalies[:ppts_limits].to_dict(orient="records"),
            'data_median': df_median,
        }
        return response


def classify_anomaly():
    if request.method == 'GET':
        anomaly = {
            'property_type': request.args['property_type'],
            'furnished_state': request.args['furnished_state'],
            'shared_occupancy': request.args['shared_occupancy'],
            'latitude': request.args['latitude'],
            'longitude': request.args['longitude'],
            'num_bedrooms': request.args['num_bedrooms'],
            'num_bathrooms': request.args['num_bathrooms'],
            'num_recepts': request.args['num_recepts'],
            'monthly_rental_price': request.args['monthly_rental_price']
        }

        filters = {
            'property_type': anomaly['property_type'],
            'rental_prices.shared_occupancy': anomaly['shared_occupancy']
        }

        # filters = generate_filter_dict(request.args)
        anomalies, df_median = detect_anomalies.detect_db(filters, anomaly_data=anomaly)
        anomaly_score = anomalies.iloc[0]['outlier_score'] * -1
        # anomalies.drop('_id', axis=1, inplace=True)
        # anomalies.sort_values(by='outlier_score', ascending=False, inplace=True)

        # response = {
        #     'anomalies' : anomalies[:ppts_limits].to_dict(orient="records"),
        #     'data_median' : df_median,
        # }

        return {'property_anomaly_score': anomaly_score,
                'highest_df_score': anomalies.sort_values(by='outlier_score', ascending=False).iloc[0]['outlier_score']}
