# -*- coding: utf-8 -*-
"""
TalosBDD Environment.
In this file, the hooks are executed in sequential order according to the execution time.
In each hook the necessary actions are made so that the framework performs its functionalities.
The order of execution of the hooks are:
 - before execution
 - before all
 - before feature
 - before_tag
 - before scenario
 - before step
 - after step
 - after scenario
 - after feature
 - after_tag
 - after all
 - after execution
"""
import datetime
import json
import os
import logging

from colorama import Fore

from arc.core.behave.configuration import set_report_configuration
from arc.core.env_settings import activate_environment_proxy
from arc.core.test_method.visual_test import activate_visualtesting, VisualTest
from arc.integrations.alm import run_alm_connect
from arc.integrations.octane import run_octane_connect
from arc.misc import title
from arc.reports.evidence import Evidence
from arc.reports.html.utils import BASE_DIR
from arc.reports.json_join import join_json_reports
from arc.settings.settings_manager import Settings
from arc.web.app.utils import send_info_portal
from arc.contrib import func
from arc.contrib.api import api_wrapper
from arc.contrib.db import sqlite
from arc.contrib.tools import ftp
from arc.core.behave import config_data, gherkin_format
from arc.core.behave.context_utils import RuntimeDatas, TestData
from arc.core.behave.env_utils import (
    post_jira,
    config_faker,
    enable_txt_report,
    run_hooks,
    enable_json_report,
    enable_host, close_host,
    set_alm_custom_variable, generate_screenshot, set_initial_feature_data,
    add_scenario_data, add_feature_data, set_initial_step_data, add_step_data, generate_simple_html_reports,
    generate_html_reports, generate_doc_reports, generate_pdf_reports, validate_generate_reports,
    utils_before_execution, utils_after_execution, set_accessibility_initial_data, run_accessibility_test,
    init_talos_virtual, init_auto_retry, wait_seconds_autoretry, prepare_json_data, generate_accessibility_html_reports,
    save_metrics, add_summary_portal, run_portal_hooks, print_errors_end, start_recording, stop_recording,
    check_install_driver, generate_error_reports
)
from arc.core.behave.environment import (
    before_all as core_before_all,
    before_feature as core_before_feature,
    before_scenario as core_before_scenario,
    after_scenario as core_after_scenario,
    after_feature as core_after_feature,
    after_all as core_after_all
)
from arc.core.paths.directories import enable_delete_old_reports, enable_save_old_reports, generate_needed_dir
from arc.core.paths.drivers import add_drivers_directory_to_path
from arc.contrib.utilities import Utils

from behave.step_registry import StepRegistry  # noqa
from behave.model import Scenario
from arc.core.behave.template_var import find_match, get_global

logger = logging.getLogger(__name__)


def before_execution():
    """
    Functions that are executed before Behave execution and testing.
    """
    logger.info('Running before execution environment')
    os.environ['EXECUTION_TYPE'] = 'Manual'
    run_portal_hooks(context=None, moment='before_execution')
    utils_before_execution()
    started_at = f'Started at: {datetime.datetime.now()}'
    logger.info(started_at)
    print(started_at)

    title()

    # Check if environment path exist
    logger.info('Checking the existence of the configured environment path')
    config_data.check_exist_environment_path()

    logger.info('Checking if the setting to save old reports is enabled')
    enable_save_old_reports(Settings.PYTALOS_REPORTS.get('save_old_reports'))

    logger.info('Checking if the setting to delete old reports is enabled')
    enable_delete_old_reports(Settings.PYTALOS_REPORTS.get('delete_old_reports'))

    logger.info('Generating needed dir')
    generate_needed_dir()

    activate_environment_proxy()

    logger.info('Settings reports configuration')
    set_report_configuration()

    # run hooks
    run_hooks(context=None, moment='before_execution')

    logger.info("The core before execution actions have been executed correctly")


