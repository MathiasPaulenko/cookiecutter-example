# -*- coding: utf-8 -*-
"""
Page Elements class, parent of all elements.
"""
import logging

from arc.core.driver.driver_manager import DriverManager
from arc.page_elements.button_page_element import Button
from arc.page_elements.checkbox_page_element import Checkbox
from arc.page_elements.group_page_element import Group
from arc.page_elements.input_radio_page_element import InputRadio
from arc.page_elements.input_text_page_element import InputText
from arc.page_elements.layer_page_element import Layer
from arc.page_elements.link_page_element import Link
from arc.page_elements.page_element import PageElement
from arc.page_elements.select_page_element import Select
from arc.page_elements.text_page_element import Text
from arc.page_objects.common_object import CommonObject

logger = logging.getLogger(__name__)


class PageElements(CommonObject):
    """
    Page Elements class instance, subclass of CommonObject.
    """
    page_element_class = PageElement
    _web_elements = None

    def __init__(self, by, value, parent=None, page_element_class=None, order=None):
        super(PageElements, self).__init__()
        self.locator = (by, value)
        self.parent = parent
        self.order = order
        self.shadowroot = None
        self.driver_wrapper = DriverManager.get_default_wrapper()

        if page_element_class:
            self.page_element_class = page_element_class
        self._page_elements = []
        self.reset_object(self.driver_wrapper)

    def reset_object(self, driver_wrapper=None):
        """
        Reset page object element.
        :param driver_wrapper:
        :return:
        """
        logger.debug('Reset page object elements')
        if driver_wrapper:
            self.driver_wrapper = driver_wrapper
        for element in self._page_elements:
            element.reset_object(driver_wrapper)
        self._web_elements = []
        self._page_elements = []

    @property
    def web_elements(self):
        """
        Find web element or raise error.
        :return:
        """
        if not self._web_elements or not self.config.getboolean_optional('Driver', 'save_web_element'):
            if self.parent:
                self._web_elements = self.utils.get_web_element(self.parent).find_elements(*self.locator)
            else:
                self._web_elements = self.driver.find_elements(*self.locator)
        return self._web_elements

    @property
    def page_elements(self):
        """
        return all web element matches with the locator.
        :return:
        """
        if not self._page_elements or not self.config.getboolean_optional('Driver', 'save_web_element'):
            self._page_elements = []
            for order, web_element in enumerate(self.web_elements):
                page_element = self.page_element_class(self.locator[0], self.locator[1], parent=self.parent,
                                                       order=order)
                page_element.reset_object(self.driver_wrapper)
                page_element._web_element = web_element
                self._page_elements.append(page_element)
        return self._page_elements


class Buttons(PageElements):
    """
    Button page element class.
    """
    page_element_class = Button


class Checkboxes(PageElements):
    """
    Checkboxes page element class.
    """
    page_element_class = Checkbox


class InputRadios(PageElements):
    """
    InputRadios page element class.
    """
    page_element_class = InputRadio


class InputTexts(PageElements):
    """
    InputTexts page element class.
    """
    page_element_class = InputText


class Links(PageElements):
    """
    Links page element class.
    """
    page_element_class = Link


class Selects(PageElements):
    """
    Selects page element class.
    """
    page_element_class = Select


class Texts(PageElements):
    """
    Texts page element class.
    """
    page_element_class = Text


class Groups(PageElements):
    """
    Groups page element class.
    """
    page_element_class = Group


class Layers(PageElements):
    """
    Layers page element class.
    """
    page_element_class = Layer
