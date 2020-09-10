from os import environ

from flask import Flask
from flask_cors import CORS
from property_anomaly_detector.api.controllers import anomalies, properties

app = Flask(__name__)

if environ.get("CORS"):
    CORS(app)

app.add_url_rule('/classify-property', 'classify-property', anomalies.classify_anomaly, methods=['GET'])
app.add_url_rule('/anomalies', 'anomalies', anomalies.get_anomalies, methods=['GET'])

app.add_url_rule("/properties", "properties", properties.get_properties, methods=['GET'])
app.add_url_rule("/get-categorical-filters", "filters", properties.get_categorical_filters, methods=['GET'])

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=True
    )