def before_all(context):
    """
    Functions that are executed before anything of the tests.
    :param context:
    """
    logger.info('Running before all environment')
    # visual testing
    activate_visualtesting(context)

    # core task
    core_before_all(context)
    check_install_driver(context)

    # set core context functionalities
    logger.info('Settings core context functionalities')
    context.runtime = RuntimeDatas(context)
    context.test = TestData(context)
    context.runtime.master_file = Settings.PYTALOS_PROFILES.get('master_file')
    context.current_driver = context.pytalos_config.get('Driver', 'type')
    context.runtime.current_date = datetime.datetime.now()
    context.fake_data = config_faker()
    context.sqlite = sqlite.sqlite_db()

    # run before all functionalities
    Scenario.continue_after_failed_step = Settings.PYTALOS_RUN.get('continue_after_failed_step')
    logger.info('Adding drivers directory to path')
    add_drivers_directory_to_path()

    logger.info('Checking if txt report is enabled')
    context.runtime.txt_log = enable_txt_report()

    # run hooks
    run_hooks(context, 'before_all')

    logger.info("The core before all actions have been executed correctly")


def before_feature(context, feature):
    """
    Functionalities that are executed before the execution of the features.
    :param context:
    :param feature:
    """
    logger.info(f'Running before feature environment for: {feature.name}')
    logger.info('Checking if auto retry is enabled')
    init_auto_retry(feature)


    # core task
    core_before_feature(context, feature)
    logger.info('Settings initial feature data')
    set_initial_feature_data(context, feature)

    # init talos virtual
    logger.info('Checking if talos virtual is enabled')
    init_talos_virtual(context)

    # add log txt info
    if Settings.PYTALOS_REPORTS.get('generate_txt'):
        context.runtime.txt_log.write_before_feature_info(feature)

    # run hooks
    run_hooks(context, 'before_feature', feature)

    logger.info("The core before feature actions have been executed correctly")


def before_scenario(context, scenario):
    """
    Functionalities that are executed before the execution of the scenarios.
    :param context:
    :param scenario:
    """
    logger.info(f'Running before scenario environment for: {scenario.name}')

    # core task
    core_before_scenario(context, scenario)
    logger.info('Settings initial scenario data')

    # set core context functionalities
    logger.info('Setting core context functionalities for current scenario')
    context.runtime.scenario = scenario
    context.utilities = Utils()
    context.func = func.Func(context)

    # override function find_math of matchers (behave)
    StepRegistry.find_match = find_match

    gherkin_format.generate_scenario_description(scenario)
    logger.info(f'Scenario description generated: {scenario.description}')

    # enable reporting
    logger.info('Checking if json report is enabled')
    context.runtime.alm_json = enable_json_report(scenario)

    # enable automation functionalities
    logger.info('Checking if host is enabled')
    enable_host(context)
    logger.info('Setting api wrapper instance in context')
    context.api = api_wrapper.ApiObject(context)
    logger.info('Setting fpt wrapper instance in context')
    context.ftp = ftp.FtpObject(context)

    # run automatic accessibility analysis
    logger.info('Checking if automatically accessibility test is enabled')
    set_accessibility_initial_data(context)

    # run hooks
    run_hooks(context, 'before_scenario', scenario)

    # run recorder
    context.recorder = start_recording(context, scenario)

    logger.info("The core before scenario actions have been executed correctly")


