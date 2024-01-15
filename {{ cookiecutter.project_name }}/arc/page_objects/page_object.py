# -*- coding: utf-8 -*-
"""
PageObject module.
"""
from arc.contrib.tools.repository import Repository
from arc.core.driver.driver_manager import DriverManager
from arc.page_objects.common_object import CommonObject
from arc.settings.settings_manager import Settings


class PageObject(CommonObject):
    """
    PageObject class, subclass of CommonObject.
    All page objects to be used in the tests must inherit from this class and implement the init_page_elements method
    for the correct functioning of the user page objects.
    """
    app_strings = None

    def __init__(self, context=None, driver_wrapper=None, wait=False):
        super(PageObject, self).__init__()
        self.wait = wait
        self.driver_wrapper = driver_wrapper if driver_wrapper else DriverManager.get_default_wrapper()
        self.context = context
        if Settings.PYTALOS_PROFILES.get('repositories') is True:
            self.repositories = context.repositories if context is not None else Repository()
            self.literals = self.repositories.literals
            self.elements = self.repositories.elements
        self.lang = Settings.PYTALOS_PROFILES.get('language')
        self.init_page_elements()
        self.reset_object(self.driver_wrapper)

    def reset_object(self, driver_wrapper=None):
        """
        Reset current page object.
        :param driver_wrapper:
        :return:
        """
        if driver_wrapper:
            self.driver_wrapper = driver_wrapper
        self.app_strings = self.driver_wrapper.app_strings
        for element in self._get_page_elements():
            element.reset_object()

    def init_page_elements(self):
        """
        It includes all the page elements of this method.
        :return:
        """
        pass

    def _get_page_elements(self):
        """
        Return page elements declared.
        :return:
        """
        page_elements = []
        for attribute, value in list(self.__dict__.items()) + list(self.__class__.__dict__.items()):
            if attribute != 'parent' and isinstance(value, CommonObject):
                page_elements.append(value)
        return page_elements

    def wait_until_loaded(self, timeout=None):
        """
        Wait until page elements is loaded.
        :param timeout:
        :return:
        """
        for element in self._get_page_elements():
            if hasattr(element, 'wait') and element.wait:
                from arc.page_elements import PageElement
                if isinstance(element, PageElement):
                    element.wait_until_visible(timeout)
                if isinstance(element, PageObject):
                    element.wait_until_loaded(timeout)
        return self

    def format_text(self, element, text=None, **kwargs):
        """
        Return repository data formatted.
        :param element:
        :param text:
        :param kwargs:
        :return:
        """
        return self.repositories.format_text(element, text, **kwargs)
