# -*- coding: utf-8 -*-
"""
Select Page Element class file
"""
import logging

from selenium.webdriver.support.ui import Select as SeleniumSelect

from arc.core.test_method.exceptions import TalosTestError
from arc.page_elements import PageElement

logger = logging.getLogger(__name__)


class Select(PageElement):
    """
     Checkbox Page Element class, a subclass of PageElement.
    """

    @property
    def option(self):
        """
        Return select option using selenium.
        :return:
        """
        try:
            return self.selenium_select.first_selected_option.text
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    @option.setter
    def option(self, value):
        """
        Set select option using selenium by visible text.
        :param value:
        :return:
        """
        try:
            self.selenium_select.select_by_visible_text(value)
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    @property
    def selenium_select(self):
        """
        Selelect a option with native SeleniumSelect class.
        :return:
        """
        try:
            return SeleniumSelect(self.web_element)
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))
