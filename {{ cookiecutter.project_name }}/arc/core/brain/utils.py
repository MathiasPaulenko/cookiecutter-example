# -*- coding: utf-8 -*-
"""
Utils used for saving web elements info in a csv in the self-healing process.
"""
import csv
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def generate_current_elements_csv_headers(csv_path, data_field):
    """
    Generates the headers of the csv using the keys in data_field.
    """
    try:
        with open(csv_path, 'w', newline='') as f:
            w = csv.DictWriter(f, data_field.keys())
            w.writeheader()
            logger.info("CSV headers created")
    except(Exception,):
        logger.error("Unable to create CSV headers")


def insert_element_data(data, csv_path):
    """
    Inserts the data of a web element into a csv.
    :param data:
    :param csv_path:
    :return:
    """
    try:
        file_data = pd.read_csv(csv_path)
        logger.info(f"Read CSV at '{csv_path}'")
    except(Exception,):
        file_data = pd.DataFrame()
        logger.info(f"Creating CSV with path '{csv_path}'")
    atts = [data]
    df_data = pd.DataFrame(atts)
    union_data = pd.concat([file_data, df_data], axis=0, ignore_index=True)
    union_data = union_data.drop_duplicates(subset=union_data.columns.difference(['url', 'rect']))
    union_data.to_csv(csv_path, index=False)
    logger.info("Web element data inserted in csv")
