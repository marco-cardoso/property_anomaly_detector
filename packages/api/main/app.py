from os import environ

from flask import Flask
from flask_cors import CORS
from main.controllers import anomalies, properties

app = Flask(__name__)


def get_app(config) -> Flask:
    flask_app = Flask(__name__)
    flask_app.config.from_object(config)

    flask_app.register_blueprint(anomalies.app)
    flask_app.register_blueprint(properties.app)

    if environ.get("CORS"):
        CORS(flask_app, origins=['localhost:3000'])
        flask_app.config['CORS_HEADERS'] = 'Content-Type'

    return flask_app


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        debug=True
    )
