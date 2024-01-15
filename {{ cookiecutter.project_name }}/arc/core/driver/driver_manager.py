# -*- coding: utf-8 -*-
"""
File with driver management classes ...
Core of the operation, configuration and actions related to Selenium and the execution driver.
"""
import datetime
import logging
import os

from arc.core.config_manager import ConfigFiles
from arc.integrations.selenoid import Selenoid
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


class DriverManager(object):
    """
    This class manages the drivers used in the execution of Talos tests.
    """
    driver_wrappers = []
    config_directory = None
    output_directory = None
    screenshots_directory = None
    screenshots_number = None
    videos_directory = None
    logs_directory = None
    videos_number = None
    visual_baseline_directory = None
    visual_output_directory = None
    visual_number = None

    @classmethod
    def is_empty(cls):
        """
        Check if driver wrapper is empty
        :return:
        """
        return len(cls.driver_wrappers) == 0

    @classmethod
    def get_default_wrapper(cls):
        """
        Get default driver wrapper if empty
        :return:
        """
        if cls.is_empty():
            from arc.core.driver.driver_wrapper import DriverWrapper
            DriverWrapper()
        return cls.driver_wrappers[0]

    @classmethod
    def add_wrapper(cls, driver_wrapper):
        """
        Add driver wrapper
        :param driver_wrapper:
        :return:
        """
        cls.driver_wrappers.append(driver_wrapper)

    @classmethod
    def capture_screenshots(cls, name):
        """
        Capture screenshot of driver
        :param name:
        :return:
        """
        screenshot_name = '{}_driver{}' if len(cls.driver_wrappers) > 1 else '{}'
        driver_index = 1
        for driver_wrapper in cls.driver_wrappers:
            if not driver_wrapper.driver:
                continue
            try:
                driver_wrapper.utils.capture_screenshot(screenshot_name.format(name, driver_index))
            except Exception as ex:
                logger.warning("Capture warning: %s" % ex)
            driver_index += 1

    @classmethod
    def connect_default_driver_wrapper(cls, config_files=None):
        """
        Link default driver wrapper and connect from config file if passed
        :param config_files:
        :return:
        """
        driver_wrapper = cls.get_default_wrapper()
        if not driver_wrapper.driver:
            config_files = DriverManager.initialize_config_files(config_files)
            driver_wrapper.configure(config_files)
            driver_wrapper.connect()
        logger.debug("Default driver wrapper connected")
        return driver_wrapper

    @classmethod
    def close_drivers(cls, scope, test_name, test_passed=True, context=None):
        """
        Close current driver
        :param scope:
        :param test_name:
        :param test_passed:
        :param context:
        :return:
        """
        if scope == 'function':
            if not test_passed:
                cls.capture_screenshots(test_name)
            if context and hasattr(context, 'dyn_env'):
                context.pytalos.dyn_env.execute_after_scenario_steps(context)
            cls.save_all_webdriver_logs(test_name, test_passed)

        reuse_driver = cls.get_default_wrapper().should_reuse_driver(scope, test_passed, context)
        logger.debug("Stopping current drivers from driver manager")
        cls.stop_drivers(reuse_driver)
        cls.download_videos(test_name, test_passed, reuse_driver)
        cls.save_all_ggr_logs(test_name, test_passed)
        logger.debug("Removing current drivers session from driver manager")
        cls.remove_drivers(reuse_driver)

    @classmethod
    def stop_drivers(cls, maintain_default=False):
        """
        Stop the current driver running
        :param maintain_default:
        :return:
        """
        driver_wrappers = cls.driver_wrappers[1:] if maintain_default else cls.driver_wrappers
        close_driver = Settings.PYTALOS_RUN.get('close_webdriver')
        for driver_wrapper in driver_wrappers:
            if not driver_wrapper.driver:
                continue
            try:
                if close_driver:
                    driver_wrapper.driver.quit()
            except Exception as e:
                logger.warning(f"Capture exceptions to avoid errors in teardown method due to session timeouts: {e}")

    @classmethod
    def download_videos(cls, name, test_passed=True, maintain_default=False):
        """
        Download remote video recorded if enabled and the server is selenoid
        :param name:
        :param test_passed:
        :param maintain_default:
        :return:
        """
        driver_wrappers = cls.driver_wrappers[1:] if maintain_default else cls.driver_wrappers
        video_name = '{}_driver{}' if len(driver_wrappers) > 1 else '{}'
        video_name = video_name if test_passed else 'error_{}'.format(video_name)
        driver_index = 1

        for driver_wrapper in driver_wrappers:
            if not driver_wrapper.driver:
                continue
            try:
                if (not test_passed or driver_wrapper.config.getboolean_optional('Server', 'video_enabled', False)) \
                        and driver_wrapper.remote_node_video_enabled:
                    if driver_wrapper.server_type in ['ggr', 'selenoid']:
                        from arc.contrib.utilities import get_valid_filename
                        name = get_valid_filename(video_name.format(name, driver_index))
                        Selenoid(driver_wrapper).download_session_video(name)
                    elif driver_wrapper.server_type == 'grid':
                        driver_wrapper.utils.download_remote_video(driver_wrapper.remote_node,
                                                                   driver_wrapper.session_id,
                                                                   video_name.format(name, driver_index))
            except Exception as exc:
                logger.warning(f"Error downloading videos: {exc}")
            driver_index += 1

    @classmethod
    def remove_drivers(cls, maintain_default=False):
        """
        Remove current driver session
        :param maintain_default:
        :return:
        """
        close_driver = Settings.PYTALOS_RUN.get('close_webdriver')
        if close_driver:
            cls.driver_wrappers = cls.driver_wrappers[0:1] if maintain_default else []

    @classmethod
    def save_all_webdriver_logs(cls, test_name, test_passed):
        """
        Save all webdriver log generated
        :param test_name:
        :param test_passed:
        :return:
        """
        log_name = '{} [driver {}]' if len(cls.driver_wrappers) > 1 else '{}'
        driver_index = 1
        for driver_wrapper in cls.driver_wrappers:
            if not driver_wrapper.driver or driver_wrapper.server_type in ['ggr', 'selenoid']:
                continue
            if driver_wrapper.config.getboolean_optional('Server', 'logs_enabled') or not test_passed:
                try:
                    driver_wrapper.utils.save_webdriver_logs(log_name.format(test_name, driver_index))
                except Exception as exc:
                    logger.warning(f"Error downloading webdriver logs: {exc}")
            driver_index += 1

    @classmethod
    def save_all_ggr_logs(cls, test_name, test_passed):
        """
        Save all ggr logs generated
        :param test_name:
        :param test_passed:
        :return:
        """
        log_name = '{} [driver {}]' if len(cls.driver_wrappers) > 1 else '{}'
        driver_index = 1
        for driver_wrapper in cls.driver_wrappers:
            if not driver_wrapper.driver or driver_wrapper.server_type not in ['ggr', 'selenoid']:
                continue
            try:
                if driver_wrapper.config.getboolean_optional('Server', 'logs_enabled') or not test_passed:
                    from arc.contrib.utilities import get_valid_filename
                    name = get_valid_filename(log_name.format(test_name, driver_index))
                    Selenoid(driver_wrapper).download_session_log(name)
            except Exception as exc:
                logger.warning(f"Error downloading GGR logs: {exc}")
            driver_index += 1

    @staticmethod
    def get_configured_value(system_property_name, specific_value, default_value):
        """
        Get configured value from default and system property
        :param system_property_name:
        :param specific_value:
        :param default_value:
        :return:
        """
        try:
            return os.environ[system_property_name]
        except KeyError:
            return specific_value if specific_value else default_value

    @classmethod
    def configure_common_directories(cls, tc_config_files):
        """
        Configure common directories like output and driver properties cfg
        :param tc_config_files:
        :return:
        """
        if cls.config_directory is None:
            config_directory = cls.get_configured_value('Config_directory', tc_config_files.config_directory, 'conf')
            logger.debug(f"Driver config directory set: {config_directory}")
            prop_filenames = cls.get_configured_value(
                'Config_prop_filenames', tc_config_files.config_properties_filenames, 'properties.cfg'
            )
            logger.debug(f"Properties filenames founded: {prop_filenames}")
            cls.config_directory = cls._find_parent_directory(config_directory, prop_filenames.split(';')[0])

            cls.output_directory = cls.get_configured_value(
                'Output_directory', tc_config_files.output_directory, 'output'
            )

            if not os.path.isabs(cls.output_directory):
                cls.output_directory = os.path.join(os.path.dirname(cls.config_directory), cls.output_directory)
            if not os.path.exists(cls.output_directory):
                try:
                    os.makedirs(cls.output_directory)
                except FileExistsError:
                    pass

            default_baseline = os.path.join(cls.output_directory, 'visualtests', 'baseline')
            logger.debug(f"Default baseline configured: {default_baseline}")
            cls.visual_baseline_directory = cls.get_configured_value(
                'Visual_baseline_directory', tc_config_files.visual_baseline_directory, default_baseline
            )
            if not os.path.isabs(cls.visual_baseline_directory):
                cls.visual_baseline_directory = os.path.join(
                    os.path.dirname(cls.config_directory), cls.visual_baseline_directory
                )

    @staticmethod
    def get_default_config_directory():
        """
        Get default driver config directory
        :return:
        """
        test_path = os.path.abspath("settings")
        return os.path.join(test_path, 'conf')

    @staticmethod
    def _find_parent_directory(directory, filename):
        """
        Find driver properties parent directory
        :param directory:
        :param filename:
        :return:
        """
        parent_directory = directory
        absolute_directory = '.'
        while absolute_directory != os.path.abspath(parent_directory):
            absolute_directory = os.path.abspath(parent_directory)
            if os.path.isfile(os.path.join(absolute_directory, filename)):
                return absolute_directory
            if os.path.isabs(parent_directory):
                parent_directory = os.path.join(
                    os.path.dirname(parent_directory), '../..', os.path.basename(parent_directory)
                )
                logger.debug(f"Driver properties parent directory: {parent_directory}")
            else:
                parent_directory = os.path.join('../..', parent_directory)
                logger.debug(f"Driver properties parent directory: {parent_directory}")
        return os.path.abspath(directory)

    @classmethod
    def configure_visual_directories(cls, driver_info):
        """
        This function configure visual testing directories if enabled.
        :param driver_info:
        :return:
        """
        if cls.screenshots_directory is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
            folder_name = '%s_%s' % (date, driver_info) if driver_info else date
            from arc.contrib.utilities import get_valid_filename
            folder_name = get_valid_filename(folder_name)
            # This line was corrected because it was stepping on the output directory
            # cls.output_directory = os.path.abspath("output/")
            visual_directory = os.path.abspath("output/")  # noqa
            cls.screenshots_directory = os.path.join(visual_directory, 'screenshots', folder_name)
            cls.screenshots_number = 1
            cls.videos_directory = os.path.join(visual_directory, 'videos', folder_name)
            cls.logs_directory = os.path.join(visual_directory, 'logs', folder_name)
            cls.videos_number = 1
            cls.visual_output_directory = os.path.join(visual_directory, 'visualtests')
            cls.visual_number = 1
            logger.debug("Visual Testing directories configured:")
            logger.debug(f"Screenshot directory: {cls.screenshots_directory}")
            logger.debug(f"Screenshot number: {cls.screenshots_number}")
            logger.debug(f"Videos directory: {cls.videos_directory}")
            logger.debug(f"Video number: {cls.videos_number}")
            logger.debug(f"Log directory: {cls.logs_directory}")
            logger.debug(f"Visual output directory: {cls.visual_output_directory}")
            logger.debug(f"Visual number: {cls.visual_number}")

    @staticmethod
    def initialize_config_files(tc_config_files=None):
        """
        This function initialize properties cfg driver files
        :param tc_config_files:
        :return:
        """
        if tc_config_files is None:
            tc_config_files = ConfigFiles()

        env = DriverManager.get_configured_value('Config_environment', None, None)
        logger.debug(f"Environment form driver manager configured: {env}")
        if env:
            prop_filenames = tc_config_files.config_properties_filenames
            new_prop_filenames_list = prop_filenames.split(';') if prop_filenames else ['properties.cfg']
            base, ext = os.path.splitext(new_prop_filenames_list[0])
            new_prop_filenames_list.append('{}-{}{}'.format(env, base, ext))
            new_prop_filenames_list.append('local-{}-{}{}'.format(env, base, ext))
            tc_config_files.set_config_properties_filenames(*new_prop_filenames_list)

            output_log_filename = tc_config_files.output_log_filename
            base, ext = os.path.splitext(output_log_filename) if output_log_filename else ('pytalos', '.log')
            tc_config_files.set_output_log_filename('{}_{}{}'.format(base, env, ext))

        return tc_config_files

    @classmethod
    def _empty_pool(cls):
        """
        Clean driver manager configuration and set default values.
        :return:
        """
        cls.driver_wrappers = []
        cls.config_directory = None
        cls.output_directory = None
        cls.screenshots_directory = None
        cls.screenshots_number = None
        cls.videos_directory = None
        cls.logs_directory = None
        cls.videos_number = None
        cls.visual_output_directory = None
        cls.visual_number = None
        logger.debug("Driver manager configurations cleared")
