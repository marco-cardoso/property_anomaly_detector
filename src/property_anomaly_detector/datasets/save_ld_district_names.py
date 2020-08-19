"""
    In order to execute it you need to have installed in your machine
    at least Python 3.7 and MongoDB. Make sure to have installed all the
    dependencies available in one of the package files in the root of this
    project. E.g requirements.txt

    You also need to have the follow environment variables properly configured :

    - MONGO_HOST
        Your MongoDB host.

    - MONGO_PORT
        Your MongoDB port

    With all necessary steps done simply execute :

        python save_ld_district_names.py
"""
import os
import logging

import pandas as pd
from property_anomaly_detector.database import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


def main():
    db = Database("zoopla")

    script_path = os.path.dirname(__file__)
    csv_path = os.path.join(script_path, "london_district_names.csv")
    file = pd.read_csv(csv_path)

    logging.info("Inserting districts into MongoDB collection")
    london_districts = list(file['district_name'].values)
    db.insert_districts(london_districts)
    logging.info("Finished")


if __name__ == "__main__":
    main()
