import os
import pathlib

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent.parent


class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '}@$12310adm/=(+@d%#1`9~8/5'
    SERVER_PORT = 5001


class ProductionConfig(Config):
    DEBUG = False
    SERVER_ADDRESS = os.environ.get('SERVER_ADDRESS', '0.0.0.0')
    SERVER_PORT = os.environ.get('SERVER_PORT', '5001')


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
