"""

    The zoopla.py script uses the ZOOPLA API to get rental properties from the
    London districts that are currently being displayed in their website.
    In order to execute it you need to have installed in your machine
    at least Python 3.7 and MongoDB. Make sure to have installed all the
    dependencies available in one of the package files in the root of this
    project. E.g requirements.txt

    You also need to have the follow environment variables properly configured :

    - ZOOPLA_API
        Your Zoopla API key. In order to get it you need to register into ZOOPLA website :
        https://developer.zoopla.co.uk

    - MONGO_HOST
        Your MongoDB host.

    - MONGO_PORT
        Your MongoDB port

    It's also necessary to have a MongoDB collection with the London districts. In order to
    create this collection execute once the script located at :

        src/property_anomaly_detector/datasets/save_ld_district_names.py

    All the instructions necessary to run save_ld_district_names.py are available on itself.

    With all necessary steps done simply execute :

        python zoopla.py

    At the end of the execution a log will be generated in this folder called debug.log.

    It takes several hours to get all the properties since It's respecting the website policy of
    100 requests per hour.

"""
import logging
import os
import sys
from time import sleep
from datetime import datetime

import requests as re

from property_anomaly_detector.database import database as db

API_KEY = os.environ['ZOOPLA_API']

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

# Variables used by the logging
_current_district_idx = None
_current_district_name = None
_current_page_idx = None
_london_districts = None


def iteration_log_message(message: str):
    logging.info(
        f"{_current_district_idx + 1}/{len(_london_districts)} District : {_current_district_name}  | Page {_current_page_idx} | "
        f"{message}"
    )


def main():
    global _current_district_idx, _current_district_name
    global _current_page_idx, _london_districts

    _london_districts = list(db.get_districts())

    if len(_london_districts) == 0:
        logging.error("London districts are not available in MongoDB. Please insert them using the script available at "
                      "src/property_anomaly_detector/datasets/save_ld_district_names.py")
        sys.exit()

    for idx, district in enumerate(_london_districts):
        district = district['district_name']
        logging.info(f"Collecting {district} properties !")

        _current_district_name = district
        _current_district_idx = idx

        _current_page_idx = 0
        while _current_page_idx < 100:

            url = f"http://api.zoopla.co.uk/api/v1/property_listings.json?" \
                  f"area={district},London&listing_status=rent&page_size=100" \
                  f"&page_number={_current_page_idx}&api_key={API_KEY}"

            response = re.get(url)
            logging.info(url)

            iteration_log_message(f"Request code : {response.status_code}!!")

            if response.status_code == 200:

                properties = response.json()['listing']

                if len(properties) == 0:
                    iteration_log_message(f"No more properties available for this district !!")
                    break

                for property in properties:
                    property.update({'announced_at': datetime.strftime(datetime.utcnow(), "%Y-%m-%d")})

                db.insert_properties(properties)
                iteration_log_message(f"properties successfully saved !")
            elif response.status_code == 403:
                iteration_log_message(f" 100 calls reached. Wait for the 1 hour delay ! Trying again in 1 hour...")
                sleep(3600)
                continue
            else:
                iteration_log_message(f"Something went wrong !!")
                break

            sleep(1)
            _current_page_idx += 1

    date = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")
    logging.info("Saving last update date")
    db.insert_last_update_date(date)

    logging.info("Removing old properties")
    db.remove_properties({'announced_at': {'$ne': date}})


if __name__ == "__main__":
    main()
