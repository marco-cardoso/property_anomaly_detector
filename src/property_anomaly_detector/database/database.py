import os

from pymongo import MongoClient


class Database:

    def __init__(self, database_name: str) -> None:
        """
        Database constructor
        :param database_name: A string with the database_name
        """
        self.client = MongoClient(os.environ.get('MONGO_HOST'), int(os.environ.get('MONGO_PORT')))

        database = self.client[database_name]

        self.properties = database['properties']
        self.districts = database['districts']
        self.specs = database['specs']

    def get_properties(self, default_filter={}, projection={}):
        return list(self.properties.find(default_filter, projection))

    def remove_properties(self, condition: dict):
        self.properties.remove(condition)

    def insert_properties(self, properties: list):
        """
        List of dictionaries representing the properties
        :param properties: List of dictionaries representing the properties
        """
        self.properties.insert_many(properties)

    def insert_last_update_date(self, date):
        self.specs.remove({})
        self.specs.insert({'last_update_date': date})

    def insert_districts(self, districts: list):
        self.districts.insert_many([{'district_name': district} for district in districts])

    def get_unique_elements(self, field: str) -> list:
        """
        It gets the unique values from a specific field
        :param field: String with the field
        :return: A list with the strings of the unique values
        """
        return self.properties.distinct(field)
