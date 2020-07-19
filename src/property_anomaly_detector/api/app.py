import ast

from flask import Flask, request, jsonify, Response
from property_anomaly_detector.database import Database
from property_anomaly_detector.ml import detect_anomalies

app = Flask(__name__)
db = Database("zoopla")

default_projection = {
    '_id': False,
    'rental_prices.shared_occupancy': 1,
    'num_floors': 1,
    'num_bedrooms': 1,
    'num_bathrooms': 1,
    'furnished_state': 1,
    'category': 1,
    'property_type': 1,
    'num_recepts': 1,
    'latitude': 1,
    'longitude': 1,
    'rental_prices.per_month': 1,
    'outcode': 1,
    'details_url': 1

}


def generate_filter_dict(args):
    filters = {}

    if 'shared_occupancy' in args:
        filters['rental_prices.shared_occupancy'] = {'$in': ast.literal_eval(args['shared_occupancy'])}

    categorical_variables = ['furnished_state', 'property_type']
    for variable in categorical_variables:
        if variable in args:
            filters[variable] = {'$in': ast.literal_eval(args[variable])}

    numerical_variables = ['num_bedrooms', 'num_bathrooms', 'num_recepts', 'num_floors']
    for variable in numerical_variables:
        if variable + '_min' in args and variable + '_max' in args:
            filters[variable] = {'$gte': args[variable + '_min'], '$lte': args[variable + '_max']}

    return filters


@app.route("/properties", methods=['GET'])
def get_properties():
    if request.method == 'GET':
        filters = generate_filter_dict(request.args)
        properties = db.get_properties(default_filter=filters, default_projection=default_projection)
        return jsonify(properties)


@app.route("/anomalies", methods=['GET'])
def get_anomalies():
    if request.method == 'GET':
        filters = generate_filter_dict(request.args)
        anomalies = detect_anomalies.detect_db(filters).drop('_id', axis=1)
        anomalies.sort_values(by='outlier_score', inplace=True)
        return Response(anomalies.to_json(orient="records"), mimetype='application/json')


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=True
    )
