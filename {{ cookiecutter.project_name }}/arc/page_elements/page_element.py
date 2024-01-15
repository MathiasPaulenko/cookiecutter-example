# -*- coding: utf-8 -*-
"""
Page Element class, parent of all elements.
"""
import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from arc.core.brain.scraping import Scraper
from arc.core.driver.driver_manager import DriverManager
from arc.page_objects.common_object import CommonObject
from arc.core.test_method.visual_test import VisualTest
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)
SELF_HEALING_ENABLED = Settings.PYTALOS_IA.get('self-healing', {}).get('enabled', False)


class PageElement(CommonObject):
    """
    Page Element class instance, subclass of CommonObject.
    """
    _web_element = None

    def __init__(
            self, by=None, value=None, multi_locator: list = None,
            parent=None, order=None, wait=False, shadowroot=None
    ):
        super(PageElement, self).__init__()
        if multi_locator is not None:
            self.locator = multi_locator
        else:
            self.locator = (by, value)
        self.parent = parent
        self.order = order
        self.wait = wait
        self.shadowroot = shadowroot
        self.shadowroot_advanced = False
        self.driver_wrapper = DriverManager.get_default_wrapper()
        self.reset_object(self.driver_wrapper)
        self.locator_was_mod = False

    def reset_object(self, driver_wrapper=None):
        """
        Reset page object element.
        :param driver_wrapper:
        :return:
        """
        logger.debug("Resetting page element object")
        if driver_wrapper:
            self.driver_wrapper = driver_wrapper
        self._web_element = None

    def scraping_element(self):
        """
        Calls the save_web_element_scraping function from utils
        to get the info of an interactive element.
        """
        from arc.core.brain.scraping import Scraper
        if self.locator_was_mod is False:
            scraper = Scraper(self.driver)
            scraper.save_web_element_scraping(self._web_element, self.locator)

    @property
    def web_element(self):
        """
        Find web element or raise error.
        :return:
        """
        try:
            self._find_web_element()
            self.scraping_element()
        except NoSuchElementException as exception:
            parent_msg = " and parent locator '{}'".format(self.parent) if self.parent else ''  # noqa
            msg = "Page element of type '%s' with locator %s%s not found"
            exception.msg += "\n  {}".format(msg % (type(self).__name__, self.locator, parent_msg)) # noqa
            self.logger.error(exception)
            raise exception
        return self._web_element

    def _find_web_element(self):
        """
        Find web element
        :return:
        """
        logger.debug("Finding web element")
        if (isinstance(self.locator, list) and '.shadowRoot.' in self.locator[0][1]) or '.shadowRoot.' in self.locator[
            1]:
            logger.debug('A shadow root class has been detected in the element')
            self.shadowroot_advanced = True
        if not self._web_element or not self.config.getboolean_optional('Driver', 'save_web_element'):
            # If the element is encapsulated we use the shadowroot tag in yaml (eg. Shadowroot: root_element_name)
            if self.shadowroot_advanced or self.shadowroot:
                self.find_shadow_root_element()
            else:
                # Element will be found from parent element or from driver
                base = self.utils.get_web_element(self.parent) if self.parent else self.driver
                if isinstance(self.locator, tuple):
                    self._web_element = self.find_element(base, self.locator[0], self.locator[1])
                elif isinstance(self.locator, list):
                    locators = self.locator.copy()
                    for index, locator in enumerate(locators):
                        # Find elements and get the correct index or find a single element
                        try:
                            selected_element = self.find_element(base, locator[0], locator[1])
                            if isinstance(selected_element, WebElement):
                                self.found_element = True
                                self._web_element = selected_element
                                # When the first valid locator is found we must set again the locator attribute
                                # in order to be used in future methods like wait_until,
                                # otherwise the execution duration will be longer.
                                self.locator = (locator[0], locator[1])
                                break
                        except NoSuchElementException as exception:
                            if index == len(locators) - 1 and not self.found_element:
                                exception.msg = f"No such element: Unable to locate" \
                                                f" element/s with locators and elements {self.locator}"
                                self.locator = (locator[0], locator[1])
                                self._web_element = exception
                                logger.error(exception)
                                raise exception

    def scroll_element_into_view(self):
        """
        Scroll to element into view.
        :return:
        """
        x = self.web_element.location['x']
        y = self.web_element.location['y']
        logger.debug(f"Scrolling into element view: {x} and {y}")
        if self.driver_wrapper.is_mobile_test():
            self.driver.swipe(start_x=x, start_y=y, end_x=0, end_y=0, duration=2)
        else:
            self.driver.execute_script('window.scrollTo({0}, {1})'.format(x, y))
        return self

    def is_present(self):
        """
        Check if a web element is present.
        :return:
        """
        try:
            self._web_element = None
            self._find_web_element()
            logger.debug(f"Web element is present")
            return True
        except NoSuchElementException:
            logger.debug(f"Web element is not present")
            return False

    def is_visible(self):
        """
        Check if a web element is visible.
        :return:
        """
        logger.debug('Checking if web element is visible')
        return self.is_present() and self.web_element.is_displayed()

    def wait_until_visible(self, timeout=None):
        """
        Wait until web element is visible.
        :param timeout:
        :return:
        """
        logger.debug("Waiting until web element is visible")
        try:
            self.utils.wait_until_element_visible(self, timeout)
        except TimeoutException as exception:
            parent_msg = " and parent locator '{}'".format(self.parent) if self.parent else ''
            msg = "Page element of type '%s' with locator %s%s not found or is not visible after %s seconds"
            timeout = timeout if timeout else self.utils.get_explicitly_wait()
            self.logger.error(msg, type(self).__name__, self.locator, parent_msg, timeout)
            exception.msg += "\n  {}".format(msg % (type(self).__name__, self.locator, parent_msg, timeout))
            logger.error(exception)
            raise exception
        return self

    def wait_until_not_visible(self, timeout=None):
        """
        Wait web element until element is not visible.
        :param timeout:
        :return:
        """
        logger.debug("Waiting until web element is not visible")
        try:
            self.utils.wait_until_element_not_visible(self, timeout)
        except TimeoutException as exception:
            parent_msg = " and parent locator '{}'".format(self.parent) if self.parent else ''
            msg = "Page element of type '%s' with locator %s%s is still visible after %s seconds"
            timeout = timeout if timeout else self.utils.get_explicitly_wait()
            self.logger.error(msg, type(self).__name__, self.locator, parent_msg, timeout)
            exception.msg += "\n  {}".format(msg % (type(self).__name__, self.locator, parent_msg, timeout))
            logger.error(exception)
            raise exception
        return self

    def wait_until_clickable(self, timeout=None):
        """
        Wait web element is clickable.
        :param timeout:
        :return:
        """
        logger.debug("Waiting until web element is clickable")
        try:
            self.utils.wait_until_element_clickable(self, timeout)
        except TimeoutException as exception:
            parent_msg = " and parent locator '{}'".format(self.parent) if self.parent else ''
            msg = "Page element of type '%s' with locator %s%s not found or is not clickable after %s seconds"
            timeout = timeout if timeout else self.utils.get_explicitly_wait()
            self.logger.error(msg, type(self).__name__, self.locator, parent_msg, timeout)
            exception.msg += "\n  {}".format(msg % (type(self).__name__, self.locator, parent_msg, timeout))
            logger.error(exception)
            raise exception
        return self

    def assert_screenshot(self, filename, threshold=0, exclude_elements=None, force=False):
        """
        Assert screehsnot from filename with current page.
        :param filename:
        :param threshold:
        :param exclude_elements:
        :param force:
        :return:
        """
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(self.driver_wrapper, force).assert_screenshot(
            self.web_element,
            filename,
            self.__class__.__name__,
            threshold,
            exclude_elements
        )

    def get_attribute(self, name):
        """
        Get the given attribute or property of the element
        :param name: name of the attribute/property to retrieve
        :returns: attribute value
        """
        logger.debug(f"Getting web element attribute: {name}")
        return self.web_element.get_attribute(name)

    def find_element(self, base, locator, value):
        """
        Return web element from a base element.
        :param base:
        :param locator:
        :param value:
        :return:
        """
        selected_element = None
        try:
            if self.order:
                selected_element = base.find_elements(by=locator, value=value)[self.order]
            else:
                selected_element = base.find_element(by=locator, value=value)
        except NoSuchElementException:
            if SELF_HEALING_ENABLED:
                new_locator = self.self_healing()
                if new_locator:
                    self.locator = new_locator
                    self.locator_was_mod = True
                else:
                    logger.info('Unable to get a new locator for the element')
            else:
                logger.info('Self-healing is disabled')
        return selected_element

    def find_shadow_root_element(self):
        """
        Find web element from shadow root element.
        :return:
        """
        logger.debug('Finding element from shadow root')
        if isinstance(self.locator, list):
            by_selector = self.locator[0][0]
            locator = self.locator[0][1]
        else:
            by_selector = self.locator[0]
            locator = self.locator[1]

        if by_selector != By.CSS_SELECTOR:
            raise NoSuchElementException(
                f'Locator type should be CSS_SELECTOR using shadowroot but found: {by_selector}'
            )
        # querySelector only support CSS SELECTOR locator
        if self.shadowroot_advanced is True:
            locators = locator.split('.shadowRoot.')
            self._web_element = self.utils.get_element_inside_shadowroot(locators)
        elif self.shadowroot:
            self._web_element = self.driver.execute_script(
                'return document.querySelector("%s").shadowRoot.'
                'querySelector("%s")' % (
                    self.shadowroot,
                    locator
                )
            )

    def self_healing(self):
        """
        Scraps the current page and gets the new healed locator using the self-healing script.
        :return:
        """
        from arc.core.brain.healing import init_healing
        scraper = Scraper(self.driver)
        scraper.scraping_current_page_elements()
        new_locator = init_healing(self.locator)
        return new_locator
