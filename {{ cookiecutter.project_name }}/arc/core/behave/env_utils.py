# -*- coding: utf-8 -*-
"""
Classes and functionalities of utilities used in the environment.
"""
import copy
import datetime
import json
import logging
import os
import time
import traceback
import warnings
from configparser import NoSectionError, NoOptionError

import requests
import yaml
from behave.model import Feature
from colorama import Fore
from pkg_resources import parse_version

from arc.contrib.accessibility.axe_utils import write_results
from arc.contrib.accessibility.axe_wrapper import AxeWrapper
from arc.contrib.tools.formatters import replace_chars
from arc.contrib.tools.repository import Repository
from arc.contrib.utilities import get_valid_filename, set_test_default_data
from jinja2 import Environment, FileSystemLoader, select_autoescape

from arc.core.behave.template_var import replace_template_var
from arc.core.driver.driver_install import InstallDriver
from arc.core.test_method.exceptions import TalosConfigurationError, TalosGenerationReportError, TalosRunError
from arc.integrations.alm import compress_html_report
from arc.reports.error.create_report import ErrorReport
from arc.reports.html.utils import (
    get_datetime_from_timestamp,
    get_duration, json_pretty, parse_content_type,
    transform_image_to_webp, get_short_name, transform_accessibility_image_to_webp, BASE_DIR
)
from arc.settings.settings_manager import Settings
from arc.web.app.utils import print_portal_console, send_alert_portal
from arc.web.db.db_api import get_db, set_settings_config
from arc.web.models.models import Execution, StatusType, ExecutionFeature, ExecutionScenario, ScenarioType, \
    ExecutionStep
try:
    from settings import settings
except (ModuleNotFoundError, ImportError):
    from arc.settings import settings
from arc.contrib.utilities import load_translation
from arc.contrib.host import host
from arc.contrib.host.utils import get_host_screenshot
from arc.core import constants
from arc.core.config_manager import ConfigFiles
from arc.core.behave.context_utils import PyTalosContext
from arc.core.driver.driver_manager import DriverManager
from arc.integrations.jira import Jira
from arc.integrations.elasticsearch import Elasticsearch
from arc.page_elements import PageElement
from arc.core.test_method.visual_test import VisualTest
from arc.reports import log_generation, html_reporter
from arc.reports import generate_json
from arc.reports.video.recorder import Recorder
from test.helpers import hooks
from arc.web.app import hooks as portal_hooks
from arc.reports.doc.create_report import CreateDOC
from arc.reports.pdf.create_report import CreatePDF
from arc.talos_virtual.core.contrib.mountebank.mountebank import MountebankWrapper
from arc.talos_virtual.core.context import TalosVirtual
from arc.talos_virtual.core.env_utils import create_dict_imposter
from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry
from arc.contrib.tools.files import get_files_to_edit
from arc.settings.settings_manager import Settings


warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class DynamicEnvironment:
    """
    Module of actions to dynamize the environment.
    """
    actions = None

    def __init__(self, **kwargs):
        self.show = kwargs.get("show", True)
        self.init_actions()
        self.scenario_counter = 0
        self.feature_error = False
        self.scenario_error = False

    def init_actions(self):
        """
        Initialization of environmental actions.
        """
        self.actions = {
            constants.ACTIONS_BEFORE_FEATURE: [],
            constants.ACTIONS_BEFORE_SCENARIO: [],
            constants.ACTIONS_AFTER_SCENARIO: [],
            constants.ACTIONS_AFTER_FEATURE: []
        }

    def get_label_from_description(self, row, label):
        """
        Return label from description of the actions
        """
        for action_label in self.actions:
            if row.lower().find(action_label) >= 0:
                label = action_label
        logger.debug(f"Getting label from description: {label}")
        return label

    def get_steps_from_feature_description(self, description):  # noqa
        """
        Get steps from the description of the features.
        """
        self.init_actions()
        label = constants.EMPTY
        for row in description:
            if label != constants.EMPTY:
                if "#" in row:
                    row = row[0:row.find("#")].strip()

                if any(row.startswith(x) for x in constants.KEYWORDS):
                    self.actions[label].append(row)
                elif row.find(constants.TABLE_SEPARATOR) >= 0:
                    self.actions[label][-1] = "%s\n      %s" % (self.actions[label][-1], row)
                else:
                    label = constants.EMPTY
            label = self.get_label_from_description(row, label)
            logger.debug(f"Get steps from the description of the features: {label}")

    @staticmethod
    def __remove_prefix(step):
        step_length = len(step)
        for k in constants.KEYWORDS:
            step = step.lstrip(k)
            if len(step) < step_length:
                break
        logger.debug(f"Step prefix removed: {step}")
        return step

    @staticmethod
    def __print_step(step):
        step_list = step.split(u'\n')
        for s in step_list:
            logger.info(u'    %s' % repr(s).replace("u'", "").replace("'", ""))

    def __execute_steps_by_action(self, context, action):
        if len(self.actions[action]) > 0:
            if action in [constants.ACTIONS_BEFORE_FEATURE, constants.ACTIONS_BEFORE_SCENARIO,
                          constants.ACTIONS_AFTER_FEATURE]:
                logger.info('\n')
                if action == constants.ACTIONS_BEFORE_SCENARIO:
                    self.scenario_counter += 1
                    logger.info(
                        f"  ------------------ Scenario Number: {self.scenario_counter} ------------------")
                logger.info('  %s:' % action)
            for item in self.actions[action]:
                self.scenario_error = False
                try:
                    self.__print_step(item)
                    context.execute_steps(u'''%s%s''' % (constants.GIVEN_PREFIX, self.__remove_prefix(item)))
                    logger.debug(u'step defined in pre-actions: %s' % repr(item))
                except Exception as exc:
                    if action in [constants.ACTIONS_BEFORE_FEATURE]:
                        self.feature_error = True
                    elif action in [constants.ACTIONS_BEFORE_SCENARIO]:
                        self.scenario_error = True
                    logger.error(exc)
                    self.error_exception = exc
                    break

    def reset_error_status(self):
        """
        Method of resetting the error status of the features and scenario.
        """
        try:
            return self.feature_error or self.scenario_error
        finally:
            self.feature_error = False
            self.scenario_error = False

    def execute_before_feature_steps(self, context):
        """
        Execution of before feature hooks.
        :param context:
        """
        self.__execute_steps_by_action(context, constants.ACTIONS_BEFORE_FEATURE)

        if context.pytalos.dyn_env.feature_error:
            context.feature.mark_skipped()

    def execute_before_scenario_steps(self, context):
        """
        Execution of before scenario hooks.
        :param context:
        """
        if not self.feature_error:
            self.__execute_steps_by_action(context, constants.ACTIONS_BEFORE_SCENARIO)

        if context.pytalos.dyn_env.scenario_error:
            context.scenario.mark_skipped()

    def execute_after_scenario_steps(self, context):
        """
        Execution of after scenario hooks.
        :param context:
        """
        if not self.feature_error and not self.scenario_error:
            self.__execute_steps_by_action(context, constants.ACTIONS_AFTER_SCENARIO)

        if self.reset_error_status():
            context.scenario.reset()
            context.pytalos.dyn_env.fail_first_step_precondition_exception(context.scenario)

    def execute_after_feature_steps(self, context):
        """
        Execution of after feature hooks.
        :param context:
        """
        if not self.feature_error:
            self.__execute_steps_by_action(context, constants.ACTIONS_AFTER_FEATURE)

        if self.reset_error_status():
            context.feature.reset()
            for scenario in context.feature.walk_scenarios():
                context.pytalos.dyn_env.fail_first_step_precondition_exception(scenario)

    def fail_first_step_precondition_exception(self, scenario):
        """
        Method that fails the precondition in the first step.
        :param scenario:
        :return:
        """
        try:
            import behave
            if parse_version(behave.__version__) < parse_version('1.2.6'):
                status = 'failed'
            else:
                status = behave.model_core.Status.failed  # noqa
        except ImportError as exc:
            logger.error(exc)
            raise

        scenario.steps[0].status = status
        scenario.steps[0].exception = Exception("Preconditions failed")
        scenario.steps[0].error_message = self.error_exception.message  # noqa


