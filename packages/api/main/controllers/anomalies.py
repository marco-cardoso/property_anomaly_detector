from flask import request, jsonify
from flask import Blueprint

from property_anomaly_detector.anomaly import detect_anomalies
from property_anomaly_detector.database import database

app = Blueprint('anomalies', __name__)


@app.route('/anomalies', methods=['GET'])
def get_anomalies():
    if request.method == 'GET':
        anomalies = database.get_top_outliers()
        return jsonify(anomalies)


@app.route('/classify-property', methods=['GET'])
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

        property_anomaly_score, highest_neighbor_score = detect_anomalies.classify_property(
            property
        )

        result = {
            'property_anomaly_score': property_anomaly_score,
            'highest_neighbor_score': highest_neighbor_score
        }

        return result
