# -*- coding: utf-8 -*-
"""
Layer Page Element class file.
"""
import logging

from selenium.common.exceptions import StaleElementReferenceException

from arc.core.test_method.exceptions import TalosTestError
from arc.page_elements.page_element import PageElement

logger = logging.getLogger(__name__)


class Layer(PageElement):
    """
    Layer Page Element class, a subclass of PageElement.
    A Layer refers to HTML elements such as div, section, footer, and other elements that nest other elements.
    """

    @property
    def text(self):
        """
        Return text from layer page element.
        :return:
        """
        try:
            return self.web_element.text
        except StaleElementReferenceException:
            # Retry if element has changed
            return self.web_element.text
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    @property
    def id(self):
        """
        Return id from attribute of layer page element.
        :return:
        """
        try:
            return self.web_element.get_attribute("id")
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    @property
    def css_class(self):
        """
        Return class from attribute of layer page element.
        :return:
        """
        try:
            return self.web_element.get_attribute("class")
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))
