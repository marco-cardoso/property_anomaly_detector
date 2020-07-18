import os

from pymongo import MongoClient


class Database:

    def __init__(self, database_name: str) -> None:
        """
        Database constructor
        :param database_name: A string with the database_name
        """
        self.client = MongoClient(os.environ.get('MONGO_HOST'), int( os.environ.get('MONGO_PORT')))

        database = self.client[database_name]

        self.properties = database['properties']
        self.links = database['links']
        self.districts = database['districts']
        self.errors = database["errors"]

    def get_properties(self, default_projection={}):
        return list(self.properties.find({}, default_projection))

    def insert_properties(self, properties: list):
        """
        List of dictionaries representing the properties
        :param properties: List of dictionaries representing the properties
        """
        self.properties.insert_many(properties)
