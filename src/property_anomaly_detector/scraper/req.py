import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from property_anomaly_detector.database import Database
from property_anomaly_detector.utils import *

import traceback

database = Database()


def sleep(function):
    def wrapper(*args, **kwargs):

        result = None

        while True:
            try:
                result = function(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                print("Out of connection - Trying again ...")
                time.sleep(1)
                continue
            except Exception :
                print(traceback.format_exc())
                # There's nothing to do in this specific case
                # Proceed ...
                break
            else:
                time.sleep(0.5)
                break

        return result

    return wrapper


class Requests():

    def __init__(self):
        super().__init__()
        self.main_url = "https://www.rightmove.co.uk"
        self.dst_code_url = "https://www.rightmove.co.uk/typeAhead/uknostreet/"

    @sleep
    def get_district_code(self, district: str):

        district = district.upper().replace(" ", "")
        splitted = [district[i:i + 2] + "/" for i in range(0, len(district), 2)]
        final_url = self.dst_code_url + str().join(splitted)

        response = requests.get(final_url).json()['typeAheadLocations']

        location_identifier = next(filter(
            lambda dictionary:
            dictionary['normalisedSearchTerm'].endswith("BOROUGH")
            or
            dictionary['normalisedSearchTerm'].endswith("CITY OF"),
            response
        ))

        # Removing the string REGION^ from the text
        location_identifier['locationIdentifier'] = location_identifier['locationIdentifier'].split("^")[1]
        print(location_identifier)
        database.insert_district(location_identifier)

    @sleep
    def get_property_information(self, district: str, path: str):
        url = self.main_url + path

        # This try-exception is necessary since some observations presented
        # a few errors. 7/27411
        try:

            response = requests.get(url)

            soup = BeautifulSoup(response.text, features="html.parser")

            ##### Attributes ####

            # Header attributes
            property_rent_and_price_div = soup.find("div", {"class": "property-header-bedroom-and-price"})

            title = clean_string(property_rent_and_price_div.findChildren("h1")[0].text)

            address = clean_string(property_rent_and_price_div.findChildren("address")[0].text)
            price = clean_string(soup.find("p", {"id": "propertyHeaderPrice"}).findChildren("strong")[0].text)

            # Letting section attributes / Optional attributes
            letting_div = soup.find("div", {"id": "lettingInformation"})
            letting_table_rows = letting_div.find_next("tbody").find_all_next("tr")

            letting_info = {get_html_value(row, 0): get_html_value(row, 1) for row in letting_table_rows}

            # Agent content attributes
            agent_content_div = soup.find("div", {"class": "agent-content"})

            key_features_list = agent_content_div.findChildren("ul")

            if len(key_features_list) > 0:
                key_features = [key_feature.text for key_feature in key_features_list[0].findChildren("li")]
            else:
                key_features = []

            description = agent_content_div.find_next("p", {"itemprop": "description"}).text

            # Coordinates
            location_image_url = soup.find("a", {"class": "js-ga-minimap"}).findChildren("img")[0].attrs['src']
            latitude = re.findall("latitude=([-0-9_\.]+)\w+", location_image_url)[0]
            longitude = re.findall("longitude=([-0-9_\.]+)\w+", location_image_url)[0]

            stations = []
            stations_li = soup.find("ul", {"class": "stations-list"})

            if stations_li is not None:
                stations_li = stations_li.findChildren("li")
                stations = [
                    {
                        'name': clean_string(station_li.findChildren("span")[0].text),
                        'distance': convert_station_distance(station_li.findChildren("small")[0].text)
                    }
                    for station_li in stations_li
                ]

            document = {
                'url': url,
                'title': title,
                'address': address,
                'price': price,
                'letting': letting_info,
                'key_features': key_features,
                'description': description,
                'latitude': latitude,
                'longitude': longitude,
                'stations': stations,
                "amt_stations": len(stations),
                'district': district
            }

            database.insert_property(document)
        except Exception as e:
            database.save_error(url)
            print("Saving the error")
            raise e

    @sleep
    def get_properties(self, district_nb, index):
        url = "https://www.rightmove.co.uk/property-to-rent/find.html?" \
              f"locationIdentifier=OUTCODE%5E{district_nb}&" \
              f"index={index}&" \
              "propertyTypes=&" \
              "includeLetAgreed=true&" \
              "mustHave=&" \
              "dontShow=&" \
              "furnishTypes=&" \
              "keywords="

        response = requests.get(url)
        return BeautifulSoup(response.text, features="html.parser")
