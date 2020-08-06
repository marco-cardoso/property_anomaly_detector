"""
    To use it you need to have a ZOOPLA API key.
"""
import logging
import os
from time import sleep
from datetime import datetime

import pandas as pd
import requests as re
from property_anomaly_detector.database import Database

db = Database("zoopla")
API_KEY = os.environ['ZOOPLA_API']

LONDON_DISTRICTS = pd.read_csv(
    "../../datasets/london_district_names.csv", usecols=['district_name']
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


def main():
    for idx, district in enumerate(LONDON_DISTRICTS.values):
        logging.info(f"Collecting {district[0]} properties !")

        i = 0
        while i < 100:

            url = f"http://api.zoopla.co.uk/api/v1/property_listings.json?" \
                  f"area={district[0]},London&listing_status=rent&page_size=100&page_number={i}&api_key={API_KEY}"

            response = re.get(url)
            logging.info(
                f"{idx + 1}/{len(LONDON_DISTRICTS.values)} District : {district[0]}  | Page {i} | "
                f"Request code : {response.status_code}!!")

            if response.status_code == 200:

                properties = response.json()['listing']

                if len(properties) == 0:
                    logging.info(
                        f"{idx + 1}/{len(LONDON_DISTRICTS.values)} District : {district[0]}  | Page {i} | "
                        f"No more properties available for this district !!")
                    break

                for property in properties:
                    property.update({'announced_at': datetime.strftime(datetime.now(), "%Y-%m-%d")})

                db.insert_properties(properties)

                logging.info(
                    f"{idx + 1}/{len(LONDON_DISTRICTS.values)} District : {district[0]}  | Page {i} | {len(properties)} "
                    f"properties successfully saved !")
            elif response.status_code == 403:
                logging.info(
                    f"{idx + 1}/{len(LONDON_DISTRICTS.values)} District : {district[0]}  | Page {i} | "
                    f" 100 calls reached. Wait for the 1 hour delay ! Trying again in 1 hour...")
                sleep(3600)
                continue
            else:
                logging.info(
                    f"{idx + 1}/{len(LONDON_DISTRICTS.values)} District : {district[0]}  | Page {i} | "
                    f"Something went wrong !!")
                break

            sleep(1)
            i += 1


if __name__ == "__main__":
    main()
