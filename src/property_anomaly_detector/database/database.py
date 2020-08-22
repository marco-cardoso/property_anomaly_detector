import datetime
import os

import pandas as pd
from pymongo import MongoClient, CursorType, DESCENDING


class Database:
    """
        This class is a MongoClient wrapper to easily perform operations related to the properties

        It manages the follow collections :

        -   Properties
            Responsible to store the properties obtained from the zoopla api

        -   Districts
            Responsible to store the London district names

        -   Specs
            Responsible to store parameters used by any module in this project

        -   Anomalies
            Responsible to store the top 100 anomaly properties

    """

    def __init__(self, database_name: str) -> None:
        """
        :param database_name: A string with the database_name
        """
        self.client = MongoClient(os.environ.get('MONGO_HOST'), int(os.environ.get('MONGO_PORT')))

        database = self.client[database_name]

        self.properties = database['properties']
        self.districts = database['districts']
        self.specs = database['specs']
        self.anomalies = database['anomalies']

    def get_properties(self, default_filter=None, projection=None) -> list:
        """

        Return the properties from the database matching the given filter and
        projection.

        :param default_filter: A dictionary with the filter. If none is passed
        no filter will be used.
        :param projection: A dictionary with the projection. If none is passed
        all of the variables will be returned.
        :return: A list with the properties matching the given filter and projection
        """

        if projection is None:
            projection = {}
        if default_filter is None:
            default_filter = {}

        last_update_date = self.get_specs()['last_update_date']
        default_filter.update({'announced_at': last_update_date})

        return list(self.properties.find(default_filter, projection))

    def remove_properties(self, default_filter: dict) -> None:
        """

        Remove the properties from the database matching the given filter
        dictionary

        :param default_filter: A dictionary with the conditions to filter the properties
        """
        self.properties.remove(default_filter)

    def insert_properties(self, properties: list) -> None:
        """

        Insert a list of properties in the database

        :param properties: List of dictionaries representing the properties
        """
        self.properties.insert_many(properties)

    def insert_last_update_date(self, date: datetime.datetime) -> None:
        """

        Insert in the database the date when the data was last updated

        :param date: A datetime object with the date to be inserted in the database
        """

        self.specs.remove({})
        self.specs.insert({'last_update_date': date})

    def get_specs(self) -> dict:
        """

        Get the system specifications stored in Mongo

        :return: A dictionary with the system specifications
        """
        return self.specs.find({})[0]

    def insert_districts(self, districts: list) -> None:
        """

        Insert a list of districts in the database

        :param districts: A list with the district names
        """

        self.districts.insert_many([{'district_name': district} for district in districts])

    def get_districts(self) -> CursorType:
        """

        Return a cursor with all london districts in the database

        :return: A cursor with all london districts
        """
        return self.districts.find({})

    def get_unique_elements(self, field: str) -> list:
        """

        Get the unique values from a specific field

        :param field: String with the field
        :return: A list with the strings of the unique values
        """
        return self.properties.distinct(field)

    def save_top_outliers(self, df: pd.DataFrame):
        """
        Save the given dataframe with the anomaly properties
         in a Mongo collection called anomalies

        :param df: A pandas dataframe with the results
        """
        self.anomalies.remove({})
        self.anomalies.insert_many(df.to_dict(orient="records"))

    def get_top_outliers(self) -> list:
        """
        :return: A list with the anomalies stored in the 'anomalies' collection sorted by outlier_score
        """
        return list(self.anomalies.find({}, {'_id': False}).sort([("outlier_score", DESCENDING)]))


db = Database("zoopla")