def configure_properties_from_tags(context, scenario):
    """
    Configuration of properties according to labels that have the scenario in execution.
    :param context:
    :param scenario:
    """
    if 'no_reset_app' in scenario.tags:
        os.environ["AppiumCapabilities_noReset"] = 'true'
        os.environ["AppiumCapabilities_fullReset"] = 'false'
        logger.debug("Found the no_reset_app tag in the scenario")
    elif 'reset_app' in scenario.tags:
        os.environ["AppiumCapabilities_noReset"] = 'false'
        os.environ["AppiumCapabilities_fullReset"] = 'false'
        logger.debug("Found the reset_app tag in the scenario")

    elif 'full_reset_app' in scenario.tags:
        os.environ["AppiumCapabilities_noReset"] = 'false'
        os.environ["AppiumCapabilities_fullReset"] = 'true'
        logger.debug("Found the full_reset_app tag in the scenario")

    if 'reset_driver' in scenario.tags:
        DriverManager.stop_drivers()
        DriverManager.download_videos('multiple tests', context.pytalos.global_status['test_passed'])
        DriverManager.save_all_ggr_logs('multiple tests', context.pytalos.global_status['test_passed'])
        DriverManager.remove_drivers()
        context.pytalos.global_status['test_passed'] = True
        logger.debug("Found the reset_driver tag in the scenario")

    if 'android_only' in scenario.tags and context.pytalos.driver_wrapper.is_ios_test():
        scenario.skip('Android scenario')
        logger.debug("Found the android_only tag in the scenario")
    elif 'ios_only' in scenario.tags and context.pytalos.driver_wrapper.is_android_test():
        scenario.skip('iOS scenario')
        logger.debug("Found the ios_only tag in the scenario")


def utils_before_execution():
    """
    Useful functions that are executed before the execution of the tests.
    """
    dev_mode = False
    if hasattr(settings, 'DEV_MODE'):
        dev_mode = settings.DEV_MODE
    if os.environ.get('EXECUTION_TYPE') == 'Portal':
        set_settings_config()
    if dev_mode is False:
        valid_parameter("application", 2)
        valid_parameter("business_area", 2)
        valid_parameter("entity", 2)
        valid_parameter("user_code", 2)


def valid_parameter(parameter, length):
    """
    Parameter validation function of Talos configurations.
    :param parameter:
    :param length:
    """
    valid = False
    msg_error = "Fields: application, business_area, entity, user_code which are in settings in PROJECT_INFO " \
                "section are required. "
    if parameter in Settings.PROJECT_INFO.get():
        if isinstance(Settings.PROJECT_INFO.get(parameter), str):
            if len(Settings.PROJECT_INFO.get(parameter)) >= length:
                if not str(Settings.PROJECT_INFO.get(parameter)).startswith(" "):
                    valid = True
                else:
                    msg_error += f"{parameter} starts with a space. "
            else:
                msg_error += f"{parameter} has a length less than {length} characters. "
        else:
            msg_error += f"{parameter} is not type string. "
    else:
        msg_error += f"{parameter} was not found in PROJECT_INFO section. "

    if not valid:
        from arc.settings.doc_urls import PROJECT_INFO_FIELD
        msg_error += f"\nFor more details see:  {PROJECT_INFO_FIELD}"
        logger.exception(msg_error, exc_info=False)
        if os.environ.get('EXECUTION_TYPE') == 'Portal':
            send_alert_portal(msg_error)
            print_portal_console(msg_error)
        raise TalosConfigurationError(msg_error)


from arc.core.behave.config_data import get_profile_data
from arc.core.behave.template_var import get_global


def save_profile_dict(repository):
    final_dict = {}
    files_profiles = get_profile_data()
    files_repositories = repository.data
    files_repositories['elements'] = repository.elements
    files_repositories['literals'] = repository.literals
    final_dict['profiles'] = files_profiles
    final_dict['repositories'] = files_repositories
    template_var = get_global()
    template_var.update(final_dict)


def utils_before_all(context):
    """
    Useful functions that are executed before all the tests.
    :param context:
    """
    set_test_default_data()
    env = context.config.userdata.get('Config_environment')
    context.pytalos = PyTalosContext(context)

    if env:
        os.environ['Config_environment'] = env

    if not hasattr(context, 'config_files'):
        logger.debug("Adding config_files instance to context.pytalos")
        context.pytalos.config_files = ConfigFiles()
    logger.debug("Initializing configuration files")
    context.pytalos.config_files = DriverManager.initialize_config_files(context.pytalos.config_files)

    if not context.pytalos.config_files.config_directory:
        logger.debug("Setting directory settings")
        context.pytalos.config_files.set_config_directory(DriverManager.get_default_config_directory())

    if Settings.PYTALOS_PROFILES.get('repositories') is True:
        logger.debug("Setting repository data")
        context.repositories = Repository()
        save_profile_dict(context.repositories)

    logger.debug("Creating core wrapper")
    context.pytalos.global_status = {'test_passed': True}
    create_wrapper(context)
    logger.debug("Creating dynamic environment")
    context.pytalos.dyn_env = DynamicEnvironment()


def utils_before_feature(context, feature):
    """
    Useful functions that are executed before features.
    :param context:
    :param feature:
    """

    check_scenarios_order(feature)

    context.pytalos.global_status = {'test_passed': True}
    no_driver = 'no_driver' in feature.tags
    context.pytalos.reuse_driver_from_tags = 'reuse_driver' in feature.tags

    if context.pytalos_config.getboolean_optional('Driver', 'reuse_driver') or context.pytalos.reuse_driver_from_tags:
        logger.info("Starting reuse driver")
        start_driver(context, no_driver)

    context.pytalos.dyn_env.get_steps_from_feature_description(feature.description)
    context.pytalos.dyn_env.execute_before_feature_steps(context)


def utils_before_scenario(context, scenario):
    """
    Useful functions that are executed before features.
    :param context:
    :param scenario:
    """
    configure_properties_from_tags(context, scenario)
    no_driver = 'no_driver' in scenario.tags or 'no_driver' in scenario.feature.tags
    logger.info("Starting driver")
    start_driver(context, no_driver)
    add_assert_screenshot_methods(scenario)
    logger.info(f"Running scenario: {scenario.name}")
    context.pytalos.dyn_env.execute_before_scenario_steps(context)


def utils_after_scenario(context, scenario, status):
    """
    Useful functions that are executed after scenario.
    :param context:
    :param scenario:
    :param status:
    """
    if status == 'skipped':
        logger.info(f"The scenario {scenario.name} has skipped")
        return
    elif status == 'passed':
        logger.info(f"The scenario {scenario.name} has passed")
    else:
        logger.error(f"The scenario {scenario.name} has failed")
        context.pytalos.global_status['test_passed'] = False

    logger.info("Closing driver in scope function")
    DriverManager.close_drivers(
        scope='function',
        test_name=scenario.name,
        test_passed=status == 'passed',
        context=context
    )


def utils_after_feature(context, feature):
    """
    Useful functions that are executed after feature.
    :param context:
    :param feature:
    :return:
    """
    context.pytalos.dyn_env.execute_after_feature_steps(context)
    logger.info("Closing driver in scope module")

    DriverManager.close_drivers(
        scope='module',
        test_name=feature.name,
        test_passed=context.pytalos.global_status['test_passed']
    )


