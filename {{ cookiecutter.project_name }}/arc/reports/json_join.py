# -*- coding: utf-8 -*-
"""
Module to unify the json reports generated in parallel executions into a single json report.
"""
import datetime
import json
import logging
import os

from arc.core.behave.env_utils import format_decimal
from arc.core.behave.parallel import ENVIRONMENTS, BROWSERS, MULTI_BROWSERS_SCENARIOS
from arc.settings.settings_manager import Settings
from arc import __VERSION__
logger = logging.getLogger(__name__)

JSONS_PATH = Settings.REPORTS_PATH.get(force=True) + os.sep


def get_reports():
    """
    Gets and parses all generated json reports.
    :return:
    """
    jsons = []
    for file_name in [file for file in os.listdir(JSONS_PATH) if file.endswith('.json')]:
        logger.debug(f'Reading and retrieving data from the json report: {file_name}')
        with open(JSONS_PATH + file_name, encoding='utf8') as json_file:
            data = json.load(json_file)
            jsons.append(data)

    logger.debug(f"Unifying json reports for parallel executions: {os.environ['PARALLEL_TYPE']}")
    if os.environ['PARALLEL_TYPE'] in [BROWSERS, MULTI_BROWSERS_SCENARIOS]:
        for _json in jsons:
            for feature in _json['features']:
                feature['name'] += f" - {feature['config_environment'].upper()}"
                for scenario in feature['elements']:
                    scenario['name'] += f" - {feature['config_environment'].upper()}"
    if os.environ['PARALLEL_TYPE'] == ENVIRONMENTS:
        for _json in jsons:
            for feature in _json['features']:
                feature['name'] += f" - {_json['global_data']['environment'].upper()}"
                for scenario in feature['elements']:
                    scenario['name'] += f" - {_json['global_data']['environment'].upper()}"

    return jsons


def insert_scenarios(json_feature, scenario, scenario_name):
    """
    Insert scenarios from json reports.
    :param json_feature:
    :param scenario:
    :param scenario_name:
    :return:
    """
    insert = True
    for json_scenario in json_feature['elements']:
        if json_scenario['name'] == scenario_name:
            insert = False
    if insert:
        json_feature['elements'].append(scenario)


def unify_scenarios(report_json, feature, feature_name):
    """
    Unify scenarios between json reports.
    :param report_json:
    :param feature:
    :param feature_name:
    :return:
    """
    for scenario in feature['elements']:
        if scenario['keyword'] != 'Background':
            scenario_name = scenario['name']
            for json_feature in report_json['features']:
                if json_feature['name'] == feature_name:
                    insert_scenarios(json_feature, scenario, scenario_name)


def unify_reports(json_data, report_json):
    """
    Unify json reports.
    :param json_data:
    :param report_json:
    :return:
    """
    features_names = []
    for data in json_data:
        features = data['features']
        for feature in features:
            feature_name = feature['name']
            if feature_name not in features_names:
                features_names.append(feature_name)
                report_json['features'].append(feature)
            else:
                unify_scenarios(report_json, feature, feature_name)

    return report_json


def match_steps_data(scenario, steps_passed, steps_failed, steps_skipped, duration):
    """
    Match steps result data.
    :param scenario:
    :param steps_passed:
    :param steps_failed:
    :param steps_skipped:
    :param duration:
    :return:
    """
    for step in scenario['steps']:
        if scenario['keyword'] != 'Background' and step.get('result'):
            if step['result']['status'] == 'passed':
                steps_passed += 1
            elif step['result']['status'] == 'failed':
                steps_failed += 1
            else:
                steps_skipped += 1

            duration += step['result']['duration']
        else:
            steps_skipped += 1

    return steps_passed, steps_failed, steps_skipped, duration


def match_scenario_data(scenario, passed_scenarios, failed_scenarios, total_steps):
    """
    Match scenario result data.
    :param scenario:
    :param passed_scenarios:
    :param failed_scenarios:
    :param total_steps:
    :return:
    """
    if scenario['keyword'] != 'Background':
        if scenario['status'] == 'passed':
            passed_scenarios += 1
        else:
            failed_scenarios += 1

        total_steps += len(scenario['steps'])

    return passed_scenarios, failed_scenarios, total_steps


