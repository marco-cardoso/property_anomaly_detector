"""
    This module reads the london_district_names.csv file and
    stores it into a MongoDB collection
"""
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
    file = pd.read_csv(
        "london_district_names.csv"
    )

    logging.info("Inserting districts into MongoDB collection")
    london_districts = list(file['district_name'].values)
    db.insert_districts(london_districts)
    logging.info("Finished")


if __name__ == "__main__":
    main()