def utils_after_all(context):
    """
    Useful functions that are executed after all.
    :param context:
    :return:
    """
    logger.info("Closing driver in scope session")
    try:
        if context.pytalos_config.get('Server', 'enabled').lower() == 'true' \
                and context.pytalos_config.get('Server', 'type').lower() == 'saucelabs':
            sauce_labs_set_test_status(context)
    except (NoSectionError, AttributeError, NoOptionError) as e:
        logger.info(e)
    DriverManager.close_drivers(
        scope='session',
        test_name='multiple_tests',
        test_passed=context.pytalos.global_status['test_passed']
    )
    update_profile_files()


def utils_after_execution():
    """
    Useful functions that are executed after execution.
    """
    dev_mode = False
    if hasattr(settings, 'DEV_MODE'):
        dev_mode = settings.DEV_MODE
    if dev_mode is False:
        try:
            logger.info('Posting information to Elastic Search')
            Elasticsearch().run()
        except (Exception,):
            logger.warning('Upload to ElasticSearch error')


def create_wrapper(context):
    """
    Method of creating the wrapper according to driver configuration.
    :param context:
    """
    context.pytalos.driver_wrapper = DriverManager.get_default_wrapper()
    context.utils = context.pytalos.driver_wrapper.utils

    try:
        behave_properties = context.config.userdata
    except AttributeError:
        behave_properties = None

    logger.debug("Configuring driver wrapper")
    context.pytalos.driver_wrapper.configure(context.pytalos.config_files, behave_properties=behave_properties)
    logger.debug("Driver wrapper configured with:")
    logger.debug(context.pytalos.config_files)
    logger.debug(behave_properties)
    context.pytalos_config = context.pytalos.driver_wrapper.config
    if config_environment := behave_properties.get('Config_environment'):
        context.config_environment = config_environment
    logger.debug(context.pytalos_config)


def connect_wrapper(context):
    """
    Connect the wrapper to the no driver session.
    :param context:
    :return:
    """
    reuse_driver_session = context.pytalos_config.getboolean_optional('Driver', 'reuse_driver_session')
    if context.pytalos.driver_wrapper.driver and reuse_driver_session:
        context.driver = context.pytalos.driver_wrapper.driver
    else:
        context.driver = context.pytalos.driver_wrapper.connect(scenario=context.scenario)

    context.pytalos.app_strings = context.pytalos.driver_wrapper.app_strings


def start_driver(context, no_driver):
    """
    Driver execution function.
    :param context:
    :param no_driver:
    """
    create_wrapper(context)
    if not no_driver:
        connect_wrapper(context)


