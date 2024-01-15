# -*- coding: utf-8 -*-
"""
Functions for automatic installation of selenium browser drivers.
"""
import logging
import os
import shutil

from arc.core.test_method.exceptions import TalosRunError
from arc.settings.settings_manager import Settings
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from arc.core import constants

logger = logging.getLogger(__name__)


def _disabled_proxy():
    """
    This function disables the proxy configured when installing the drivers if the proxy option is enabled in
    the settings
    :return:
    """
    if Settings.PYTALOS_GENERAL.get('update_driver').get('enable_proxy'):
        logger.debug("Disabling existed proxy for installing driver")
        os.environ["HTTP_PROXY"] = ""
        os.environ["HTTPS_PROXY"] = ""


def _enabled_proxy():
    """
    This function disables the proxy configured when installing the drivers if the proxy option is disabled in
    the settings
    :return:
    """
    if Settings.PYTALOS_GENERAL.get('update_driver').get('enable_proxy'):
        http = Settings.PYTALOS_GENERAL.get('update_driver').get('proxy').get('http_proxy')
        https = Settings.PYTALOS_GENERAL.get('update_driver').get('proxy').get('https_proxy')
        logger.debug(f"http: {http}")
        logger.debug(f"https: {https}")
        logger.debug("settings.PYTALOS_GENERAL['update_driver']['proxy']['http_proxy']")
        os.environ["HTTP_PROXY"] = http
        os.environ["HTTPS_PROXY"] = https


class InstallDriver:
    """
    Selenium driver automatic installation class.
    """
    drivers_path = 'settings/drivers/'

    def __init__(self, driver_name):
        logger.debug(f"Initializing {driver_name} installation")
        self.driver_name = driver_name

    def _move_driver(self, driver_path):
        logger.debug(f"Moving driver into: {driver_path}")
        shutil.move(driver_path, self.drivers_path + self.driver_name)

    def _download_driver(self, driver):
        logger.debug(f"Downloading driver: {driver}")
        driver_path = ''
        if driver == constants.IEXPLORER:
            driver_path = IEDriverManager().install()
        elif driver == constants.CHROME:
            driver_path = ChromeDriverManager().install()
        elif driver == constants.EDGE:
            driver_path = EdgeChromiumDriverManager().install()
        elif driver == constants.FIREFOX:
            driver_path = GeckoDriverManager().install()
        logger.debug(f"Successful driver download in: {driver_path}")
        return driver_path

    def install_driver(self, driver):
        """
        This method start the driver installation..
        :param driver:
        :return:
        """
        try:
            _enabled_proxy()
            driver_path = self._download_driver(driver)
            self._move_driver(driver_path)
            _disabled_proxy()
        except (Exception,):
            msg = 'Impossible to update ' + driver + ' driver.'
            logger.exception(msg)
            raise TalosRunError(msg)