def match_results(report_json):
    """
    Match result data.
    :param report_json:
    :return:
    """
    for feature in report_json['features']:
        total_scenarios = len(feature['elements'])
        feature['total_scenarios'] = total_scenarios

        passed_scenarios = 0
        failed_scenarios = 0
        total_steps = 0
        steps_passed = 0
        steps_failed = 0
        steps_skipped = 0
        duration = 0

        for scenario in feature['elements']:
            passed_scenarios, failed_scenarios, total_steps = match_scenario_data(
                scenario, passed_scenarios, failed_scenarios, total_steps
            )

            steps_passed, steps_failed, steps_skipped, duration = match_steps_data(
                scenario, steps_passed, steps_failed, steps_skipped, duration
            )

        feature['passed_scenarios'] = passed_scenarios
        feature['failed_scenarios'] = failed_scenarios

        feature['total_steps'] = total_steps
        feature['steps_passed'] = steps_passed
        feature['steps_failed'] = steps_failed
        feature['steps_skipped'] = steps_skipped

        scenarios_passed_percent = f"{0 if passed_scenarios == 0 else (passed_scenarios * 100) / total_scenarios:.2f}"
        scenarios_failed_percent = f"{0 if failed_scenarios == 0 else (failed_scenarios * 100) / total_scenarios:.2f}"

        feature['scenarios_passed_percent'] = scenarios_passed_percent
        feature['scenarios_failed_percent'] = scenarios_failed_percent

        feature['steps_passed_percent'] = f"{0 if steps_passed == 0 else (steps_passed * 100) / total_steps:.2f}"
        feature['steps_failed_percent'] = f"{0 if steps_failed == 0 else (steps_failed * 100) / total_steps:.2f}"
        feature['steps_skipped_percent'] = f"{0 if steps_skipped == 0 else (steps_skipped * 100) / total_steps:.2f}"

        feature['end_time'] = feature['start_time'] + duration
        feature['duration'] = duration
        feature['total_scenarios'] = total_scenarios

    return report_json


def dump_json(report_json):
    """
    Generate final json report
    :param report_json:
    :return:
    """
    path = JSONS_PATH + 'talos_report.json'
    with open(path, 'w', encoding='utf8') as fp:
        json.dump(report_json, fp, indent=4, ensure_ascii=False)
        logger.debug(f"Talos json report unified in: {path}")


def match_global_results(json_list):
    """
    Match global result data.
    :param json_list:
    :return:
    """
    ignore_keys = [
        "features_passed_percent",
        "features_failed_percent",
        "scenarios_passed_percent",
        "scenarios_failed_percent",
        "start_time",
        "end_time"
    ]
    global_result = {}

    last_start_time = None
    last_end_time = None

    if len(json_list) == 0:
        return {
            "total_features": 0,
            "features_passed": 0,
            "features_failed": 0,
            "total_scenarios": 0,
            "passed_scenarios": 0,
            "failed_scenarios": 0,
            "total_steps": 0,
            "steps_passed": 0,
            "steps_failed": 0,
            "steps_skipped": 0,
            "features_passed_percent": "0",
            "features_failed_percent": "0",
            "scenarios_passed_percent": "0",
            "scenarios_failed_percent": "0"
        }

    for _json in json_list:
        if last_start_time is None:
            last_start_time = _json['global_data']['results']['start_time']
        else:
            last_start_time = _json['global_data']['results']['start_time'] if last_start_time < \
                                                                               _json['global_data']['results'][
                                                                                   'start_time'] else last_start_time
        if last_end_time is None:
            last_end_time = _json['global_data']['results']['end_time']
        else:
            last_end_time = _json['global_data']['results']['end_time'] if last_end_time > \
                                                                           _json['global_data']['results'][
                                                                               'end_time'] else last_end_time
        for key, value in _json['global_data']['results'].items():
            if key not in ignore_keys:
                global_result[key] = global_result.get(key, 0) + value

    global_result[  # noqa
        'scenarios_passed_percent'
    ] = "0" if global_result['passed_scenarios'] == 0 else format_decimal(
        (global_result['passed_scenarios'] * 100) / global_result['total_scenarios'])
    global_result['scenarios_failed_percent'] = "0" if global_result['failed_scenarios'] == 0 else format_decimal(
        (global_result['failed_scenarios'] * 100) / global_result['total_scenarios'])

    global_result['features_passed_percent'] = "0" if global_result['features_passed'] == 0 else format_decimal(
        (global_result['features_passed'] * 100) / global_result['total_features']
    )
    global_result['features_failed_percent'] = "0" if global_result['features_failed'] == 0 else format_decimal(
        (global_result['features_failed'] * 100) / global_result['total_features']
    )

    global_result['start_time'] = last_start_time
    global_result['end_time'] = last_end_time

    return global_result


def join_json_reports():
    """
    Join json data reports.
    :return:
    """
    try:
        json_list = get_reports()
        final_results = match_global_results(json_list)
        _json = {
            'features': [],
            "global_data": {
                "keyword": "global_data",
                "date": datetime.datetime.now().strftime('%Y/%m/%d'),
                'application': Settings.PROJECT_INFO.get('application'),
                'business_area': Settings.PROJECT_INFO.get('business_area'),
                'entity': Settings.PROJECT_INFO.get('entity'),
                'environment': Settings.PYTALOS_PROFILES.get('environment'),
                'user_code': Settings.PROJECT_INFO.get('user_code'),
                'version': __VERSION__,
                'results': final_results
            },
            'octane': {
                'server': Settings.PYTALOS_OCTANE.get('server'),
                'username': Settings.PROJECT_INFO.get('user_code'),
                'clientid': Settings.PYTALOS_OCTANE.get('client_id'),
                'secret': Settings.PYTALOS_OCTANE.get('secret'),
                'sharedspace': Settings.PYTALOS_OCTANE.get('shared_space'),
                'workspace': Settings.PYTALOS_OCTANE.get('workspace')
            }
        }
        _json = unify_reports(json_list, _json)
        _json = match_results(_json)
        dump_json(_json)
    except FileNotFoundError as ex:
        logger.warning('The json report files have not been generated in order to generate the general report json.')
        logger.warning(ex)