def add_assert_screenshot_methods(scenario):
    """
    Function that adds assertion methods for screenshots for visual testing.
    :param scenario:
    """
    file_suffix = scenario.name

    def assert_screenshot_page_element(self, filename, threshold=0, exclude_elements=None, force=False):
        """
        Compare a screenshot to a page element.
        :param self:
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
            file_suffix,
            threshold,
            exclude_elements
        )

    PageElement.assert_screenshot = assert_screenshot_page_element


def enable_txt_report():
    """
    Enabling the report in txt format.
    :return:
    """
    if Settings.PYTALOS_REPORTS.get('generate_txt'):
        logger.info("TXT report enabled")
        return log_generation.ExecutionTxtLog()


def set_alm_custom_variable(context):
    """
    Setting custom alm result variable.
    :param context:
    :return:
    """
    logger.debug('Initialising ALM custom result attributes')
    context.runtime.step.result_expected = None
    context.runtime.step.obtained_result_failed = None
    context.runtime.step.obtained_result_passed = None
    context.runtime.step.obtained_result_skipped = None


def enable_json_report(scenario):
    """
    Enabling the report in json format for ALM.
    :param scenario:
    :return:
    """
    if Settings.PYTALOS_ALM.get('post_to_alm'):
        logger.info("Upload to ALM enabled")
        Settings.PYTALOS_ALM.set('generate_json', value=True)
    if Settings.PYTALOS_ALM.get('generate_json'):
        logger.info("Json ALM report enabled")
        return generate_json.GenerateJson(scenario)


def enable_host(context):
    """
    Configuring default values in host executions.
    :param context:
    :return:
    """
    if context.pytalos_config.get('Driver', 'type') == 'host':
        ws_path = context.pytalos_config.get('Driver', 'ws_path')
        cscript = context.pytalos_config.get('Driver', 'cscript_path')
        context.host = host.Host(ws_path, cscript)
        logger.debug("Host properties configured:")
        logger.debug(f"WS path: {ws_path}")
        logger.debug(f"CScript path: {cscript}")


def close_host(context):
    """
    Closes the host window if the settings option is enabled.
    :param context:
    :return:
    """
    if context.pytalos_config.get('Driver', 'type') == 'host':
        if Settings.PYTALOS_RUN.get('close_host'):
            logger.info("Closing the host window")
            context.host.close_emulator()


def config_faker():
    """
    Set faker parameters if installed.
    :return:
    """
    try:
        from faker import Faker  # noqa
        return Faker(Settings.PYTALOS_PROFILES.get('locale_fake_data'))
    except (Exception,):
        return None


def run_hooks(context, moment, extra_info=None):
    """
    Run user custom hooks
    :param context:
    :param moment:
    :param extra_info:
    :return:
    """
    logger.info(f'Running user hook: {moment}')
    try:
        if moment == 'before_execution':
            hooks.before_execution()
        elif moment == 'before_all':
            hooks.before_all(context)
        elif moment == 'after_all':
            hooks.after_all(context)
        elif moment == 'before_feature':
            hooks.before_feature(context, extra_info)
        elif moment == 'after_feature':
            hooks.after_feature(context, extra_info)
        elif moment == 'before_scenario':
            hooks.before_scenario(context, extra_info)
        elif moment == 'after_scenario':
            hooks.after_scenario(context, extra_info)
        elif moment == 'before_step':
            hooks.before_step(context, extra_info)
        elif moment == 'after_step':
            hooks.after_step(context, extra_info)
        elif moment == 'after_execution':
            hooks.after_execution()
        elif moment == 'before_reports':
            hooks.before_reports(extra_info)
        elif moment == 'before_tag':
            hooks.before_tag(context, extra_info)
        elif moment == 'after_tag':
            hooks.after_tag(context, extra_info)
    except (Exception,) as ex:
        logger.error(f"WARNING: there was an error in the hooks {moment}: {ex}")
        raise ex


def run_portal_hooks(context, moment, extra_info=None):
    """
    Run user custom hooks
    :param context:
    :param moment:
    :param extra_info:
    :return:
    """
    logger.info(f'Running user hook: {moment}')
    try:
        if os.environ.get('TALOS_PORTAL') == 'True':
            if moment == 'before_execution':
                portal_hooks.before_execution()
            elif moment == 'after_execution':
                portal_hooks.after_execution()
    except (Exception,) as ex:
        logger.error(f"WARNING: there was an error in the hooks {moment}: {ex}")
        raise ex


def generate_simple_html_reports(generate):
    """
    Generate simple html report if enabled
    :param generate:
    :return:
    """
    if generate:
        try:
            logger.info("Simple html generation enabled")
            html_reporter.make_html_reports()
        except (Exception,) as ex:
            logger.warning(ex)


def generate_html_reports(json_data):
    """
    This function generates the html reports.
    :return:
    :rtype:
    """
    logger.debug('HTML generation begins')
    try:
        html_files, attach_files = _generate_html_reports(json_data)
        return html_files, attach_files

    except (Exception,) as ex:
        logger.exception(ex)
        raise TalosGenerationReportError(f"It was impossible to generate HTML reports, Exception error: {ex}")


def prepare_json_data(json_data):
    """
    Return prepared talos data json.
    """
    scenario_names = []
    for feature in json_data['features']:
        for scenario in feature['elements']:
            if scenario['name'] in scenario_names:
                scenario_location = str(scenario['location']).rfind(':')
                _scenario = f"{get_short_name(scenario['name'])}_{scenario['location'][scenario_location + 1:]}"
                scenario['scenario_file_name'] = _scenario
                logger.debug(f'Getting scenario data from: {_scenario}')
            else:
                _scenario = get_short_name(scenario['name'])
                scenario['scenario_file_name'] = _scenario
                logger.debug(f'Getting scenario data from report json from scenario: {_scenario}')
                scenario_names.append(scenario['name'])
    logger.debug("Talos json data prepared")
    return json_data


def generate_accessibility_html_reports(json_data, accessibility_files):
    """
    This function generate the accessibility html reports, global and single report.
    :type json_data: dict
    :type accessibility_files: list
    :return:
    """
    env, _ = load_env_html()
    html_files = [f"{BASE_DIR}/output/reports/accessibility/html/global_accessibility.html"]
    global_template = env.get_template("global_accessibility_template.html")

    global_datas = {
        "page_title": "Global Accessibility Report",
        "navbar_title": "Global Accessibility Reports",
        "reports": [],
        "global_data": json_data['global_data']
    }

    accessibility_template = env.get_template("accessibility_template.html")
    for accessibility_file in accessibility_files:
        with open(f"{BASE_DIR}/output/reports/accessibility/{accessibility_file}") as f:
            file_name = accessibility_file.replace(".json", '')
            accessibility_json_data = json.load(f)
            violations_percent, passes_percent, impact_results = _calculate_accessibility_results(
                accessibility_json_data)
            quality_gates, quality_gates_result = _calculate_quality_gates(accessibility_json_data)
            accessibility_json_data['quality_gates_result'] = quality_gates_result
            data = {
                "page_title": "Accessibility Report",
                "violations_percent": violations_percent,
                "passes_percent": passes_percent,
                "navbar_title": "Accessibility Reports",
                "data": accessibility_json_data,
                "global_data": json_data['global_data'],
                "impact_results": impact_results,
                "quality_gates": quality_gates,
            }
            accessibility_template.stream(data).dump(
                f"{BASE_DIR}/output/reports/accessibility/html/accessibility_{file_name}.html")
            html_files.append(f"{BASE_DIR}/output/reports/accessibility_{file_name}.html")
            global_datas['reports'].append({
                "name": file_name,
                "data": accessibility_json_data,
                "violations_percent": violations_percent,
                "passes_percent": passes_percent,
                "impact_results": impact_results
            })
    global_datas['global_results'] = _calculate_global_accessibility_results(global_datas['reports'])
    global_template.stream(global_datas).dump(f"{BASE_DIR}/output/reports/accessibility/html/global_accessibility.html")

    return html_files


def _calculate_accessibility_results(accessibility_json_data):
    """
    This function calculates the results of a single accessibility report and return
    the violation percent, passes percent and impact results.
    :param accessibility_json_data:
    :return:
    """
    violations_percent = 0
    passes_percent = 0
    impact_results = 0
    violations_and_passes = len(accessibility_json_data['violations']) + len(accessibility_json_data['passes'])
    if violations_and_passes > 0:
        passes_percent = format_decimal(
            (violations_and_passes - len(accessibility_json_data['violations'])) / violations_and_passes * 100)
        violations_percent = format_decimal(
            (violations_and_passes - len(accessibility_json_data['passes'])) / violations_and_passes * 100)

        impact_results = {}

        for item in accessibility_json_data['violations']:
            impact_results.setdefault(item['impact'], 0)
            impact_results[item['impact']] += 1

    return violations_percent, passes_percent, impact_results


def _calculate_global_accessibility_results(reports):
    impact_results = {}

    total_violations = 0
    total_passes = 0

    for report in reports:
        total_violations += len(report['data']['violations'])
        total_passes += len(report['data']['passes'])

        for item in report['data']['violations']:
            impact_results.setdefault(item['impact'], 0)
            impact_results[item['impact']] += 1

    violations_and_passes = total_violations + total_passes
    total_passes_percent = format_decimal(
        (violations_and_passes - total_violations) / violations_and_passes * 100)
    total_violations_percent = format_decimal(
        (violations_and_passes - total_passes) / violations_and_passes * 100)

    return {
        "impact_results": impact_results,
        "total_passes": total_passes,
        "total_violations": total_violations,
        "violations_and_passes": violations_and_passes,
        "violations_percent": total_violations_percent,
        "passes_percent": total_passes_percent
    }


def _calculate_quality_gates(json_data):
    """
    This function check if there are quality gates and return a key dict with the rules with passed or failed.
    :param json_data:
    :return:
    """
    rules = get_accessibility_rules()
    quality_gates = {}
    quality_gates_results = "passed"
    for rule in rules:
        quality_gates[rule] = "passed"

    violations = copy.copy(json_data['violations'])
    violations += json_data['incomplete']
    for violation in violations:
        for tag in violation['tags']:
            if tag in quality_gates and quality_gates[tag] == "passed":
                quality_gates[tag] = "failed"
                quality_gates_results = "failed"
    return quality_gates, quality_gates_results


def _generate_html_reports(json_data):
    """
    This function generates the html reports.
    :return:
    :rtype:
    """
    env, _ = load_env_html()

    global_template = env.get_template("global_template.html")

    data = {
        "page_title": f"{_('Global Report')}",
        "navbar_title": f"{_('Global Report')} - {json_data['global_data']['application']}",
        "features": json_data['features'],
        "global_data": json_data['global_data']
    }

    logger.debug("Data form HTML report configured")

    global_template.stream(data).dump(f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/global.html")
    feature_template = env.get_template("feature_template.html")
    scenario_template = env.get_template("scenario_template.html")
    html_files = [
        f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/global.html",
    ]

    attach_files = {}
    for feature in json_data['features']:
        feature['name'] = replace_chars(feature['name'])
        feature['short_name'] = get_short_name(feature['name'])
        feature_data = {
            "page_title": f"{_('Report for feature')} {feature['name']}",
            "navbar_title": f"{_('Report for feature')} {feature['name']}",
            "feature": feature,
            "global_data": json_data['global_data']
        }
        feature_template.stream(feature_data).dump(
            f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/feature_{feature['short_name']}.html")
        html_files.append(f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/feature_{feature['short_name']}.html")
        for scenario in feature['elements']:
            if scenario['type'] != "background":
                scenario['name'] = replace_chars(scenario['name'])
                scenario['short_name'] = get_short_name(scenario['name'])
                scenario_data = {
                    "feature_name": feature['name'],
                    "feature_short_name": feature['short_name'],
                    "page_title": f"{_('Report for scenario')} {scenario['name']}",
                    "navbar_title": f"{_('Report for scenario')} {scenario['name']}",
                    "scenario": scenario,
                    "scenario_short_name": scenario['short_name'],
                    "include_sub_steps_in_results": Settings.PYTALOS_REPORTS.get('include_sub_steps_in_results'),
                    "global_data": json_data['global_data']
                }
                scenario_template.stream(scenario_data).dump(
                    f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/scenario_{scenario['scenario_file_name']}.html")
                file_path = f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/scenario_{scenario['scenario_file_name']}.html"
                html_files.append(file_path)
                attach_files[file_path] = []
                for step in scenario['steps']:
                    if step.get('screenshots'):
                        attach_files[file_path] += [screenshot for screenshot in step['screenshots']]

    logger.debug(f"HTML templates loaded: {html_files}")
    logger.debug(f"HTML scenario template loaded: {scenario_template}")
    return html_files, attach_files


def post_jira(reports, json_data):
    """
    This function generates the pdf reports.
    :return:
    :rtype:
    """
    try:
        logger.info("Jira report enabled")
        jira = Jira()
        logger.info("Starting process of publishing evidences in Jira")
        doc_files = reports.get('doc', None)
        pdf_files = reports.get('pdf', None)
        if reports.get('html_attach'):
            compress_html_report(reports.get('html_attach', None))
        html_files = [Settings.OUTPUT_PATH.get() + os.sep + f for f in os.listdir(Settings.OUTPUT_PATH.get()) if f.endswith('.zip')]

        for i in range(0, len(json_data.get("features", []))):
            jira.post_to_jira(json_data.get("features", [])[i], html_files, pdf_files, doc_files)
        logger.info("Publishing process in Jira finished successfully")
    except (Exception,) as ex:
        logger.exception(ex)
        traceback.print_exc()


def generate_doc_reports(json_data):
    """
    This function generates the doc reports.
    :return:
    :rtype:
    """
    try:
        doc_report = CreateDOC()
        doc_files = []
        for feature in json_data.get("features", []):
            doc_files = doc_report.generate_document_report(feature, json_data.get("global_data", []))
        return doc_files
    except (Exception,) as ex:
        logger.exception(ex)
        raise TalosGenerationReportError(f"It was impossible to generate DOC reports, Exception error: {ex}")


def generate_pdf_reports(json_data):
    """
        This function generates pdf reports.
    :return:
    :rtype:
    """
    try:
        pdf_report = CreatePDF()
        pdf_files = []
        for feature in json_data.get("features", []):
            pdf_files = pdf_report.generate_document_report(feature, json_data.get("global_data", []))
        return pdf_files
    except (Exception,) as ex:
        logger.exception(ex)
        raise TalosGenerationReportError(f"It was impossible to generate PDF reports, Exception error: {ex}")


def generate_error_reports(json_data):
    """
        This function generates error reports.
    :return:
    :rtype:
    """
    try:
        env, _ = load_env_html()
        error_report = ErrorReport(json_data, env, _)
        error_report.generate_execution_errors_report()
    except (Exception,) as ex:
        logger.exception(ex)
        raise TalosGenerationReportError(f"It was impossible to generate error report, Exception error: {ex}")


def validate_generate_reports():
    """
    Validation of configurations for report generation.
    :return:
    """
    logger.debug('Validating reports to be generated')
    if Settings.PYTALOS_ALM.get('post_to_alm', default=False):
        if Settings.PYTALOS_ALM.get('attachments', default=False).get('pdf', False):
            Settings.PYTALOS_REPORTS.set('generate_pdf', value=True)
        if Settings.PYTALOS_ALM.get('attachments', default=False).get('docx', False):
            Settings.PYTALOS_REPORTS.set('generate_docx', value=True)
        if Settings.PYTALOS_ALM.get('attachments', default=False).get('html', False):
            Settings.PYTALOS_REPORTS.set('generate_html', value=True)
    if Settings.PYTALOS_JIRA.get('post_to_jira', default=False):
        if Settings.PYTALOS_JIRA.get('report', default=False).get('upload_pdf_evidence', False):
            Settings.PYTALOS_REPORTS.set('generate_pdf', value=True)
        if Settings.PYTALOS_JIRA.get('report', default=False).get('upload_doc_evidence', False):
            Settings.PYTALOS_REPORTS.set('generate_docx', value=True)
        if Settings.PYTALOS_JIRA.get('report', default=False).get('upload_html_evidence', False):
            Settings.PYTALOS_REPORTS.set('generate_html', value=True)


def update_profile_files():
    files_to_edit = get_files_to_edit()
    for key, value in files_to_edit.items():
        if key.endswith(".json"):
            with open(key, 'w', encoding='utf8') as json_file:
                json.dump(value, json_file)
        elif key.endswith(".yaml"):
            with open(key, 'w', encoding='utf8') as yaml_file:
                yaml.dump(value, yaml_file)


def generate_screenshot(context, step):
    """
    Screenshot generation.
    :param context:
    :param step:
    :return:
    """
    current_driver = str(context.current_driver).lower()
    tags = context.runtime.scenario.feature.tags + context.runtime.scenario.tags
    if current_driver not in ['api', 'backend', 'service'] and 'no-screenshot' not in tags:
        if Settings.PYTALOS_REPORTS.get('generate_screenshot'):
            if current_driver == 'host':
                program_title = context.pytalos_config.get('Driver', 'window_title')
                screenshot = get_host_screenshot(program_title)
                logger.debug(f"Screenshot for host saved: {screenshot}")
                return screenshot
            else:
                screenshot = get_step_screenshot(context, step)
                logger.debug(f"Screenshot for webdriver saved: {screenshot}")
                return screenshot
        elif Settings.PYTALOS_REPORTS.get('generate_screenshot_if_failed') is True and \
                step.status == 'failed' and current_driver != 'host':
            screenshot = get_step_screenshot(context, step)
            logger.debug(f"Screenshot for step failure saved: {screenshot}")
            return screenshot


def get_step_screenshot(context, step):
    """
    Gets screenshot of the step.
    :param context:
    :param step:
    :return:
    """
    try:
        return context.utilities.capture_screenshot(
            f"{str(step.keyword)}_{str(step.name)}"
        )
    except AttributeError as ex:
        logger.warning(ex)
    except (Exception,) as ex:
        logger.warning(ex)


def set_initial_step_data(step):
    """
    This function set new initial data to the step passed in order to avoid errors in the html reports generation.
    :param step:
    :type step:
    :return:
    :rtype:
    """
    step.start_time = datetime.datetime.now().timestamp()
    logger.debug('Setup initial step data')
    return step


def set_initial_feature_data(context, feature):
    """
    This function set new initial data to the scenario passed in order
    to avoid errors in the html reports generation.
    :param context:
    :type context:
    :param feature:
    :type feature:
    :return:
    :rtype:
    """
    feature.start_time = datetime.datetime.now().timestamp()
    feature.driver = context.current_driver
    feature.config_environment = context.config_environment

    logger.debug('Setup initial feature data')

    return feature


def add_step_data(context, step, screenshot_path):
    """
    This function add data to the step in order to be reflected in the json file.
    :param context:
    :type context:
    :param step:
    :type step:
    :param screenshot_path:
    :type screenshot_path:
    :return:
    :rtype:
    """
    step.end_time = datetime.datetime.now().timestamp()
    try:
        if hasattr(context, "response") and len(context.runtime.api_info) > 0:
            # If the step isn't a sub step or if the option include_sub_steps_in_results is True
            if not hasattr(step, 'parent_step') or Settings.PYTALOS_REPORTS.get('include_sub_steps_in_results'):
                step.request = dict({
                    "url": context.runtime.api_info['url'],
                    "headers": context.runtime.api_info['headers'],
                    "body": context.runtime.api_info['body'],
                    "params": context.runtime.api_info['params']
                })
                step.response_content = context.runtime.api_info['response']
                step.response_headers = context.runtime.api_info['response_headers']
                step.api_info = context.runtime.api_info
            else:
                # Only when the step is a sub step and the option include_sub_steps_in_results is False then add
                # evidences to parent step
                step.parent_step.request = dict({
                    "url": context.runtime.api_info['url'],
                    "headers": context.runtime.api_info['headers'],
                    "body": context.runtime.api_info['body'],
                    "params": context.runtime.api_info['params']
                })
                step.parent_step.api_info = context.runtime.api_info
                step.parent_step.response_content = context.runtime.api_info['response']
                step.parent_step.response_headers = context.runtime.api_info['response_headers']
    except KeyError as ex:
        logger.warning(ex)

    # If the step is a normal step or if it's a sub step and the option include_sub_steps_in_results is True
    if not hasattr(step, 'parent_step') or Settings.PYTALOS_REPORTS.get('include_sub_steps_in_results'):
        step.jsons = context.func.evidences.jsons
        step.unit_tables = context.func.evidences.unit_tables
        step.additional_text = context.func.evidences.texts
        step.additional_html = context.func.evidences.htmls
        step.screenshots = context.func.evidences.screenshots
        step.screenshots += [screenshot_path] if screenshot_path is not None else []
    else:
        context.func.evidences.screenshots += [screenshot_path] if screenshot_path is not None else []

    logger.debug('Execution step data information added into json report')

    return step


def add_scenario_data(scenario):
    """
    This function add data to the scenario in order to be reflected in the json file.
    :param scenario:
    :type scenario:
    :return:
    :rtype:
    """
    if Settings.PYTALOS_REPORTS.get('include_sub_steps_in_results'):
        scenario.steps += scenario.sub_steps
    scenario.end_time = datetime.datetime.now().timestamp()
    scenario.total_steps = len(scenario.steps + scenario.background_steps)
    scenario.steps_passed, scenario.steps_failed, scenario.steps_skipped = count_scenario_passed_steps(scenario)

    scenario.steps_passed_percent = "0" if scenario.steps_passed == 0 else format_decimal(
        scenario.steps_passed * 100 / scenario.total_steps)
    scenario.steps_failed_percent = "0" if scenario.steps_failed == 0 else format_decimal(
        scenario.steps_failed * 100 / scenario.total_steps)
    scenario.steps_skipped_percent = "0" if scenario.steps_skipped == 0 else format_decimal(
        scenario.steps_skipped * 100 / scenario.total_steps
    )
    logger.debug('Execution scenario data information added into json report')
    return scenario


def add_feature_data(feature):
    """
        This function add data to the feature in order to be reflected in the json file.
    :param feature:
    :type feature:
    :return:
    :rtype:
    """
    feature.end_time = datetime.datetime.now().timestamp()

    for scenario in feature.scenarios:
        if scenario.type == "scenario" and scenario.status != "skipped":
            if scenario.status == "passed":
                feature.passed_scenarios += 1
            elif scenario.status == "failed":
                feature.failed_scenarios += 1
            feature.total_scenarios += 1

            feature.total_steps += scenario.total_steps
            feature.steps_passed += scenario.steps_passed
            feature.steps_failed += scenario.steps_failed
            feature.steps_skipped += scenario.steps_skipped

        elif scenario.type == "scenario_outline":
            scenarios_list = [_scenario for _scenario in scenario.scenarios if _scenario.status != "skipped"]

            _passed_scenarios, _failed_scenarios, _total_scenarios = count_feature_passed_scenarios(scenarios_list)
            feature.passed_scenarios += _passed_scenarios
            feature.failed_scenarios += _failed_scenarios
            feature.total_scenarios += _total_scenarios

            for scenario_from_scenario_list in scenarios_list:
                feature.total_steps += scenario_from_scenario_list.total_steps
                feature.steps_passed += scenario_from_scenario_list.steps_passed
                feature.steps_failed += scenario_from_scenario_list.steps_failed
                feature.steps_skipped += scenario_from_scenario_list.steps_skipped

    feature.scenarios_passed_percent = "0" if feature.passed_scenarios == 0 else format_decimal(
        feature.passed_scenarios * 100 / feature.total_scenarios)
    feature.scenarios_failed_percent = "0" if feature.failed_scenarios == 0 else format_decimal(
        feature.failed_scenarios * 100 / feature.total_scenarios)

    feature.steps_passed_percent = "0" if feature.steps_passed == 0 else format_decimal(
        feature.steps_passed * 100 / feature.total_steps)
    feature.steps_failed_percent = "0" if feature.steps_failed == 0 else format_decimal(
        feature.steps_failed * 100 / feature.total_steps)
    feature.steps_skipped_percent = "0" if feature.steps_skipped == 0 else format_decimal(
        feature.steps_skipped * 100 / feature.total_steps)
    logger.debug('Execution feature data information added into json report')

    return feature


def count_scenario_passed_steps(scenario):
    """
        This function counts and return the passed, failed and skipped steps given a scenario object
    :param scenario:
    :type scenario:
    :return:
    :rtype:
    """
    passed_steps = 0
    failed_steps = 0
    skipped_steps = 0
    steps = scenario.steps + scenario.background_steps

    for step in steps:
        if step.status == "passed":
            passed_steps += 1
        elif step.status == "failed":
            failed_steps += 1
        elif step.status == "skipped":
            skipped_steps += 1
        elif step.status == "undefined":
            skipped_steps += 1
        elif step.status == "untested":
            skipped_steps += 1
    logger.debug("Step results of the executed scenario:")
    logger.debug(f"Passed: {passed_steps}, Failed: {failed_steps}, Skipped: {skipped_steps}")
    return passed_steps, failed_steps, skipped_steps


def count_feature_passed_scenarios(scenarios):
    """
        This function counts and return the passed, failed and skipped steps given a feature object
    :param scenarios:
    :type scenarios:
    :return:
    :rtype:
    """
    passed_scenarios = 0
    failed_scenarios = 0
    total_scenarios = 0

    for scenario in scenarios:
        if scenario.status == "passed":
            passed_scenarios += 1
            total_scenarios += 1
        else:
            failed_scenarios += 1
            total_scenarios += 1
    logger.debug("Scenarios results of the executed feature:")
    logger.debug(f"Passed: {passed_scenarios}, Failed: {failed_scenarios}")
    return passed_scenarios, failed_scenarios, total_scenarios


def format_decimal(value):
    """
    Format value to decimal
    :param value:
    :return:
    """
    return f"{value:.2f}"


def set_accessibility_initial_data(context):
    """
    Configuring accessibility test initial data
    :param context:
    :return:
    """
    if Settings.PYTALOS_ACCESSIBILITY.get('automatic_analysis'):
        logger.info('Accessibility automatic analysis enabled')
        context.runtime.current_url = 'data:,'
        settings_rules = Settings.PYTALOS_ACCESSIBILITY.get('rules')
        logger.debug(f"Accessibility rules activated: {settings_rules}")

        context.runtime.rules = get_accessibility_rules()


def get_accessibility_rules():
    """
    This function return an array with all the accessibility rules
    :return:
    """
    settings_rules = Settings.PYTALOS_ACCESSIBILITY.get('rules')
    rules = []
    for rule in settings_rules.keys():
        if rule == 'cat':
            for cat in settings_rules[rule].keys():
                if settings_rules[rule][cat]:
                    rules.append(f"cat.{cat}")
        elif settings_rules[rule]:
            rules.append(rule)
    return rules


def run_accessibility_test(context):
    """
    Execute accessibility test if enabled
    :param context:
    :return:
    """
    no_driver = ['backend', 'no_driver', 'host', 'service', 'api']
    if Settings.PYTALOS_ACCESSIBILITY.get('automatic_analysis') and context.current_driver not in no_driver:
        if context.driver.current_url != context.runtime.current_url:
            logger.info("Analysis of accessibility running:")
            logger.info(f"URL to analyze: {context.runtime.current_url}")
            context.runtime.current_url = context.driver.current_url
            axe = AxeWrapper(context.driver)
            axe.inject()

            if not context.runtime.rules:
                options = None
            else:
                options = {
                    'runOnly': context.runtime.rules
                }

            results = axe.run(options=options)

            file_name = results['url'] \
                .replace('https://', '') \
                .replace('www', '') \
                .replace('.com', '') \
                .replace('.html', '') \
                .replace('.htm', '') \
                .replace('.asp', '') \
                .replace('.php', '')

            file_name = get_valid_filename(file_name)
            logger.debug(f"Results generated in: {file_name}")
            write_results(results, file_name)


def init_talos_virtual(context):
    """
    This function initialize talos virtual if it is enabled in settings.
    :param context:
    :return:
    """
    if Settings.TALOS_VIRTUAL.get('mountebank').get("enabled"):
        context.talosvirtual = TalosVirtual(context)
        context.talosvirtual.mountebank = MountebankWrapper()
        context.talosvirtual.mountebank.start_process()
        create_dict_imposter(context)
        context.talosvirtual.mountebank.create_imposter(
            dict_imposter=context.talosvirtual.mountebank.dict_imposter  # noqa
        )


def init_auto_retry(feature):
    """
    This function initialize autoretry if it is enabled in settings.
    :param feature:
    :return:
    """
    if Settings.PYTALOS_RUN.get('autoretry').get('enabled'):
        attempts = Settings.PYTALOS_RUN.get('autoretry').get('attempts')
        logger.debug(f"Execution auto retry is enabled with {attempts} attempts")
        for scenario in feature.scenarios:
            patch_scenario_with_autoretry(scenario, max_attempts=attempts)
    else:
        for scenario in feature.scenarios:
            if 'autoretry' in scenario.tags:
                logger.debug(f"Autoretry tag found in scenario: {scenario.name}")
                patch_scenario_with_autoretry(scenario, max_attempts=Settings.PYTALOS_RUN.get('autoretry').get('attempts'))


def wait_seconds_autoretry(context):
    """
    This function wait in seconds a time between attempts.
    :return:
    """
    if (Settings.PYTALOS_RUN.get('autoretry').get('enabled') or 'autoretry' in context.scenario.tags) \
            and context.scenario.status.name == 'failed':
        logger.debug('Performing auto retry wait')
        time.sleep(Settings.PYTALOS_RUN.get('autoretry').get('attempts_wait_seconds'))


def check_scenarios_order(feature):
    """
        This function check if the scenarios of a feature contains 'order-' in the tag so in that case
        reorder the scenarios to execute.
    :param feature:
    :return:
    """
    priority_list = []
    zero_list = []
    no_priority_list = []

    for scenario in feature.scenarios:
        tags = [tag for tag in scenario.tags if 'order-' in tag]
        if len(tags) > 0:
            try:
                order = tags[0].split('-')[1]
                if order == '0':
                    zero_list.append(scenario)
                else:
                    priority_list.insert(int(order) - 1, scenario)
            except (Exception,):
                no_priority_list.append(scenario)
        else:
            no_priority_list.append(scenario)

    feature.scenarios = zero_list + priority_list + no_priority_list


def check_features_order(features):
    """
        This function check if the feature contains 'order-' in any of their tags so in that case
        reorder the features to execute.
    :param features:
    :return:
    """
    ordered_features = [0] * len(features)
    unordered_features = []

    for old_position, feature in enumerate(features):
        tag = [tag for tag in feature.tags if 'order-' in tag]
        if len(tag) > 0:
            new_position = int(tag[0].replace('order-', '')) - 1
            ordered_features[new_position] = features[old_position]
        else:
            unordered_features.append(feature)

    unordered_index = 0
    for idx, _feature in enumerate(ordered_features):
        if not isinstance(_feature, Feature):
            ordered_features[idx] = unordered_features[unordered_index]
            unordered_index += 1

    return ordered_features


def load_env_html():
    logger.debug('Configuring Babel environment for translations of the HTML report')
    gnu_translations = load_translation('html_reports')

    env = Environment(
        extensions=['jinja2.ext.i18n'],
        loader=FileSystemLoader(f"{BASE_DIR}/arc/resources/html_templates"),
        autoescape=select_autoescape(),
    )

    env.install_gettext_translations(gnu_translations, newstyle=True)  # noqa

    _ = gnu_translations.gettext
    logger.debug("Translations uploaded for HTML templates")

    env.filters['format_datetime'] = get_datetime_from_timestamp
    env.filters['get_duration'] = get_duration
    env.filters['jsonpretty'] = json_pretty
    env.filters['parse_content_type'] = parse_content_type
    env.filters['transform_image_to_webp'] = transform_image_to_webp
    env.filters['transform_accessibility_image_to_webp'] = transform_accessibility_image_to_webp
    env.filters['replace_template_var'] = replace_template_var
    env.filters['get_short_name'] = get_short_name
    return env, _


def sauce_labs_set_test_status(context):
    """
        This function update the status of the job when it's finished.
        It takes note if the job was in a real device or in a virtual device because
        the api url changes if between a real device or a virtual device.

        Also, it needs to check the job status and when it's complete then set passed or failed.
        It checks the job status 10 times. At the first attempt if it's complete then do the update and exit the while.
    :param context:
    :return:
    """
    url = context.pytalos_config.get('Server', 'host').replace('ondemand', 'api')
    username = context.pytalos_config.get('Server', 'username')
    api_key = context.pytalos_config.get('Server', 'password')
    if context.pytalos.driver_wrapper.driver.capabilities.get('jobUuid'):
        logger.debug("The job is executed in a real device")
        job_id = context.pytalos.driver_wrapper.driver.capabilities['jobUuid']
        job_type = "v1/rdc"
    else:
        logger.debug("The job is executed in a virtual device")
        job_id = context.pytalos.driver_wrapper.driver.session_id
        job_type = f"rest/v1/{username}"
    full_uri = f"{url}/{job_type}/jobs/{job_id}"
    logger.debug(f"Prepared uri {full_uri}")
    logger.debug("Preparing request to update job status.")
    tries = 0
    while tries < 10:
        time.sleep(2.5)
        try:
            response = requests.get(auth=(username, api_key), url=full_uri)
            if response.status_code == 200:
                response_json = json.loads(response.text)
                if response_json['status'] == "complete":
                    response = requests.put(
                        auth=(username, api_key), url=full_uri,
                        headers={"Content-Type": "application/json"},
                        json={"passed": "true" if context.pytalos.global_status['test_passed'] else "false"}
                    )
                    if response.status_code in [200]:
                        logger.debug("The job status info has been updated")
                        logger.debug(f"Response: {response.text}")
                    else:
                        logger.debug(f"There was an error sending the request. Status code {response.status_code}")
                        logger.debug(f"Response: {response.text}")
                    logger.debug(f"Retries needed {tries}")
                    break
                tries += 1
            else:
                break
        except TalosRunError as e:
            tries += 1
            logger.error("The was an error sending the request to SauceLabs api.")
            logger.error(e)


def save_metrics(json_data):
    from sqlalchemy.orm import Session

    """
        Given the talos_report json data generate the db engine and try to save the execution result, the features,
        scenarios and steps and sub steps.
        "With" is needed in order to keep opened the connection with the database and close it when it's finished.
    :param json_data:
    :return:
    """
    engine = get_db()
    with Session(engine) as session:
        # Save execution
        execution = save_execution_data(session, json_data)
        # Save features, scenarios and steps.
        for feature_position, feature in enumerate(json_data['features'], 1):
            execution_feature = save_feature_data(session, feature, execution.id, feature_position)
            for scenario_position, element in enumerate(feature['elements'], 1):
                if element["type"] != "background":
                    execution_scenario = save_scenario_data(session, element, execution_feature.id, scenario_position)
                    for step_position, step in enumerate(element['steps'], 1):
                        save_step_data(session, step, execution_scenario.id, step_position)


def add_summary_portal(results):
    try:
        if os.environ.get('EXECUTION_TYPE') == 'Portal':
            diff_hours = 0
            diff_minutes = 0
            diff_seconds = 0

            features_passed = results.get('features_passed')
            features_failed = results.get('features_failed')
            features_skipped = results.get('total_features') - features_passed - features_failed
            scenarios_passed = results.get('passed_scenarios')
            scenarios_failed = results.get('failed_scenarios')
            scenarios_skipped = results.get('total_scenarios') - scenarios_passed - scenarios_failed
            steps_passed = results.get('steps_passed')
            steps_failed = results.get('steps_failed')
            steps_skipped = results.get('steps_skipped')

            if results.get('start_time') and results.get('end_time'):
                diff_seconds = abs(results.get('start_time') - results.get('end_time'))
                diff_timedelta = datetime.timedelta(seconds=diff_seconds)
                diff_hours = diff_timedelta.seconds // 3600
                diff_minutes = (diff_timedelta.seconds % 3600) // 60
                diff_seconds = diff_timedelta.seconds % 60
            print_portal_console(
                f"Features: {features_passed} passed, {features_failed} failed, {features_skipped} skipped\n")
            print_portal_console(
                f"Scenarios: {scenarios_passed} passed, {scenarios_failed} failed, {scenarios_skipped} skipped\n")
            print_portal_console(f"Steps: {steps_passed} passed, {steps_failed} failed, {steps_skipped} skipped\n")
            print_portal_console(f"Duration: {diff_hours:02}h {diff_minutes:02}m {diff_seconds:02}s\n")
        else:
            return False
    except requests.ConnectionError:
        return False


def save_execution_data(session, json_data):
    """
        Given the session and the json data save the execution results data.
        Return the created execution in order to use it later for the features.
    :param session:
    :param json_data:
    :return:
    """
    _results = json_data['global_data']['results']
    results = {
        "total_features": _results['total_features'],
        "features_passed": _results['features_passed'],
        "features_failed": _results['features_failed'],
        "total_scenarios": _results['total_scenarios'],
        "passed_scenarios": _results['passed_scenarios'],
        "failed_scenarios": _results['failed_scenarios'],
        "total_steps": _results['total_steps'],
        "steps_passed": _results['steps_passed'],
        "steps_failed": _results['steps_failed'],
        "steps_skipped": _results['steps_skipped'],
        "start_time": _results['start_time'],
        "end_time": _results['end_time'],
        "application": json_data['global_data']['application'],
        "business_area": json_data['global_data']['business_area'],
        "entity": json_data['global_data']['entity'],
        "user_code": json_data['global_data']['user_code'],
        "environment": json_data['global_data']['environment'],
        "version": json_data['global_data']['version'],
    }
    execution = Execution(**results)
    session.add(execution)
    session.commit()
    return execution


def save_feature_data(session, feature, execution_id, position):
    """
        Given a session, a feature dict, the execution id and the position of the feature save all the data
        of the feature in the database.
    :param session:
    :param feature:
    :param execution_id:
    :param position:
    :return:
    """
    feature_data = {
        "execution_id": execution_id,
        "name": feature['name'],
        "description": feature.get('description', [''])[0],
        "status": StatusType[feature['status'].upper()],
        "position": position,
        "total_scenarios": feature['total_scenarios'],
        "passed_scenarios": feature['passed_scenarios'],
        "failed_scenarios": feature['failed_scenarios'],
        "total_steps": feature['total_steps'],
        "steps_passed": feature['steps_passed'],
        "steps_failed": feature['steps_failed'],
        "steps_skipped": feature['steps_skipped'],
        "start_time": feature['start_time'],
        "end_time": feature['end_time'],
        "duration": feature['duration'],
        "os": feature['operating_system'],
        "driver": feature['driver'],
    }
    execution_feature = ExecutionFeature(**feature_data)
    session.add(execution_feature)
    session.commit()
    return execution_feature


def save_scenario_data(session, element, feature_id, position):
    """
        Given a session, a scenario dict, the feature id and the position of the scenario save all the data
        of the scenario in the database.
    :param session:
    :param element:
    :param feature_id:
    :param position:
    :return:
    """
    element_data = {
        "feature_id": feature_id,
        "name": element['name'],
        "description": element.get('description', [''])[0],
        "status": StatusType[element['status'].upper()],
        "position": position,
        "scenario_type": ScenarioType[element['type'].upper()],
        "total_steps": element.get('total_steps', 0),
        "steps_passed": element.get('steps_passed', 0),
        "steps_failed": element.get('steps_failed', 0),
        "steps_skipped": element.get('steps_skipped', 0),
        "start_time": element.get('start_time', 0),
        "end_time": element.get('end_time', 0),
        "duration": element.get('duration', 0)
    }
    execution_scenario = ExecutionScenario(**element_data)
    session.add(execution_scenario)
    session.commit()
    return execution_scenario


def save_step_data(session, step, scenario_id, position, parent_step_id=None):
    """
        Given a session, a step dict, the scenario id and the position of the step save all the data
        of the step in the database.
        Also, if the step have sub steps then create the step with the parent step id
    :param session:
    :param step:
    :param scenario_id:
    :param position:
    :param parent_step_id:
    :return:
    """
    step_data = {
        "scenario_id": scenario_id,
        "parent_step": parent_step_id,
        "keyword": step['keyword'],
        "name": step['name'],
        "position": position,
    }
    if step.get('result'):
        step_data.update({
            "status": StatusType[step.get('result').get('status').upper()],
            "duration": step.get('result').get('duration'),
            "start_time": step.get('start_time'),
            "end_time": step.get('end_time'),
        })
    else:
        step_data.update({
            "status": StatusType.SKIPPED,
            "duration": 0
        })
    execution_step = ExecutionStep(**step_data)
    session.add(execution_step)
    session.commit()
    if hasattr(step, 'sub_steps') and len(step.get('sub_steps')):
        for sub_step_position, sub_step in enumerate(step.get('sub_steps'), 1):
            save_step_data(session, sub_step, scenario_id, sub_step_position, execution_step.id)


def start_recording(context, scenario):
    """
        Given the context driver and scenario name, uses the recorder class to start a recording
        of the driver execution.
    :param context:
    :param scenario:
    :return: returns the recorder object to stop it after the scenario is executed.
    """
    if Settings.PYTALOS_REPORTS.get('generate_video') and Settings.PYTALOS_REPORTS.get('generate_video').get('enabled'):
        if context.current_driver in ['api', 'backend', 'service', 'no_driver']:
            Settings.PYTALOS_REPORTS.set('generate_video.enabled', value=False)
            return None
        else:
            output_file = f"{BASE_DIR}/output/videos/{scenario.name}"
            fps = Settings.PYTALOS_REPORTS.get('generate_video').get('fps')
            video_format = Settings.PYTALOS_REPORTS.get('generate_video').get('video_format')
            recorder = Recorder(
                driver=context.driver,
                file_name=output_file,
                fps=fps,
                video_format=video_format
            )
            recorder.record_screen()
            return recorder


def stop_recording(context):
    """
        Given the context recorder, calls the function to stop the recording and save
        the video report.
    :param context:
    :return:
    """
    if Settings.PYTALOS_REPORTS.get('generate_video') and Settings.PYTALOS_REPORTS.get('generate_video').get('enabled'):
        if context.current_driver in ['api', 'backend', 'service', 'no_driver']:
            Settings.PYTALOS_REPORTS.set('generate_video.enabled', value=False)
            return None
        else:
            context.recorder.stop_recording()


def print_errors_end():
    from arc.core.behave.runner import ERROR_HOOK_MSG
    if len(ERROR_HOOK_MSG) > 0:
        ERROR_HOOK_MSG.reverse()
        print("\n")
        for msg in ERROR_HOOK_MSG:
            if ERROR_HOOK_MSG.index(msg) + 1 == len(ERROR_HOOK_MSG):
                console_msg = f"MAIN ERROR: {msg}"
            else:
                console_msg = f"ERROR {ERROR_HOOK_MSG.index(msg) + 1}: {msg}"
            print(console_msg)
            logger.error(console_msg)
            if os.environ.get('EXECUTION_TYPE') == 'Portal':
                print_portal_console(console_msg + '\n')
        print("\n")


def check_install_driver(context):
    if Settings.PYTALOS_GENERAL.get('update_driver').get('enabled_update'):
        driver_type = context.pytalos_config.get('Driver', 'type')
        driver_name = 'gecko' if driver_type == 'firefox' else driver_type
        logger.info(f"Updating {driver_name} driver...")
        print(Fore.YELLOW + f"Updating {driver_name} driver...")
        driver_path = context.pytalos_config.get('Driver', f"{driver_name}_driver_path")
        install_driver = InstallDriver(driver_path)
        install_driver.install_driver(driver_type)
