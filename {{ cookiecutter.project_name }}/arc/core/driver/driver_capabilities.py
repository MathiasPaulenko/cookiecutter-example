# -*- coding: utf-8 -*-
"""
File that contains functions for configuring the capabilities of the drivers.
"""
import ast
import os
import logging
from configparser import NoSectionError
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

from arc.core import constants
from arc.core.test_method.exceptions import TalosConfigurationError
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

APPIUM_SERVER = 'Appium server'


def get_driver_capabilities(driver_name):
    """
    This function obtains the capabilities corresponding to the type of driver to be executed.
    :param driver_name:
    :return:
    """
    logger.info(f"Getting capabilities for the driver: {driver_name}")
    if driver_name == constants.FIREFOX:
        return DesiredCapabilities.FIREFOX.copy()
    elif driver_name == constants.CHROME:
        return DesiredCapabilities.CHROME.copy()
    elif driver_name == constants.SAFARI:
        return DesiredCapabilities.SAFARI.copy()
    elif driver_name == constants.OPERA:
        return DesiredCapabilities.OPERA.copy()
    elif driver_name == constants.IEXPLORER:
        return DesiredCapabilities.INTERNETEXPLORER.copy()
    elif driver_name == constants.EDGEIE:
        return DesiredCapabilities.INTERNETEXPLORER.copy()
    elif driver_name == constants.EDGE:
        return DesiredCapabilities.EDGE.copy()
    elif driver_name == constants.PHANTOMJS:
        return DesiredCapabilities.CHROME.copy()
    elif driver_name in (constants.ANDROID, constants.IOS, constants.IPHONE):
        return {}

    msg = f"Unknown driver {driver_name}"
    logger.error(msg)
    raise TalosConfigurationError(msg)


def get_remote_driver_capabilities(driver_name):
    """
    This function obtains the capabilities corresponding to the type of remote driver to be executed.

    :param driver_name:
    :return:
    """
    logger.info(f"Getting capabilities for the driver: {driver_name}")
    if driver_name == constants.FIREFOX:
        return webdriver.FirefoxOptions()
    elif driver_name == constants.CHROME:
        return webdriver.ChromeOptions()
    elif driver_name == constants.SAFARI:
        return webdriver.Safari()
    elif driver_name == constants.OPERA:
        return webdriver.Opera()
    elif driver_name == constants.IEXPLORER:
        return webdriver.IeOptions()
    elif driver_name == constants.EDGEIE:
        return webdriver.EdgeOptions()
    elif driver_name == constants.EDGE:
        return webdriver.EdgeOptions()
    elif driver_name == constants.PHANTOMJS:
        return webdriver.ChromeOptions()
    elif driver_name in (constants.ANDROID, constants.IOS, constants.IPHONE):
        return {}
    msg = f"Unknown driver {driver_name}"
    logger.error(msg)
    raise TalosConfigurationError(msg)


def add_driver_capabilities(capabilities, section, base_config):
    """
    This function add capabilities into the driver from properties cfg file.
    :param capabilities:
    :param section:
    :param base_config:
    :return:
    """
    logger.debug(f"Adding webdriver capabilities: {capabilities}")
    capabilities_type = {'Capabilities': 'server', 'AppiumCapabilities': APPIUM_SERVER}
    try:
        for cap, cap_value in dict(base_config.config.items(section)).items():
            logger.debug(f"Added {capabilities_type[section]} capability: {cap} = {cap_value}")
            capabilities[cap] = cap_value if cap == 'version' else _convert_property_type(cap_value)
    except NoSectionError as ex:
        logger.warning(ex)


def add_appium_driver_capabilities(capabilities, section, base_config):
    """
    This function add capabilities into the appium driver from properties cfg file.
    :param capabilities:
    :param section:
    :param base_config:
    :return:
    """
    logger.debug(f"Adding appium driver capabilities: {capabilities}")
    capabilities_type = {'Capabilities': 'server', 'AppiumCapabilities': APPIUM_SERVER}
    try:
        for cap, cap_value in dict(base_config.config.items(section)).items():
            logger.debug(f"Added {capabilities_type[section]} capability: {cap} = {cap_value}")
            capabilities[f"appium:{cap}"] = cap_value if cap == 'version' else _convert_property_type(cap_value)
    except NoSectionError as ex:
        logger.warning(ex)


