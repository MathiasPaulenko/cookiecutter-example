# -*- coding: utf-8 -*-
"""
File containing the Driver wrapper, where the initial configuration of the driver pool selected by the run is done.
"""
import os
import logging
import screeninfo

from arc.core.config_manager import CustomConfigParser
from arc.core.driver.driver_manager import DriverManager
from arc.core.driver.driver_setup import SetupDriver
from arc.contrib.utilities import get_valid_filename, Utils
from arc.core.test_method.exceptions import TalosDriverError

logger = logging.getLogger(__name__)


class DriverWrapper(object):
    """
    Execution wrapper class and driver configuration.
    """
    driver = None
    config = CustomConfigParser()
    utils = None
    app_strings = None
    session_id = None
    server_type = None
    remote_node = None
    remote_node_video_enabled = False
    config_properties_filenames = None
    visual_baseline_directory = None
    baseline_name = None

    def __init__(self):
        if not DriverManager.is_empty():
            default_wrapper = DriverManager.get_default_wrapper()
            self.config = default_wrapper.config.deepcopy()
            self.config_properties_filenames = default_wrapper.config_properties_filenames
            self.visual_baseline_directory = default_wrapper.visual_baseline_directory
            self.baseline_name = default_wrapper.baseline_name

        self.utils = Utils(self)
        DriverManager.add_wrapper(self)

    def configure_properties(self, tc_config_prop_filenames=None, behave_properties=None):
        """
        This function configures the properties file settings and Behave properties.
        :param tc_config_prop_filenames:
        :param behave_properties:
        :return:
        """
        logger.debug("Setup driver properties and behave properties")
        prop_filenames = DriverManager.get_configured_value(
            'Config_prop_filenames', tc_config_prop_filenames, 'properties.cfg;local-properties.cfg'
        )
        prop_filenames = [os.path.join(DriverManager.config_directory, filename) for filename in
                          prop_filenames.split(';')]
        prop_filenames = ';'.join(prop_filenames)

        if self.config_properties_filenames != prop_filenames:
            self.config = CustomConfigParser.get_config_from_file(prop_filenames)
            self.config_properties_filenames = prop_filenames

        self.config.update_properties(os.environ)

        if behave_properties:
            self.config.update_properties(behave_properties)

    def configure_visual_baseline(self):
        """
        This function configure visual testing baseline depending on the properties' configuration.
        :return:
        """
        baseline_name = self.config.get_optional('VisualTests', 'baseline_name', '{Driver_type}')
        logger.debug(f"Visual Testing baseline name: {baseline_name}")
        for section in self.config.sections():
            for option in self.config.options(section):
                option_value = self.config.get(section, option)
                baseline_name = baseline_name.replace('{{{0}_{1}}}'.format(section, option), option_value)

        if self.baseline_name != baseline_name:
            self.baseline_name = baseline_name
            self.visual_baseline_directory = os.path.join(
                DriverManager.visual_baseline_directory, get_valid_filename(baseline_name)
            )

    def update_visual_baseline(self):
        """
        This function update visual testing baseline from baseline name configured.
        :return:
        """
        if '{PlatformVersion}' in self.baseline_name:
            try:
                platform_version = self.driver.desired_capabilities['platformVersion']
            except KeyError:
                platform_version = None
            self.baseline_name = self.baseline_name.replace('{PlatformVersion}', str(platform_version))
            self.visual_baseline_directory = os.path.join(DriverManager.visual_baseline_directory,
                                                          self.baseline_name)

        if '{Version}' in self.baseline_name:
            try:
                split_version = self.driver.desired_capabilities['version'].split('.')
                version = '.'.join(split_version[:2])
            except KeyError:
                version = None
            self.baseline_name = self.baseline_name.replace('{Version}', str(version))
            self.visual_baseline_directory = os.path.join(DriverManager.visual_baseline_directory,
                                                          self.baseline_name)

        if '{RemoteNode}' in self.baseline_name:
            self.baseline_name = self.baseline_name.replace('{RemoteNode}', str(self.remote_node))
            self.visual_baseline_directory = os.path.join(DriverManager.visual_baseline_directory,
                                                          self.baseline_name)

    def configure(self, tc_config_files, is_selenium_test=True, behave_properties=None):
        """
        This function configure driver manager.
        :param tc_config_files:
        :param is_selenium_test:
        :param behave_properties:
        :return:
        """
        DriverManager.configure_common_directories(tc_config_files)

        self.configure_properties(tc_config_files.config_properties_filenames, behave_properties)

        if is_selenium_test:
            logger.debug("Running Selenium tests")
            driver_info = self.config.get('Driver', 'type')
            DriverManager.configure_visual_directories(driver_info)
            self.configure_visual_baseline()

    def connect(self, maximize=True, scenario=None):
        """
        This function open driver depending on its type.
        :param maximize:
        :param scenario:
        :return:
        """
        if not self.config.get('Driver', 'type') or self.config.get('Driver', 'type') in [
            'backend', 'no_driver', 'host', 'service', 'api'
        ]:
            return None

        self.driver = SetupDriver(self.config, self.utils, scenario=scenario).create_driver()
        self.session_id = self.driver.session_id
        logger.debug(f"Driver session id: {self.session_id}")
        self.server_type, self.remote_node = self.utils.get_remote_node()
        logger.debug(f"Driver server type: {self.server_type}")
        if self.server_type == 'grid':
            logger.debug("Running in selenium grid server type")
            self.remote_node_video_enabled = self.utils.is_remote_video_enabled(self.remote_node)
        else:
            self.remote_node_video_enabled = True if self.server_type in ['ggr', 'selenoid'] else False

        if self.is_mobile_test() and not self.is_web_test() and \
                self.config.getboolean_optional('Driver', 'appium_app_strings'):
            self.app_strings = self.driver.app_strings()

        if self.is_maximizable():
            logger.debug('Maximising browser window')
            bounds_x, bounds_y = self.get_config_window_bounds()
            self.driver.set_window_position(bounds_x, bounds_y)
            logger.debug('Window bounds: %s x %s', bounds_x, bounds_y)

            if maximize:
                window_width = self.config.get_optional('Driver', 'window_width')
                window_height = self.config.get_optional('Driver', 'window_height')
                if window_width and window_height:
                    self.driver.set_window_size(window_width, window_height)
                else:
                    self.driver.maximize_window()

        window_size = self.utils.get_window_size()
        logger.debug('Window size: %s x %s', window_size['width'], window_size['height'])

        self.update_visual_baseline()
        self.utils.discard_logcat_logs()
        if self.config.get('Driver', 'type') != 'ios':
            self.utils.set_implicitly_wait()

        return self.driver

    def get_config_window_bounds(self):
        """
        This function get window bounds configured
        :return:
        """
        bounds_x = int(self.config.get_optional('Driver', 'bounds_x') or 0)
        bounds_y = int(self.config.get_optional('Driver', 'bounds_y') or 0)

        monitor_index = int(self.config.get_optional('Driver', 'monitor') or -1)
        if monitor_index > -1:
            try:
                monitor = screeninfo.get_monitors()[monitor_index]
                bounds_x += monitor.x
                bounds_y += monitor.y
            except NotImplementedError:
                msg = "Current environment does not support get_monitors"
                logger.exception(msg)
                raise TalosDriverError(msg)

        return bounds_x, bounds_y

    def is_android_test(self):
        """
        This function returns True if it is an Android test.
        :return:
        """
        driver_name = self.config.get('Driver', 'type').split('-')[0]
        return driver_name == 'android'

    def is_ios_test(self):
        """
        This function returns True if it is an iOS test.
        :return:
        """
        driver_name = self.config.get('Driver', 'type').split('-')[0]
        return driver_name in ('ios', 'iphone')

    def is_mac_test(self):
        """
        This function returns True if it is an iOS test.
        :return:
        """
        driver_name = self.config.get('Driver', 'type').split('-')[0]
        return driver_name == 'safari'

    def is_mobile_test(self):
        """
        This function returns True if it is a mobile test.
        :return:
        """
        return self.is_android_test() or self.is_ios_test()

    def is_web_test(self):
        """
        This function returns True if it is a web test.
        :return:
        """
        appium_browser_name = self.config.get_optional('AppiumCapabilities', 'browserName')
        return not self.is_mobile_test() or appium_browser_name not in (None, '')

    def is_android_web_test(self):
        """
        This function returns True if it is an Android web test.
        :return:
        """
        return self.is_android_test() and self.is_web_test()

    def is_ios_web_test(self):
        """
        This function returns True if it is a iOS web test.
        :return:
        """
        return self.is_ios_test() and self.is_web_test()

    def is_maximizable(self):
        """
        This function returns true if the driver is maximizable, mobile tests cannot be maximised.
        :return:
        """
        return not self.is_mobile_test()

    def should_reuse_driver(self, scope, test_passed, context=None):
        """
        This function enable reuse driver if enabled.
        :param scope:
        :param test_passed:
        :param context:
        :return:
        """
        reuse_driver = self.config.getboolean_optional('Driver', 'reuse_driver')
        reuse_driver_session = self.config.getboolean_optional('Driver', 'reuse_driver_session')
        restart_driver_after_failure = (
                self.config.getboolean_optional('Driver', 'restart_driver_after_failure') or
                self.config.getboolean_optional('Driver', 'restart_driver_fail')
        )

        logger.debug("Reuse driver configuration:")
        logger.debug(f"Reuse driver: {reuse_driver}")
        logger.debug(f"Reuse driver session: {reuse_driver_session}")
        logger.debug(f"Restart driver after failure: {restart_driver_after_failure}")

        if context and scope == 'function':
            reuse_driver = reuse_driver or (
                    hasattr(context, 'reuse_driver_from_tags')
                    and context.pytalos.reuse_driver_from_tags
            )
        return (((reuse_driver and scope == 'function') or (reuse_driver_session and scope != 'session'))
                and (test_passed or not restart_driver_after_failure))

    def get_driver_platform(self):
        """
        This function return driver platform.
        :return:
        """
        platform = ''
        if 'platform' in self.driver.desired_capabilities:
            platform = self.driver.desired_capabilities['platform']
        elif 'platformName' in self.driver.desired_capabilities:
            platform = self.driver.desired_capabilities['platformName']

        logger.debug(f"Driver platform: {platform}")
        return platform
