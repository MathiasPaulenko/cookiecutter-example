# -*- coding: utf-8 -*-
"""
InputRadio Page Element class file
"""
import logging

from arc.core.test_method.exceptions import TalosTestError
from arc.page_elements.button_page_element import Button

logger = logging.getLogger(__name__)


class InputRadio(Button):
    """
    InputRadio Page Element class, a subclass of PageElement.
    """

    @property
    def text(self):
        """
        Return text from Input radio value attribute Page Element
        :return:
        """
        try:
            return self.web_element.get_attribute("value")
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    def is_selected(self):
        """
        Select or click on input radio option if input radio is already check, this function does nothing.
        :return:
        """
        try:
            return self.web_element.is_selected()
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    def check(self):
        """
        Unselect or click on input radio option if input radio is already uncheck, this function does nothing.
        :return:
        """
        try:
            return self.click()
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))