# -*- coding: utf-8 -*-
"""
Link Page Element class file
"""
import logging

from arc.core.test_method.exceptions import TalosTestError
from arc.page_elements.button_page_element import Button

logger = logging.getLogger(__name__)

class Link(Button):
    """
    Link Page Element class, a subclass of Button.
    """

    @property
    def href(self):
        """
        Return url from href attribute value.
        :return:
        """
        try:
            return self.web_element.get_attribute("href")
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))