def add_remote_driver_capabilities(capabilities, section, base_config):
    """
    This function add capabilities into the remote driver from properties cfg file.

    :param capabilities:
    :param section:
    :param base_config:
    :return:
    """
    logger.debug(f"Adding remote driver capabilities: {capabilities}")
    capabilities_type = {'Capabilities': 'server', 'AppiumCapabilities': APPIUM_SERVER}
    try:
        for cap, cap_value in dict(base_config.config.items(section)).items():
            logger.debug(f"Added {capabilities_type[section]} capability: {cap} = {cap_value}")
            capabilities.set_capability(cap, cap_value if cap == 'version' else _convert_property_type(cap_value))
    except NoSectionError as ex:
        logger.warning(ex)


def _convert_property_type(value):
    """
    This function convert property into type
    :param value:
    :return:
    """
    if value in ('true', 'True'):
        return True
    elif value in ('false', 'False'):
        return False
    elif str(value).startswith('{') and str(value).endswith('}'):
        return ast.literal_eval(value)
    else:
        try:
            return int(value)
        except ValueError:
            return value


def add_firefox_arguments(options, base_config):
    """
    This function add firefox arguments to driver
    :param options:
    :param base_config:
    :return:
    """
    logger.debug(f"Adding firefox driver arguments: {options}")
    try:
        for preference, preference_value in dict(base_config.config.items('FirefoxArguments')).items():
            preference_value = '={}'.format(preference_value) if preference_value else ''
            logger.debug(f"Added Firefox argument: {preference} = {preference_value}")
            options.add_argument('{}{}'.format(preference, _convert_property_type(preference_value)))
    except NoSectionError as ex:
        logger.warning(ex)


def create_firefox_profile(base_config):
    """
    This function create a firefox profiles if enabled the profile option within properties file
    :param base_config:
    :return:
    """
    logger.debug("Creating firefox profile")
    profile_directory = base_config.config.get_optional('Firefox', 'profile')

    if profile_directory:
        logger.debug(f"Using Firefox profile: {profile_directory}")

    profile = webdriver.FirefoxProfile(profile_directory=profile_directory)
    profile.native_events_enabled = True

    try:
        for preference, preference_value in dict(base_config.config.items('FirefoxPreferences')).items():
            logger.debug(f"Added Firefox preference: {preference} = {preference_value}")
            profile.set_preference(preference, _convert_property_type(preference_value))
        profile.update_preferences()
    except NoSectionError as ex:
        logger.warning(ex)

    try:
        for preference, preference_value in dict(base_config.config.items('FirefoxExtensions')).items():
            logger.debug(f"Added Firefox extension: {preference} = {preference_value}")
            profile.add_extension(preference_value)
    except NoSectionError as ex:
        logger.warning(ex)

    return profile


def create_chrome_options(base_config):
    """
    This function create chrome driver options with the required format.
    :param base_config:
    :return:
    """
    options = webdriver.ChromeOptions()
    logger.debug("Creating chrome driver options")
    if base_config.config.getboolean_optional('Driver', 'headless'):
        Settings.PYTALOS_RUN.set("close_webdriver", value=True)
        logger.debug("Running Chrome in headless mode")
        options.add_argument('--headless')
        if os.name == 'nt':
            options.add_argument('--disable-gpu')

    add_chrome_options(options, 'prefs', base_config)
    add_chrome_options(options, 'mobileEmulation', base_config)
    add_chrome_arguments(options, base_config)
    logger.debug(f"Chrome driver options added: {options}")
    return options


