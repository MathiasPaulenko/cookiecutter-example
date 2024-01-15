# -*- coding: utf-8 -*-
"""
InputText Page Element class file
"""
import logging

from arc.core.test_method.exceptions import TalosTestError
from arc.page_elements.page_element import PageElement

logger = logging.getLogger(__name__)


class InputText(PageElement):
    """
    InputText Page Element class, a subclass of PageElement.
    """

    @property
    def text(self):
        """
        Return text from attribute value from input text page element.
        :return:
        """
        try:
            return self.web_element.get_attribute("value")
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    @text.setter
    def text(self, value):
        """
        Set text value to input text page element.
        :param value:
        :return:
        """
        try:
            if self.driver_wrapper.is_ios_test() and not self.driver_wrapper.is_web_test():
                self.web_element.send_keys(value)
            elif self.shadowroot:
                self.driver.execute_script('return document.querySelector("%s")'
                                           '.shadowRoot.querySelector("%s")'
                                           '.value = "%s"' % (self.shadowroot, self.locator[1], value))
            else:
                self.web_element.send_keys(value)
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))

    def clear(self):
        """
        Clear value from input text page element.
        :return:
        """
        try:
            self.web_element.clear()
            return self
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))
