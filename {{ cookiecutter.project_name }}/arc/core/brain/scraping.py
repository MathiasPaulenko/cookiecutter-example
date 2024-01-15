# -*- coding: utf-8 -*-
"""
Scraper class used for scraping web elements and web pages.
"""
import logging

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.timeouts import Timeouts
from arc.settings.settings_manager import Settings
from copy import deepcopy
import os
from arc.contrib.tools.crypto.crypto import generate_md5
from arc.core.brain import utils

REPOSITORIES_PATH = Settings.REPOSITORIES.get()
RESOURCES_PATH = Settings.USER_RESOURCES_PATH.get()
CURRENT_ELEMENTS = os.path.join(RESOURCES_PATH, 'current_elements.csv')
ELEMENTS_CSV = os.path.join(REPOSITORIES_PATH, 'elements.csv')
GET_ELEMENT_RECT = Settings.PYTALOS_IA.get('self-healing').get('elem_rect', False)

logger = logging.getLogger(__name__)

tags = [
    'a',
    'div',
    'span',
    'button',
    'input',
    'select',
    'pre',
    'textarea',
    'svg',
    'img',
    'p',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
]
TAGS = Settings.PYTALOS_IA.get('self-healing', {}).get('tags', tags)

DATA_FIELD = {
    'loc_by': None,
    'loc': None,
    'tag': None,
    'text': None,
    'class': None,
    'id': None,
    'placeholder': None,
    'type': None,
    'name': None,
    'value': None,
    'alt': None,
    'form': None,
    'hidden': None,
    'href': None,
    'label': None,
    'role': None,
    'required': None,
    'selected': None,
    'src': None,
    'style': None,
    'target': None,
    'md5': None,
    'url': None
}


class Scraper:

    def __init__(self, driver):
        self.driver = driver

    def get_elements_from_page_source(self):
        """
        Extracts all elements from the page_source using BeautifulSoup.
        :return:
        """
        elements = []
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            elements = soup.find_all(TAGS)
            logger.info("Web elements scraped from page source")
        except(Exception,):
            logger.warning("Unable to get elements from page source")
        return elements

    def get_elements_from_find_elements(self):
        """
        Extract all web elements using the Selenium web driver.
        :return:
        """
        timeout = Timeouts()
        timeout.implicit_wait = 1
        self.driver.timeouts = timeout

        elements_found = []
        for tag in TAGS:
            try:
                elements_found += self.driver.find_elements(By.TAG_NAME, tag)
                logger.info("Web elements scraped using Selenium Web Driver")
            except(Exception,):
                logger.warning("Unable to get elements using Selenium Web Driver")

        return elements_found

    def scraping_current_page_elements(self):
        """
        Gets all the data from the elements of the current web page.
        :return:
        """
        from arc.core.brain.generator import XpathGenerator

        utils.generate_current_elements_csv_headers(CURRENT_ELEMENTS, DATA_FIELD)

        xpath_generator = XpathGenerator()
        elements = self.get_elements_from_page_source()

        try:
            for element in elements:
                data = deepcopy(DATA_FIELD)
                data['loc'] = xpath_generator.from_bs_element(element)
                data['tag'] = element.name
                data['text'] = element.text

                for att in element.attrs.keys():
                    if att == 'class':
                        data[att] = ' '.join(element.attrs.get(att))
                    else:
                        data[att] = element.attrs.get(att, None)

                data['url'] = self.driver.current_url
                data['md5'] = None
                if GET_ELEMENT_RECT:
                    timeout = Timeouts()
                    timeout.implicit_wait = 1
                    self.driver.timeouts = timeout
                    element = self.driver.find_element(By.XPATH, data['loc'])
                    data['rect'] = str(element.rect)
                utils.insert_element_data(data, CURRENT_ELEMENTS)
            logger.info("Current web elements info scraped")
        except(Exception,):
            logger.warning("Unable to get current web element info")

    def save_web_element_scraping(self, web_element, locator):
        """
        Gets all the data of a Selenium web element.
        :param web_element:
        :param locator:
        :return:
        """
        try:
            data = deepcopy(DATA_FIELD)
            data['loc_by'] = locator[0]
            data['loc'] = locator[1]
            data['tag'] = web_element.tag_name
            data['text'] = web_element.text

            current_att = self.driver.execute_script(
                'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) '
                '{ items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; '
                'return items;',
                web_element
            )
            data.update(current_att)
            md5 = generate_md5(data)
            data['url'] = self.driver.current_url

            data['md5'] = md5
            if GET_ELEMENT_RECT:
                data['rect'] = str(web_element.rect)
            utils.insert_element_data(data, ELEMENTS_CSV)
            logger.info(f"Web element with locator '{locator}' scraped")
        except (Exception,):
            logger.warning(f"Unable to get web element with locator {locator} info")


