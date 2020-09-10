import ast

from flask import Blueprint
from flask import request

from property_anomaly_detector.database import database as db

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

app = Blueprint('properties', __name__)


def generate_filter_dict(args):
    filters = {}

    if 'shared_occupancy' in args:
        values = ast.literal_eval(args['shared_occupancy'])

        if "" in values:
            values.remove("")

        filters['rental_prices.shared_occupancy'] = {'$in': values}

    categorical_variables = ['furnished_state', 'property_type']
    for variable in categorical_variables:

        if variable in args:
            values = ast.literal_eval(args[variable])
            if "" in values:
                values.remove("")

            filters[variable] = {'$in': values}

    numerical_variables = ['num_bedrooms', 'num_bathrooms', 'num_recepts', 'num_floors']
    for variable in numerical_variables:
        if variable + '_min' in args and variable + '_max' in args:
            filters[variable] = {'$gte': args[variable + '_min'], '$lte': args[variable + '_max']}

    return filters


@app.route('/get-categorical-filters', methods=['GET'])
def get_categorical_filters():
    if request.method == 'GET':
        result = {'property_type': list(db.get_unique_elements("property_type"))}
        empty_string_idx = result['property_type'].index('')
        result['property_type'][empty_string_idx] = "not_specified"

        result['furnished_state'] = list(db.get_unique_elements("furnished_state"))
        empty_string_idx = result['furnished_state'].index(None)
        result['furnished_state'][empty_string_idx] = "not_specified"

        result['shared_occupancy'] = list(db.get_unique_elements("rental_prices.shared_occupancy"))
        return result
