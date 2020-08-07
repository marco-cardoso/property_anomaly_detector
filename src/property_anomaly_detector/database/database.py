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

    def get_properties(self, default_filter=None, projection=None):
        if projection is None:
            projection = {}
        if default_filter is None:
            default_filter = {}

        last_update_date = self.get_specs()['last_update_date']
        default_filter.update({'announced_at': last_update_date})

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

    def get_specs(self):
        return self.specs.find({})[0]

    def insert_districts(self, districts: list):
        self.districts.insert_many([{'district_name': district} for district in districts])

    def get_districts(self):
        return self.districts.find({})

    def get_unique_elements(self, field: str) -> list:
        """
        It gets the unique values from a specific field
        :param field: String with the field
        :return: A list with the strings of the unique values
        """
        return self.properties.distinct(field)
