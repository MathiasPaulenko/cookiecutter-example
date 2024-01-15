# -*- coding: utf-8 -*-
"""
XpathGenerator Class used to generate the xpath of a web element.
"""
import logging

logger = logging.getLogger(__name__)


class XpathGenerator:

    def _get_parent_element(self, elem, xpath):
        """
        Recursive function that builds the xpath of a BeautifulSoup web element
        navigating all the element parents until it finds an element with id
        or the root of the web page.
        :param elem:
        :param xpath:
        :return:
        """
        parent = elem.parent
        if parent is not None:
            siblings = parent.find_all(elem.name, recursive=False)
            parent_id = parent.get("id")

            if len(siblings) - 1 == 0:
                actual_elem = f"/{elem.name}" + xpath
            else:
                actual_elem = f"/{elem.name}[{1 + siblings.index(elem)}]" + xpath

            if parent_id is not None:
                logger.info(f"Found parent with id: {parent_id}")
                xpath = f'//*[@id="{parent.get("id")}"]{actual_elem}'
            else:
                xpath = self._get_parent_element(parent, actual_elem)

        return xpath

    def from_bs_element(self, element):
        """
        Generates the xpath of a BeautifulSoup web element.
        :param element:
        :return:
        """
        element_id = element.get("id")
        xpath = ''
        if element_id:
            xpath = f'//*[@id="{element_id}"]'
        else:
            logger.info("Element does not have an id attribute")
            xpath = self._get_parent_element(element, xpath)
        logger.info(f"Element xpath '{xpath}' created")
        return xpath

    def from_selenium_element(self, element):
        """
        Generates the xpath of a Selenium web element.
        :param element:
        :return:
        """
        xpath = ''
        if element.tag_name == 'a' or element.tag_name == 'button':
            xpath = f"//{element.tag_name}[text()='{element.text}']"
        elif element.tag_name == 'input':
            placeholder = element.get_attribute('placeholder')
            name = element.get_attribute('name')
            xpath = f"//{element.tag_name}[@placeholder='{placeholder}' or @name='{name}']"
        logger.info(f"Element xpath '{xpath}' created")
        return xpath