def after_scenario(context, scenario):
    """
    Functionalities that are executed after the execution of the scenarios.
    :param context:
    :param scenario:
    """
    logger.info(f'Running after scenario environment for: {scenario.name}')

    # core task
    core_after_scenario(context, scenario)
    logger.info('Adding current scenario data in reports')
    add_scenario_data(scenario)

    # reporting actions
    driver = str(context.feature.driver).upper()

    if Settings.PYTALOS_REPORTS.get('generate_txt'):
        logger.debug('Writing scenario data in txt report')
        context.runtime.txt_log.write_scenario_info(scenario)

    # automation actions
    close_host(context)

    # run hooks
    run_hooks(context, 'after_scenario', scenario)

    # stop recorder
    stop_recording(context)

    if Settings.PYTALOS_ALM.get('generate_json'):
        logger.debug('Performing json alm reporting tasks for the executed scenario')
        if hasattr(context.runtime, 'alm_json'):
            context.runtime.alm_json.generate_json_after_scenario(
                scenario, driver, generate_html_report=Settings.PYTALOS_ALM.get('attachments').get('html'),
                generate_docx_report=Settings.PYTALOS_ALM.get('attachments').get('docx'),
                generate_pdf_report=Settings.PYTALOS_ALM.get('attachments').get('pdf')
            )
        else:
            logger.info('The ALM JSON could not be generated due to lack of execution information.')

    wait_seconds_autoretry(context)
    logger.info("The core after scenario actions have been executed correctly")


def after_feature(context, feature):
    """
    Functionalities that are executed after the execution of the features.
    :param context:
    :param feature:
    """
    logger.info(f'Running after feature environment for: {feature.name}')
    # core task
    core_after_feature(context, feature)

    # reporting actions
    if Settings.PYTALOS_REPORTS.get('generate_txt'):
        logger.debug('Writing feature data in txt report')
        context.runtime.txt_log.write_after_feature_info(feature)

    logger.info('Adding current feature data in reports')
    add_feature_data(feature)

    if Settings.TALOS_VIRTUAL.get('mountebank').get("enabled"):
        logger.info('Stopping talos virtual mountebank process')
        context.talosvirtual.mountebank.stop_process()

    # run hooks
    run_hooks(context, 'after_feature', feature)

    logger.info("The core after feature actions have been executed correctly")


def after_all(context):
    """
    Functions that are executed after anything of the tests.
    :param context:
    """
    logger.info('Running after all environment')
    # core task
    core_after_all(context)

    # reporting actions
    generate_simple_html_reports(Settings.PYTALOS_REPORTS.get('generate_simple_html'))

    if Settings.PYTALOS_REPORTS.get('generate_txt'):
        context.runtime.txt_log.write_summary()

    # catalog generation
    if Settings.PYTALOS_CATALOG.get('update_step_catalog'):
        from arc.reports.catalog import excel_catalog
        logger.info('Generating steps catalogue')
        excel_catalog.Catalog()

    # run hooks
    run_hooks(context, 'after_all')

    logger.info("The core after all actions have been executed correctly")


def before_step(context, step):
    """
    Functionalities that are executed before the execution of the steps.
    :param context:
    :param step:
    """
    logger.info(f'Running before step environment for: {step.name}')

    context.config.userdata = get_global()
    # set core context functionalities
    context.runtime.step = step
    set_alm_custom_variable(context)

    logger.info('Setting user config data')

    # evidences. When using sub steps, if we are in a sub step, then don't generate the Evidence object in order
    # to have all the evidences in the parent step BUT if we set the include_sub_steps_in_results option to True
    # then the Evidence object will be created for the sub step too.
    if not hasattr(step, 'parent_step'):
        context.func.evidences = Evidence(context)
    elif hasattr(step, 'parent_step') and Settings.PYTALOS_REPORTS.get('include_sub_steps_in_results'):
        context.func.evidences = Evidence(context)

    logger.info('Setting extra evidences instance')
    context.runtime.api_info = {}

    logger.info('Settings initial step data')
    set_initial_step_data(step)

    # run automatic accessibility analysis
    logger.info('Running automatically accessibility test if enabled')
    run_accessibility_test(context)

    # run hooks
    run_hooks(context, 'before_step', step)

    logger.info("The core before step actions have been executed correctly")


