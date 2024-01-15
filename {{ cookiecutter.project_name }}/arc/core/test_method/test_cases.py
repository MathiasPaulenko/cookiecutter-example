# -*- coding: utf-8 -*-
"""
This file contains configuration classes of test types to be executed.

The parent class BasicTestCase has the information of a generic test case to execute.

Two subclasses that inherit from BasicTestCase:
- SeleniumTestCase
- AppiumTestCase
"""
import logging
import sys
import unittest

from arc.core.config_manager import ConfigFiles
from arc.core.driver.driver_manager import DriverManager
from arc.contrib.utilities import get_message_exception

logger = logging.getLogger(__name__)


class BasicTestCase(unittest.TestCase):
    """
    Parent class of the driver execution types, such as selenium and appium, contains the hooks methods setup,
    teardown, among others.
    """
    config_files = ConfigFiles()
    driver_wrapper = None

    def __init__(self, method_name: str = ...):
        super().__init__(method_name)
        self._outcomeForDoCleanups = None
        self._outcome = None

    @classmethod
    def get_subclass_name(cls):
        """
        Get subclass name.
        :return:
        """
        return cls.__name__

    def get_method_name(self):
        """
        Get method name parsed.
        :return:
        """
        # Split remove the test suffix added by ddt library
        return self._testMethodName.split('___')[0]

    def get_subclassmethod_name(self):
        """
        Get subclass method name parsed.
        :return:
        """
        return self.__class__.__name__ + "." + self.get_method_name()

    @classmethod
    def tearDownClass(cls):
        """
        Method to implement.
        :return:
        """
        pass
        # change_all_jira_status()

    def setUp(self):
        """
        Global set up method configurations at the beginning of everything.
        :return:
        """
        # Configure logger and properties
        if not isinstance(self, SeleniumTestCase):
            # By default config directory is located in test path
            if not self.config_files.config_directory:
                self.config_files.set_config_directory(DriverManager.get_default_config_directory())

            self.driver_wrapper = DriverManager.get_default_wrapper()
            self.config_files = DriverManager.initialize_config_files(self.config_files)
            self.driver_wrapper.configure(self.config_files, is_selenium_test=False)
        # Get config and logger instances
        self.config = self.driver_wrapper.config
        logger.info("Running new test: %s", self.get_subclassmethod_name())

    def tearDown(self):
        """
        Closure method and analysis of results.
        :return:
        """
        py2_exception = sys.exc_info()[1]
        try:
            # Python 3.4+
            exception_info = self._outcome.errors[-1][1] if len(self._outcome.errors) > 0 else None
            exception = exception_info[1] if exception_info else None
            logger.warning(exception)
        except AttributeError:
            try:
                # Python 3.3
                exceptions_list = self._outcomeForDoCleanups.failures + self._outcomeForDoCleanups.errors
                exception = exceptions_list[0][1] if exceptions_list else None
                logger.warning(exception)

            except AttributeError:
                # Python 2.7
                exception = py2_exception
                logger.warning(exception)

        if not exception:
            self._test_passed = True
            logger.info("The test '%s' has passed", self.get_subclassmethod_name())
        else:
            self._test_passed = False
            error_message = get_message_exception(exception)
            logger.error("The test '%s' has failed: %s", self.get_subclassmethod_name(), error_message)


class SeleniumTestCase(BasicTestCase):
    """
    Test case class for Selenium executions, subclass of BasicTestCase.
    """
    driver = None
    utils = None

    @classmethod
    def tearDownClass(cls):
        """
        Call tearDownClass of parent class, close driver.
        :return:
        """
        super(SeleniumTestCase, cls).tearDownClass()
        DriverManager.close_drivers(scope='class', test_name=cls.get_subclass_name())

    def setUp(self):
        """
        Set up selenium test case configuration.
        :return:
        """
        if not self.config_files.config_directory:
            self.config_files.set_config_directory(DriverManager.get_default_config_directory())

        self.driver_wrapper = DriverManager.connect_default_driver_wrapper(config_files=self.config_files)
        SeleniumTestCase.driver = self.driver_wrapper.driver
        self.utils = self.driver_wrapper.utils

        # Call BasicTestCase setUp
        super(SeleniumTestCase, self).setUp()

    def tearDown(self):
        """
        Call BasicTestcase TearDown and close drivers.
        :return:
        """
        # Call BasicTestCase tearDown
        super(SeleniumTestCase, self).tearDown()
        # Close drivers
        DriverManager.close_drivers(
            scope='function',
            test_name=self.get_subclassmethod_name(),
            test_passed=self._test_passed
        )


class AppiumTestCase(SeleniumTestCase):
    """
    Test case class for Appium executions, subclass of BasicTestCase.
    """
    app_strings = None

    @property
    def driver(self):
        """
        Return driver from SeleniumTestCase class.
        :return:
        """
        return SeleniumTestCase.driver

    def setUp(self):
        """
        Set up selenium test case configuration.
        :return:
        """
        self.driver_wrapper = DriverManager.get_default_wrapper()
        if not self.driver_wrapper.driver and not self.config_files.config_directory:
            # By default config directory is located in test path
            self.config_files.set_config_directory(DriverManager.get_default_config_directory())

        super(AppiumTestCase, self).setUp()
        AppiumTestCase.app_strings = self.driver_wrapper.app_strings
