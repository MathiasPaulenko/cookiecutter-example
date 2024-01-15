# -*- coding: utf-8 -*-
"""
File that configures and executes the driver that has been configured.
"""
import logging
from appium import webdriver as appium_driver
from selenium import webdriver
from selenium.webdriver import Proxy
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.remote.remote_connection import RemoteConnection

from arc.core import constants
from arc.core.config_manager import BaseConfig
from arc.core.driver.driver_capabilities import (
    get_driver_capabilities,
    get_remote_driver_capabilities,
    add_driver_capabilities,
    create_firefox_profile,
    add_remote_browser_driver_capabilities, add_sauce_labs_capabilities, add_perfecto_capabilities,
    add_appium_driver_capabilities,
)
from arc.core.driver.driver_types import DriverTypes
from arc.contrib.utilities import get_message_exception
from arc.core.test_method.exceptions import TalosDriverError
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


class SetupDriver(object):
    """"
    Configuration class and actions of the configured driver.
    """
    utilities = None
    driver_types = None
    base_config = BaseConfig()

    def __init__(self, config, utilities=None, scenario=None):
        self.base_config.config = config
        self.utilities = utilities
        self.driver_types = DriverTypes(self.base_config)
        self.scenario = scenario

    def create_driver(self):
        """
        This function create a instance of driver depending if it is a remote driver or a local driver.
        :return Object:
        """
        driver = self.base_config.config.get('Driver', 'type')
        try:
            if self.base_config.config.getboolean_optional('Server', 'enabled'):
                logger.debug(f"Creating remote driver: {driver}")
                driver = self._set_remote_driver()
            else:
                logger.info(f"Creating local driver: {driver}")
                driver = self._set_local_driver()

        except Exception as ex:
            error_message = f"{driver.capitalize()} driver can not be launched: {get_message_exception(ex)}"
            logger.error(error_message)
            raise TalosDriverError(error_message)

        return driver

    def _set_remote_driver(self):
        """
        This function set remote driver configured.
        :return:
        """
        server_url = f"{self.utilities.get_server_url()}/wd/hub"
        driver = self.base_config.config.get('Driver', 'type')
        driver_name = driver.split('-')[0]
        logger.debug(f"Setting remote driver url: {server_url}")

        if driver_name in (constants.ANDROID, constants.IOS, constants.IPHONE):
            # Set the options for remote mobile driver.
            options = self._set_options_for_remote_driver_mobile()
            logger.debug(f"Setting the options for remote mobile driver: {options}")
            return appium_driver.Remote(command_executor=server_url, desired_capabilities=options)
        else:
            driver_options = get_remote_driver_capabilities(driver_name)
            capabilities = {}

            try:
                capabilities['version'] = driver.split('-')[1]
            except IndexError:
                logger.warning("Driver version capabilities no found.")

            if self.base_config.config.get('Driver', 'proxy-server') != '':
                proxy_server = self.base_config.config.get('Driver', 'proxy-server')
                driver_options.add_argument(f"--proxy-server={proxy_server}")
                logger.debug(f"Proxy server remote driver configured: {proxy_server}")

            # Add options by browser like extensions.
            driver_options = self._set_driver_options_by_browser(driver_name, driver_options)
            # Add browser capabilities.
            driver_options = add_remote_browser_driver_capabilities(driver_name, driver_options, self.base_config)
            # Check if remote execution like saucelabs, perfecto or other.
            driver_options = self._set_options_for_remote_driver_desktop(driver_options)
            logger.debug(f"Setting the options for remote driver: {driver_options}")

            rc = RemoteConnection(server_url)
            rc.set_certificate_bundle_path(None)

            return webdriver.Remote(command_executor=rc, options=driver_options, keep_alive=False)

    def _set_local_driver(self):
        """
        This function set local driver configured.
        :return:
        """
        driver_type = self.base_config.config.get('Driver', 'type')
        driver_name = driver_type.split('-')[0]
        logger.debug(f"Setting local driver type: {driver_name}")

        if driver_name in (constants.ANDROID, constants.IOS, constants.IPHONE):
            driver = self._setup_appium()

        else:
            driver_setup = {
                'firefox': self.driver_types.firefox,
                'chrome': self.driver_types.chrome,
                'safari': self.driver_types.safari,
                'opera': self.driver_types.opera,
                'iexplorer': self.driver_types.explorer,
                'edgeie': self.driver_types.edgeie,
                'edge': self.driver_types.edge,
                'phantomjs': self.driver_types.phantomjs
            }

            driver_setup_method = driver_setup.get(driver_name)

            if not driver_setup_method:
                logger.error(f"Unknown driver {driver_name}")
                raise TalosDriverError(f"Unknown driver {driver_name}")

            capabilities = get_driver_capabilities(driver_name)
            add_driver_capabilities(capabilities, 'Capabilities', self.base_config)
            logger.debug(f"Setting the capabilities for local driver: {capabilities}")

            try:
                if Settings.PYTALOS_RUN.get('execution_proxy').get('enabled'):
                    proxy = Proxy()
                    proxy.proxy_type = ProxyType.MANUAL
                    proxy.http_proxy = Settings.PYTALOS_RUN.get('execution_proxy').get('proxy').get('http_proxy')
                    proxy.ssl_proxy = Settings.PYTALOS_RUN.get('execution_proxy').get('proxy').get('https_proxy')
                    proxy.add_to_capabilities(capabilities)
            except (Exception,) as ex:
                logger.warning(f"The proxy could not be configured: {ex}")

            driver = driver_setup_method(capabilities)

        return driver

    def _setup_appium(self):
        """
        Setup appium server configurations
        :return:
        """
        self.base_config.config.set('Server', 'host', '127.0.0.1')
        self.base_config.config.set('Server', 'port', '4723')
        return self._set_remote_driver()

    def _set_options_for_remote_driver_mobile(self):
        """
        Setup options for remote driver mobile.
        :return:
        """
        options = {}
        logger.debug("Settings options for remote driver mobile")
        if self.base_config.config.get('Server', 'type').lower() == 'saucelabs':
            sauce_options = {
                'name': f"{self.scenario.feature.name} - {self.scenario.name}"
            }
            sauce_options = add_sauce_labs_capabilities(sauce_options, self.base_config)
            options = {
                'browserName': self.base_config.config.get('AppiumCapabilities', 'browserName'),
                'platformName': self.base_config.config.get('AppiumCapabilities', 'platformName'),
                'sauce:options': sauce_options,
            }
        elif self.base_config.config.get('Server', 'type').lower() == 'perfecto':
            perfecto_options = add_perfecto_capabilities(self.base_config)
            perfecto_options['scriptName'] = f"{self.scenario.feature.name} - {self.scenario.name}"
            options = {
                'browserName': self.base_config.config.get('PerfectoCapabilities', 'browserName'),
                'platformName': self.base_config.config.get('PerfectoCapabilities', 'platformName'),
                "perfecto:options": perfecto_options
            }
        # Add appium capabilities.
        add_appium_driver_capabilities(options, 'AppiumCapabilities', self.base_config)
        logger.debug(f"Options for remote driver mobile set: {options}")
        return options

    def _set_options_for_remote_driver_desktop(self, driver_options):
        """
        Setup options for remote driver desktop.
        :param driver_options:
        :return:
        """
        logger.debug("Settings options for remote driver desktop")
        if self.base_config.config.get('Server', 'type').lower() == 'saucelabs':
            logger.debug("Settings options for remote driver desktop in Sauce Labs")
            sauce_options = {
                'name': f"{self.scenario.feature.name} - {self.scenario.name}"
            }
            sauce_options = add_sauce_labs_capabilities(sauce_options, self.base_config)
            driver_options.platform_name = self.base_config.config.get('Capabilities', 'platformName')
            driver_options.browser_version = self.base_config.config.get('Capabilities', 'browserVersion')
            driver_options.set_capability('sauce:options', sauce_options)

        elif self.base_config.config.get('Server', 'type').lower() == 'perfecto':
            logger.debug("Settings options for remote driver desktop in Perfecto")
            perfecto_options = add_perfecto_capabilities(self.base_config)
            perfecto_options['scriptName'] = f"{self.scenario.feature.name} - {self.scenario.name}"
            driver_options.set_capability('perfecto:options', perfecto_options)
            driver_options.platform_name = self.base_config.config.get('Capabilities', 'platformName')
            driver_options.setBrowserVersion = self.base_config.config.get('Capabilities', 'browserVersion')

        logger.debug(f"Options for remote driver desktop set: {driver_options}")
        return driver_options

    def _set_driver_options_by_browser(self, driver_name, driver_options):
        """
        Setup driver options by driver passed by parameter.
        :param driver_name:
        :param driver_options:
        :return:
        """
        logger.debug(f"Settings options for browser: {driver_name}")
        if driver_name == constants.FIREFOX:
            driver_options.profile = create_firefox_profile(self.base_config)

            if self.base_config.config.get('Driver', 'proxy-server') != '':
                logger.debug(f"Settings proxy server for Firefox driver")
                proxy = Proxy()
                proxy.proxy_type = ProxyType.MANUAL
                proxy.http_proxy = self.base_config.config.get('Driver', 'proxy-server')
                proxy.ssl_proxy = self.base_config.config.get('Driver', 'proxy-server')
                driver_options.proxy = proxy

            if self.base_config.config.get('Driver', 'extension-paths') != '':
                logger.debug(f"Settings extension paths for Firefox driver")
                driver_options.set_preference('xpinstall.signatures.required', False)
                driver_options.profile.set_preference('xpinstall.signatures.required', False)
                driver_options.profile.add_extension(extension=self.base_config.config.get('Driver', 'extension-paths'))
            driver_options.profile.update_preferences()
            driver_options.set_preference('profile', driver_options.profile.encoded)

        elif driver_name in [constants.CHROME, constants.EDGE, constants.EDGEIE, constants.IEXPLORER]:
            if self.base_config.config.get('Driver', 'extension-paths') != '':
                logger.debug(f"Settings extension paths for {driver_name} driver")
                driver_options.add_extension(self.base_config.config.get('Driver', 'extension-paths'))

        logger.debug(f"Options for browser set: {driver_options}")
        return driver_options
