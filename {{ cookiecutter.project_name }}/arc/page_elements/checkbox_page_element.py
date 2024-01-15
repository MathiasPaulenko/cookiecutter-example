# -*- coding: utf-8 -*-
"""
Checkbox Page Element class file
"""
import logging

from arc.core.test_method.exceptions import TalosTestError
from arc.page_elements.button_page_element import Button

logger = logging.getLogger(__name__)


class Checkbox(Button):
    """
    Checkbox Page Element class, a subclass of Button.
    """

    @property
    def text(self):
        """
        Return text from attribute value from checkbox page element.
        :return:
        """
        try:
            return self.web_element.get_attribute("value")
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    def is_selected(self):
        """
        Return true if checkbox is selected.
        :return:
        """
        try:
            return self.web_element.is_selected()
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    def check(self):
        """
        Check or click on checkbox option if checkbox is already check, this function does nothing.
        :return:
        """
        try:
            if not self.is_selected():
                self.web_element.click()
            return self
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    def uncheck(self):
        """
        Uncheck o click on checkbox option, if checkbox is already uncheck, this function does nothing.
        :return:
        """
        try:
            if self.is_selected():
                self.web_element.click()
            return self
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))