def add_chrome_options(options, option_name, base_config):
    """
    This functions add chrome options within options format configuration
    :param options:
    :param option_name:
    :param base_config:
    :return:
    """

    logger.debug(f"Adding the chrome option {option_name} into options config")
    options_conf = {
        'prefs': {
            'section': 'ChromePreferences',
            'message': 'preference'
        },
        'mobileEmulation': {
            'section': 'ChromeMobileEmulation',
            'message': 'mobile emulation option'
        }
    }

    option_value = dict()
    try:
        for key, value in dict(base_config.config.items(options_conf[option_name]['section'])).items():
            logger.debug("Added chrome %s: %s = %s", options_conf[option_name]['message'], key, value)
            option_value[key] = _convert_property_type(value)
        if len(option_value) > 0:
            options.add_experimental_option(option_name, option_value)
        options.add_experimental_option('detach', Settings.PYTALOS_RUN.get('webdriver_detach', default=True))
    except NoSectionError as ex:
        logger.warning(ex)


def add_chrome_arguments(options, base_config):
    """
    This function add chrome arguments within options
    :param options:
    :param base_config:
    :return:
    """
    logger.debug("Adding chrome arguments")
    try:
        for preference, preference_value in dict(base_config.config.items('ChromeArguments')).items():
            preference_value = '={}'.format(preference_value) if preference_value else ''
            logger.debug(f"Added Chrome argument: {preference} {preference_value}")
            options.add_argument('{}{}'.format(preference, _convert_property_type(preference_value)))
    except NoSectionError as ex:
        logger.warning(ex)


def add_edge_options(options, base_config):
    """
        This function add edge options within options
        :return:
        """
    logger.debug("Adding edge options")
    try:
        for preference, preference_value in dict(base_config.config.items('EdgeOptions')).items():
            if preference_value.lower() == 'true':
                preference_value = '={}'.format(preference_value) if preference_value else ''
                logger.debug(f"Added Edge Option: {preference} {preference_value}")
                options.add_argument('{}{}'.format(preference, _convert_property_type(preference_value)))
    except NoSectionError as ex:
        logger.warning(ex)


def add_remote_browser_driver_capabilities(driver_name, options, base_config):
    """
    This functions add remote browser driver capabilities options
    :param driver_name:
    :param options:
    :param base_config:
    :return:
    """
    driver_options = {}
    if driver_name == constants.CHROME:
        driver_options = dict(base_config.config.items('ChromeArguments'))
    elif driver_name == constants.SAFARI:
        driver_options = dict(base_config.config.items('SafariArguments'))
    elif driver_name == constants.OPERA:
        driver_options = dict(base_config.config.items('OperaArguments'))
    elif driver_name == constants.IEXPLORER:
        driver_options = dict(base_config.config.items('IExplorerArguments'))
    elif driver_name == constants.EDGEIE:
        driver_options = dict(base_config.config.items('EdgeArguments'))
    elif driver_name == constants.EDGE:
        driver_options = dict(base_config.config.items('EdgeArguments'))
    logger.debug(f"Adding remote {driver_name} driver capabilities {driver_options}")
    for preference, preference_value in driver_options.items():
        preference_value = '={}'.format(preference_value) if preference_value else ''
        logger.debug(f"Added {driver_name} argument: {preference} = {preference_value}")
        options.add_argument('{}{}'.format(preference, _convert_property_type(preference_value)))

    return options


def add_sauce_labs_capabilities(sauce_options: dict, base_config):
    """
    This functions add sauce lab capabilities options
    :param sauce_options:
    :param base_config:
    :return:
    """
    logger.debug("Adding sauce lab capabilities")
    for preference, preference_value in dict(base_config.config.items('SauceLabsCapabilities')).items():
        logger.debug(f"Added sauce options: {preference} = {preference_value}")
        sauce_options[preference] = preference_value
    return sauce_options


def add_perfecto_capabilities(base_config):
    """
    This functions add perfecto capabilities options
    :param base_config:
    :return:
    """
    logger.debug("Adding perfecto capabilities")
    perfecto_options = {}
    for preference, preference_value in dict(base_config.config.items('PerfectoCapabilities')).items():
        logger.debug(f"Added perfecto options: {preference} = {preference_value}")
        perfecto_options[preference] = preference_value
    return perfecto_options
