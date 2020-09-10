"""
    This module downloads all UK postcodes using the Wikipedia page
    https://en.wikipedia.org/wiki/List_of_postcode_areas_in_the_United_Kingdom

    In order to execute it, install all of the dependencies available in the
    requirements.txt file and in a terminal execute :

    python get_uk_postcodes.py

"""

from os import path

import pandas as pd


def download_postcodes():
    """
    It downloads the UK postcodes and stores them
    in the folder datasets/uk_postcodes
    """

    postcode_areas = download_postcode_areas()

    postcode_areas = postcode_areas.iloc[:, 0]
    postcode_areas.apply(download_postcode_districts)


def download_postcode_areas() -> pd.DataFrame:
    """
   The postcode area is the largest geographical unit used and forms the initial
   characters of the alphanumeric UK postcode.

   There are currently 121 geographic postcode areas in use in the UK and a further
   3 often combined with these covering the Crown Dependencies of Guernsey, Jersey and Isle of Man.

   This method downloads all UK postcode areas and saves them in a single CSV file
   called postcodes.csv located at datasets/uk_postcodes

   :returns: A Pandas dataframe with all UK postcode areas
   """

    uk_cities_postcodes = "https://en.wikipedia.org/wiki/List_of_postcode_areas_in_the_United_Kingdom"

    postcodes_tables = pd.read_html(uk_cities_postcodes)
    postcode_table = postcodes_tables[0]

    print("Saving the postcodes....")
    output_path = path.join("..", "datasets", "uk_postcodes", f"postcodes.csv")
    postcode_table.to_csv(output_path)
    print("Saving the postcodes....DONE")
    return postcode_table


def download_postcode_districts(postcode_area: str):
    """
    Each postcode area is further divided into post towns and postcode districts.
    There are on average 20 postcode districts to a postcode area.
    The London post town is instead divided into several postcode areas.

    This method downloads all postcode districts for a postcode area and creates
    a CSV file with them located at datasets/uk_postcodes/{postcode_area}.csv

    :param postcode_area: A String with the postcode_area. The postcode area
    is the initial characters of the alphanumeric UK postcode.

    AB for example is the postcode area of Aberdeen

    """
    uk_postcode_districts = f"https://en.wikipedia.org/wiki/{postcode_area}_postcode_area"
    postcode_districts = pd.read_html(uk_postcode_districts)[1]

    print(f"Saving {postcode_area} district codes...")
    output_path = path.join("..", "datasets", "uk_postcodes", f"{postcode_area}.csv")
    postcode_districts.to_csv(output_path)
    print(f"Saving {postcode_area} district codes...DONE")


if __name__ == "__main__":
    download_postcodes()
