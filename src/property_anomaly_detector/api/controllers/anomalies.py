from flask import request
from property_anomaly_detector.ml import detect_anomalies
from property_anomaly_detector.api.controllers.properties import generate_filter_dict


def get_anomalies():
    ppts_limits = 50
    if request.method == 'GET':
        filters = generate_filter_dict(request.args)
        anomalies = detect_anomalies.detect_db(filters)
        dataset_median = anomalies['monthly_rental_price'].median()

        anomalies.drop('_id', axis=1, inplace=True)
        anomalies.sort_values(by='outlier_score', ascending=False, inplace=True)

        response = {
            'anomalies': anomalies[:ppts_limits].to_dict(orient="records"),
            'data_median': dataset_median,
        }
        return response


def classify_anomaly():
    if request.method == 'GET':
        property = {
            'property_type': request.args['property_type'],
            'furnished_state': request.args['furnished_state'],
            'shared_occupancy': request.args['shared_occupancy'],
            'latitude': float(request.args['latitude']),
            'longitude': float(request.args['longitude']),
            'num_bedrooms': int(request.args['num_bedrooms']),
            'num_bathrooms': int(request.args['num_bathrooms']),
            'num_recepts': int(request.args['num_recepts']),
            'monthly_rental_price': float(request.args['monthly_rental_price'])
        }

        filters = {
            'property_type': property['property_type'],
            'rental_prices.shared_occupancy': property['shared_occupancy']
        }

        property_anomaly_score, highest_neighbor_score = detect_anomalies.classify_property(
            property,
            filters
        )

        result = {
            'property_anomaly_score': property_anomaly_score,
            'highest_neighbor_score' : highest_neighbor_score
        }

        return result

