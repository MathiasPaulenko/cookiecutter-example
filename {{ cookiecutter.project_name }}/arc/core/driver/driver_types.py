# -*- coding: utf-8 -*-
"""
File containing the driver return class by type.
There are several types of drivers that Talos works with:
    - safari
    - opera
    - explorer
    - edge
    - edgeie (Edge with IE compatibility)
    - phantomjs (Deprecated)
    - firefox
    - chrome
"""
import os
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from arc.core.driver.driver_capabilities import (
    add_firefox_arguments,
    create_firefox_profile,
    create_chrome_options, add_edge_options
)
from arc.core.driver.driver_manager import DriverManager
from arc.core.test_method.exceptions import TalosDriverError
from arc.settings import settings
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


class DriverTypes:
    """
    Configuration construction type according to driver type.
    """

    def __init__(self, base_config):
        self.base_config = base_config

    @staticmethod
    def safari(capabilities):
        """
        Returns an instance of Safari
        :param capabilities:
        :return:
        """
        logger.debug(f"Return Safari instance with capabilities: {capabilities}")
        return webdriver.Safari(desired_capabilities=capabilities)

    def opera(self, capabilities):
        """
        Returns an instance of Opera.
        :param capabilities:
        :return:
        """
        opera_driver = self.base_config.config.get('Driver', 'opera_driver_path')
        logger.debug(f"Return Opera instance with capabilities: {capabilities}")
        logger.debug(f"Opera driver path: {opera_driver}")
        return webdriver.Opera(executable_path=opera_driver, desired_capabilities=capabilities)

    def explorer(self, capabilities):
        """
        Returns an instance of Internet Explorer.
        :param capabilities:
        :return:
        """
        explorer_driver = self.base_config.config.get('Driver', 'explorer_driver_path')
        logger.debug(f"Return Internet Explorer instance with capabilities: {capabilities}")
        logger.debug(f"Explorer driver path: {explorer_driver}")
        return webdriver.Ie(explorer_driver, capabilities=capabilities)

    def edge(self, capabilities):
        """
        Returns an instance of Edge.
        :param capabilities:
        :return:
        """
        if self.base_config.config.getboolean_optional('EdgeOptions', 'headless'):
            Settings.PYTALOS_RUN.set("close_webdriver", value=True)
        edge_driver = self.base_config.config.get('Driver', 'edge_driver_path')
        logger.debug(f"Return Edge instance with capabilities: {capabilities}")
        logger.debug(f"Edge driver path: {edge_driver}")
        edge_options = webdriver.EdgeOptions()
        add_edge_options(edge_options, self.base_config)
        return webdriver.Edge(edge_driver, capabilities=capabilities, options=edge_options)

    def edgeie(self, capabilities):
        """
        Returns an instance of Edge with Internet Explorer compatibility.
        :param capabilities:
        :return:
        """
        explorer_driver = self.base_config.config.get('Driver', 'explorer_driver_path')
        logger.debug(f"Return Edge with IE compatibility instance with capabilities: {capabilities}")
        ie_options = webdriver.IeOptions()
        ie_options.add_additional_option("ie.edgechromium", True)
        ie_options.add_additional_option("ignoreZoomSetting", True)
        edge_app_path = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
        ie_options.add_additional_option("ie.edgepath", edge_app_path)
        logger.debug(f"Edge with IE compatibility options: {ie_options}")
        return webdriver.Ie(executable_path=explorer_driver, capabilities=capabilities, options=ie_options)

    def phantomjs(self, capabilities):
        """
        Returns an instance of PhantomJS.
        :param capabilities:
        :return:
        """
        logger.debug(f"Return PhantomJS instance with capabilities: {capabilities}")
        phantomjs_driver = self.base_config.config.get('Driver', 'phantomjs_driver_path')
        logger.debug(f"Phantom driver path: {phantomjs_driver}")
        try:
            logger.warning(f"PhantomJS driver is currently deprecated")
            return webdriver.PhantomJS(  # noqa
                executable_path=phantomjs_driver,
                desired_capabilities=capabilities
            )
        except (Exception,) as ex:
            logger.error(ex)
            raise TalosDriverError(ex)

    def firefox(self, capabilities):
        """
        Return an instance of Firefox.
        :param capabilities:
        :return:
        """
        gecko_driver = self.base_config.config.get('Driver', 'gecko_driver_path')
        logger.debug(f"Return Firefox instance with capabilities: {capabilities}")
        logger.debug(f"Gecko driver path: {gecko_driver}")

        firefox_binary = self.base_config.config.get_optional('Firefox', 'binary')

        options = Options()

        if self.base_config.config.getboolean_optional('Driver', 'headless'):
            Settings.PYTALOS_RUN.set("close_webdriver", value=True)
            logger.debug("Running Firefox in headless mode")
            options.add_argument('-headless')

        if self.base_config.config.getboolean_optional('FirefoxArguments', 'incognito'):
            options.add_argument('--private')

        add_firefox_arguments(options, self.base_config)

        if firefox_binary:
            options.binary = firefox_binary

        log_path = os.path.join(DriverManager.output_directory, 'geckodriver.log')

        logger.debug(f"Firefox options: {options}")

        try:
            return webdriver.Firefox(
                firefox_profile=create_firefox_profile(self.base_config),
                capabilities=capabilities,
                executable_path=gecko_driver,
                options=options,
                log_path=log_path,
                service_log_path=log_path
            )
        except TypeError:
            return webdriver.Firefox(
                firefox_profile=create_firefox_profile(self.base_config),
                capabilities=capabilities,
                executable_path=gecko_driver,
                options=options,
            )

    def chrome(self, capabilities):
        """
        Returns an instance of Chrome.
        :param capabilities:
        :return:
        """
        chrome_driver = self.base_config.config.get('Driver', 'chrome_driver_path')
        logger.debug(f"Return Chrome instance with capabilities: {capabilities}")
        logger.debug(f"Chrome driver path: {chrome_driver}")
        chrome_path = os.path.join(Settings.DRIVERS_HOME.get(force=True), chrome_driver)
        return webdriver.Chrome(
            executable_path=chrome_path,
            chrome_options=create_chrome_options(self.base_config),
            desired_capabilities=capabilities
        )