def after_step(context, step):
    """
    Functionalities that are executed after the execution of the steps.
    :param context:
    :param step:
    """
    logger.info(f'Running after step environment for: {step.name}')

    # reporting actions
    screenshot_path = generate_screenshot(context, step)

    logger.info('Adding current step data in report')
    add_step_data(context, step, screenshot_path)

    if hasattr(step, 'parent_step'):
        context.scenario.sub_steps.append(step)

    # run hooks
    run_hooks(context, 'after_step', step)

    logger.info("The core after step actions have been executed correctly")


def before_tag(context, tag):
    """
    Functionalities that are executed before tag of the scenario.
    :param context:
    :param tag:
    :return:
    """

    # run hooks
    run_hooks(context, 'before_tag', tag)


def after_tag(context, tag):
    """
    Functionalities that are executed after tag of the scenario.
    :param context:
    :param tag:
    :return:
    """
    # run hooks
    run_hooks(context, 'after_tag', tag)


def after_execution():
    """
    functions that are executed after Behave execution and testing.
    """
    print_errors_end()

    logger.info('Running after execution environment')

    if os.environ['RUN_TYPE'] == 'parallel':
        logger.info('Unifying json reports from parallel execution')
        join_json_reports()

    logger.debug('Checking generate report configurations')
    validate_generate_reports()

    logger.info("Generating reports...")
    print(Fore.YELLOW + "Generating reports...")

    # Read talos_report.json
    with open(f"{BASE_DIR}/output/reports/talos_report.json", encoding='utf-8') as json_file:
        logger.debug(f"Loading talos json report from: {BASE_DIR}/output/reports/talos_report.json")
        json_data = prepare_json_data(json.load(json_file))

    if Settings.PYTALOS_WEB.get('save_metrics', default=False) and len(json_data['features']) > 0:
        save_metrics(json_data)

    add_summary_portal(json_data.get('global_data').get('results'))

    # Visual tests
    if Settings.VISUAL_TESTING.get('enabled') and Settings.VISUAL_TESTING.get('generate_report'):
        if Settings.VISUAL_TESTING.get('generate_reports.json'):
            VisualTest().generate_json_report()
        if Settings.VISUAL_TESTING.get('generate_reports.html'):
            VisualTest().generate_html_report()

    # Get all json files in accessibility
    path_files = os.walk(f"{BASE_DIR}/output/reports/accessibility/")
    accessibility_files = []
    for path in path_files:
        accessibility_files += [file for file in path[2] if file.endswith('.json')]

    run_hooks(context=None, moment='before_reports', extra_info=json_data)

    pdf_files = None
    doc_files = None
    attach_files = None
    send_info_portal('Generating reports...')
    if Settings.PYTALOS_REPORTS.get('generate_html'):
        logger.info('Generating html reports')
        html_files, attach_files = generate_html_reports(json_data.copy())
        if len(accessibility_files) > 0:
            html_files += generate_accessibility_html_reports(json_data.copy(), accessibility_files)

    if Settings.PYTALOS_REPORTS.get('generate_docx'):
        logger.info('Generating docx reports')
        doc_files = generate_doc_reports(json_data.copy())

    if Settings.PYTALOS_REPORTS.get('generate_pdf'):
        logger.info('Generating pdf reports')
        pdf_files = generate_pdf_reports(json_data.copy())

    if Settings.PYTALOS_REPORTS.get('generate_error_report'):
        logger.info('Generating error reports')
        generate_error_reports(json_data)

    run_alm_connect(attach_files)
    run_octane_connect(attach_files)

    if Settings.PYTALOS_JIRA.get('post_to_jira'):
        logger.info('Posting evidences in jira')
        reports = {'html_attach': attach_files,
                   'pdf': pdf_files,
                   'doc': doc_files}
        post_jira(reports, json_data.copy())

    utils_after_execution()

    # run hooks
    run_hooks(context=None, moment='after_execution')

    logger.info("The core after execution actions have been executed correctly")
    ended_at = f'Ended at: {datetime.datetime.now()}'
    logger.info(ended_at)
    print(ended_at)
    send_info_portal('Execution has finished.')
    run_portal_hooks(context=None, moment='after_execution')

