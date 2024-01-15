# -*- coding: utf-8 -*-
"""
File with functions for the self-healing process.
"""
import os
from sklearn.preprocessing import OneHotEncoder
from sklearn.neighbors import NearestNeighbors
import pandas as pd
from pandas.errors import EmptyDataError
from colorama import Fore
import logging
from arc.settings.settings_manager import Settings

REPOSITORIES_PATH = Settings.REPOSITORIES.get()
RESOURCES_PATH = Settings.USER_RESOURCES_PATH.get()
CURRENT_ELEMENTS = os.path.join(RESOURCES_PATH, 'current_elements.csv')
ELEMENTS_CSV = os.path.join(REPOSITORIES_PATH, 'elements.csv')
PYTALOS_IA = Settings.PYTALOS_IA.get('self-healing')
SHOW_RESULT_CONSOLE = Settings.PYTALOS_IA.get('self-healing').get('show_result_console', False)

logger = logging.getLogger(__name__)


def init_healing(old_locator):
    """
        Function that uses the Nearest Neighbors ML algorithm to find the most similar elements
        to a not found element in a web page.
        :param old_locator:
        :return:
    """
    n_neighbors = PYTALOS_IA.get('n_neighbors', 3)
    algorithm = PYTALOS_IA.get('algorithm', 'ball_tree')
    tolerance = PYTALOS_IA.get('tolerance', 2.00)
    healed_locator = None
    logger.info(f'Element with locator "{old_locator[1]}" not found')
    element = read_successful_element(old_locator)
    page, page_locators = read_current_page()
    if len(element.index) != 0 and len(page.index) != 0 and len(page_locators.index) != 0:
        max_elems = len(page)
        if n_neighbors > max_elems:
            n_neighbors = max_elems
        element = pd.DataFrame(element, columns=page.columns)
        element = element.to_numpy()
        page = page.to_numpy()
        encoded_page, encoded_elem = encode(page, element)
        if encoded_page is not None and encoded_elem is not None:
            healed_locator, similarity = get_healed_locator(old_locator, encoded_page, encoded_elem, n_neighbors, algorithm,
                                                            tolerance, page_locators)
            if healed_locator is not None and similarity is not None:
                logger.info(f'Similar element found with locator: {healed_locator}')
                logger.info(f'Elements similarity: {similarity}')
                show_console(old_locator, healed_locator, similarity)
    else:
        logger.warning(f'Element with locator {old_locator[1]} has never been found before or current page is empty')
    return healed_locator


def read_successful_element(locator):
    """
        Reads the info of the last successful element found from the csv using the old locator
        :param locator:
        :return:
    """
    try:
        element = pd.read_csv(ELEMENTS_CSV, encoding='utf-8-sig')
        element = element.loc[element['loc'] == locator[1]]
        element = element.drop(columns=['loc_by', 'loc', 'md5'])
        logger.info(f'Last successful element read from csv')
    except (FileNotFoundError, EmptyDataError) as exception:
        logger.error(f'Unable to read file:{ELEMENTS_CSV}')
        logger.error(exception)
        element = pd.DataFrame()
    return element


def read_current_page():
    """
        Reads the info of the scraped web page rom the csv
        :return:
    """
    try:
        page = pd.read_csv(CURRENT_ELEMENTS, encoding='utf-8-sig')
        page_locators = page['loc']
        page = page.drop(columns=['loc_by', 'loc', 'md5'])
        logger.info(f'Page elements read from csv')
    except (FileNotFoundError, EmptyDataError) as exception:
        logger.error(f'Unable to read file:{CURRENT_ELEMENTS}')
        logger.error(exception)
        page = pd.DataFrame()
        page_locators = pd.DataFrame()
    return page, page_locators


def encode(page, element):
    """
        Converts all web elements from a list of strings to a list of binary integers
        :param page:
        :param element:
        :return:
    """
    encoded_elem = None
    encoded_page = None
    try:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoded_page = encoder.fit_transform(page)
        logger.info(f'Page encoded')
        encoded_elem = encoder.transform(element)
        logger.info(f'Element encoded')
    except Exception as exception:
        logger.error(f'Unable to encode web elements')
        logger.error(exception)
    return encoded_page, encoded_elem


def get_healed_locator(old_locator, encoded_page, encoded_elem, n_neighbors, algorithm, tolerance, page_locators):
    """
        Uses the NearestNeigbors algorithm from the sklearn library to compare and find the most similar
        web element to the las successful element in the current page
        :param old_locator:
        :param encoded_page:
        :param encoded_elem:
        :param n_neighbors:
        :param algorithm:
        :param tolerance:
        :param page_locators:
        :return:
    """
    healed_locator = None
    first_elem_similarity = None
    try:
        neighbors = NearestNeighbors(n_neighbors=n_neighbors, algorithm=algorithm).fit(encoded_page)
        distances, indexes = neighbors.kneighbors(encoded_elem)
        logger.info(f'Similar elements indexes: {indexes}')
        logger.info(f'Similar elements distances: {distances}')
        first_elem_similarity = distances[0].tolist()[0]
        healed_locator = tuple((old_locator[0], page_locators.iloc[indexes.tolist()[0][0]]))
        if tolerance and first_elem_similarity > tolerance:
            return None, first_elem_similarity
    except Exception as exception:
        logger.error("Unable to execute the NearestNeighbors algorithm")
        logger.error(exception)
    return healed_locator, first_elem_similarity


def show_console(old_locator, healed_locator, similarity):
    """
        If activated in the settings prints the result of the self-healing in the console
        :param old_locator:
        :param healed_locator:
        :param similarity:
        :return:
    """
    if SHOW_RESULT_CONSOLE:
        print(Fore.LIGHTBLUE_EX + f'\n\tElement with locator "{old_locator}" not found')
        print(Fore.LIGHTBLUE_EX + f'\tSimilar element found with locator: {healed_locator}')
        print(Fore.LIGHTBLUE_EX + f'\tElements similarity: {round(similarity, 2)}\n')
