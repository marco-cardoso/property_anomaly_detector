import ast

from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin

from property_anomaly_detector.database import Database
from property_anomaly_detector.ml import detect_anomalies

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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
@cross_origin()
def get_properties():
    if request.method == 'GET':
        filters = generate_filter_dict(request.args)
        properties = db.get_properties(default_filter=filters, default_projection=default_projection)
        return jsonify(properties)


@app.route("/anomalies", methods=['GET'])
@cross_origin()
def get_anomalies():
    ppts_limits = 50
    if request.method == 'GET':
        filters = generate_filter_dict(request.args)
        anomalies, df_median = detect_anomalies.detect_db(filters)

        anomalies.drop('_id', axis=1, inplace=True)
        anomalies.sort_values(by='outlier_score', ascending=False, inplace=True)
        
        response = {
            'anomalies' : anomalies[:ppts_limits].to_dict(orient="records"),
            'data_median' : df_median,
        }


        return response


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=True
    )
