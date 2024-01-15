# -*- coding: utf-8 -*-
"""
Button Page Element class file
"""
import logging

from selenium.common.exceptions import StaleElementReferenceException

from arc.core.test_method.exceptions import TalosTestError
from arc.page_elements.page_element import PageElement

logger = logging.getLogger(__name__)


class Button(PageElement):
    """
    Button Page Element class, a subclass of PageElement.
    """

    @property
    def text(self):
        """
        Return text from button Page Element
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

    def click(self):
        """
        Click on button page element
        :return:
        """
        try:
            self.wait_until_clickable().web_element.click()
        except StaleElementReferenceException:
            # Retry if element has changed
            self.web_element.click()
        except Exception as ex:
            logger.error(str(ex))
            raise TalosTestError(str(ex))
        return self
