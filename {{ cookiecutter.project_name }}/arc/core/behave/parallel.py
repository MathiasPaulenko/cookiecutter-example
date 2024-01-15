# -*- coding: utf-8 -*-
"""
A declaration file for Talos parallel execution command line arguments.

There are several declared argparse, since for each type of parallel execution different arguments are expected.
These args parse are:
    - parse by schema
    - parse by scenarios browser
    - parse by browsers
    - parse by environment
    - parse by scenarios
    - parse by features
"""
import argparse
import logging

from behave.model import ScenarioOutline
from behave.runner_util import parse_features, collect_feature_locations

from arc.core.behave.configuration import BehaveConfiguration

from arc.reports.custom_formatters import get_json_report_args_for_parallel
from arc.settings.settings_manager import Settings

try:
    from settings import settings
except (Exception,):
    from arc.settings import settings

logger = logging.getLogger(__name__)

BROWSERS = 'browsers'
SCENARIOS = 'scenarios'
FEATURES = 'features'
ENVIRONMENTS = 'environments'
MULTI_BROWSERS_SCENARIOS = 'multi_scenarios_browsers'
BROWSER_HELP = 'Launch configuration driver properties file'
__CLI_TITLE = 'CLI for TALOSBDD Automation Framework Parallel Execution'
MSG_PROP = 'Properties to run:'


def parse_parallel_schema_args(args=None):
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(__CLI_TITLE)
    parser.add_argument('--processes', '-p', type=int, help='Maximum number of processes. Default = 5', default=5)
    parser.add_argument('--parallel', '-x', choices=[
        'scenarios', 'features', 'browsers', 'environments', 'multi_scenarios_browsers'
    ],
                        help='Allow parallel execution', required=False)

    args = args.split(' ')
    parallel_args, unknown = parser.parse_known_args(args)
    logger.debug(f"Arguments configured for parallel execution: {parallel_args}")
    return parallel_args, ' '.join(unknown)


def parse_parallel_scenarios_browser_args(args=None):
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    # action="append", -> implemented this if it want to allow AND run conditions.
    parser = argparse.ArgumentParser(__CLI_TITLE)
    parser.add_argument('--browsers', '-b', help=BROWSER_HELP, required=True)
    parser.add_argument('--tags', '-t', help='Tags to launch', required=True)

    args = args.split(' ')
    parallel_args, unknown = parser.parse_known_args(args)
    logger.debug(f"Arguments configured for parallel execution: {parallel_args}")
    return parallel_args, ' '.join(unknown)


def parse_parallel_browsers_args(args=None):
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    # action="append", -> implemented this if it want to allow AND run conditions.
    parser = argparse.ArgumentParser(__CLI_TITLE)
    parser.add_argument('--browsers', '-b', help=BROWSER_HELP, required=True)

    args = args.split(' ')
    parallel_args, unknown = parser.parse_known_args(args)
    logger.debug(f"Arguments configured for parallel execution: {parallel_args}")
    return parallel_args, ' '.join(unknown)


def parse_parallel_environments_args(args=None):
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    # action="append", -> implemented this if it want to allow AND run conditions.
    parser = argparse.ArgumentParser(__CLI_TITLE)
    parser.add_argument('--environment', help='Launch environment configuration', required=True)

    args = args.split(' ')
    parallel_args, unknown = parser.parse_known_args(args)
    logger.debug(f"Arguments configured for parallel execution: {parallel_args}")
    return parallel_args, ' '.join(unknown)


def parse_parallel_scenarios_args(args=None):
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(__CLI_TITLE)
    parser.add_argument('--tags', '-t', help='Tags to launch', required=True)

    args = args.split(' ')
    parallel_args, unknown = parser.parse_known_args(args)
    logger.debug(f"Arguments configured for parallel execution: {parallel_args}")
    return parallel_args, ' '.join(unknown)


def parse_parallel_features_args(args=None):
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(__CLI_TITLE)
    parser.add_argument('--includes', '-i', help='Features file to launch', required=True)
    parser.add_argument('--excludes', '-e', help='Features file excluded', required=False)

    args = args.split(' ')
    parallel_args, unknown = parser.parse_known_args(args)
    logger.debug(f"Arguments configured for parallel execution: {parallel_args}")
    return parallel_args, ' '.join(unknown)


def add_extra_args_for_parallel(args):
    """
    Concatenates default arguments of parallel executions with behave arguments
    :param args:
    :return:
    """
    args += get_json_report_args_for_parallel() + ' --no-summary'
    logger.debug(f"Parallel execution extra args: {args}")
    return args


def get_browser_iterator(args, browsers):
    """
    Generation of the iterator for parallel executions for browser.
    :param args:
    :param browsers:
    :return:
    """
    from arc.core.behave.runner import CustomModelRunner
    browsers = browsers.split(',')
    iterator = []
    logger.debug(f"Getting iterator for browsers: {browsers}")
    for browser in browsers:
        params = add_extra_args_for_parallel(args)
        params = params + ' -D Config_environment=' + browser

        config = BehaveConfiguration(command_args=params, run_settings=settings)
        iterator.append((config, CustomModelRunner))

    logger.info(MSG_PROP)
    for browser in browsers:
        logger.info(f"--\t{browser}")
    logger.info('-' * 50)

    return iterator


def get_environment_iterator(args, environments):
    """
    Generation of the iterator for parallel executions for environment.
    :param args:
    :param environments:
    :return:
    """
    from arc.core.behave.runner import CustomModelRunner

    environments = environments.split(',')
    iterator = []
    logger.debug(f"Getting iterator for environments: {environments}")

    for environment in environments:
        params = add_extra_args_for_parallel(args)
        params = f'{params} -env={environment}'
        config = BehaveConfiguration(command_args=params, run_settings=settings)
        iterator.append((config, CustomModelRunner))

    logger.info(MSG_PROP)
    for environment in environments:
        logger.info(f"--\t{environment}")
    logger.info('-' * 50)

    return iterator


def run_browsers_parallel(parallel_args, run_args, pool, run_behave):
    """
    Run iterator for parallel executions for browser.
    :param parallel_args:
    :param run_args:
    :param pool:
    :param run_behave:
    :return:
    """
    browsers = parallel_args.browsers
    logger.debug(f"Running iterator for browsers: {browsers}")

    iterator = get_browser_iterator(run_args, browsers)
    with pool as process:
        results = process.starmap(run_behave, iterator)
        return results


def run_scenarios_browsers_parallel(parallel_args, run_args, pool, run_behave):
    """
    Run iterator for parallel executions for scenarios and browsers
    :param parallel_args:
    :param run_args:
    :param pool:
    :param run_behave:
    :return:
    """
    logger.debug("Running iterator for scenarios and browsers")
    iterator = get_scenarios_browsers_iterator(parallel_args, run_args)
    with pool as process:
        results = process.starmap(run_behave, iterator)
        return results


def get_scenarios_browsers_iterator(parallel_args, scenarios_args):
    """
    Generation of the iterator for parallel executions for scenarios and browsers.
    :param parallel_args:
    :param scenarios_args:
    :return:
    """
    from arc.core.behave.runner import CustomModelRunner
    tags = parallel_args.tags.split(',')
    scenarios = get_scenarios_from_tag(tags)

    iterator = []
    browsers = parallel_args.browsers.split(',')

    logger.debug(f"Getting iterator for browsers: {browsers} and tags: {tags}")

    scenarios_aux = []
    for browser in browsers:
        for scenario in scenarios:
            params = add_extra_args_for_parallel(scenarios_args)
            params += f" -n \"{scenario}\" --tags {parallel_args.tags}"
            params = params + ' -D Config_environment=' + browser
            scenarios_aux.append(f"{scenario}-{browser.capitalize()}")
            config = BehaveConfiguration(command_args=params, run_settings=settings)
            iterator.append((config, CustomModelRunner))

    logger.info(MSG_PROP)
    for scenario in scenarios_aux:
        logger.info(f"--\t{scenario}")
    logger.info('-' * 50)

    return iterator


def get_scenarios_iterator(parallel_args, scenarios_args):
    """
    Generation of the iterator for parallel executions for scenarios.
    :param parallel_args:
    :param scenarios_args:
    :return:
    """
    from arc.core.behave.runner import CustomModelRunner
    tags = parallel_args.tags.split(',')
    scenarios = get_scenarios_from_tag(tags)
    logger.debug(f"Running iterator for scenarios: {scenarios} and tags: {tags}")

    iterator = []
    for scenario in scenarios:
        params = add_extra_args_for_parallel(scenarios_args)
        params += f" -n \"{scenario}\" --tags {parallel_args.tags}"
        config = BehaveConfiguration(command_args=params, run_settings=settings)
        iterator.append((config, CustomModelRunner))

    logger.info(MSG_PROP)
    for scenario in scenarios:
        logger.info(f"--\t{scenario}")
    logger.info('-' * 50)

    return iterator


def run_scenarios_parallel(parallel_args, run_args, pool, run_behave):
    """
    Run iterator for parallel executions for scenarios
    :param parallel_args:
    :param run_args:
    :param pool:
    :param run_behave:
    :return:
    """
    logger.debug(f"Running iterator for scenarios")
    iterator = get_scenarios_iterator(parallel_args, run_args)
    with pool as process:
        results = process.starmap(run_behave, iterator)
        return results


def run_environments_parallel(parallel_args, run_args, pool, run_behave):
    """
    Run iterator for parallel executions for environments
    :param parallel_args:
    :param run_args:
    :param pool:
    :param run_behave:
    :return:
    """
    environments = parallel_args.environment
    logger.debug("Running iterator for environments")
    iterator = get_environment_iterator(run_args, environments)
    with pool as process:
        results = process.starmap(run_behave, iterator)
        return results


def get_features_iterator(parallel_args, scenarios_args):
    """
    Generate iterator for parallel executions for features
    :param parallel_args:
    :param scenarios_args:
    :return:
    """
    from arc.core.behave.runner import CustomModelRunner
    includes = parallel_args.includes.split(',')
    excludes = parallel_args.excludes
    logger.debug("Getting iterator for features")
    logger.debug(f"Includes features: {includes}")
    logger.debug(f"Excludes features: {excludes}")

    iterator = []
    for include in includes:
        params = add_extra_args_for_parallel(scenarios_args)
        params += f" -i {include}" if include != '' else ""
        params += f" -e \"{excludes}\"" if excludes else ""
        config = BehaveConfiguration(command_args=params, run_settings=settings)
        iterator.append((config, CustomModelRunner))

    logger.info('Features Files Included:')
    for include in includes:
        logger.info(f"--\t{include}")
    logger.info('-' * 50)

    if excludes:
        logger.info('Features Files Exclude:')
        for exclude in excludes.split(','):
            logger.info(f"--\t{exclude}")
        logger.info('-' * 50)

    return iterator


def run_features_parallel(parallel_args, run_args, pool, run_behave):
    """
    Run iterator for parallel executions for features
    :param parallel_args:
    :param run_args:
    :param pool:
    :param run_behave:
    :return:
    """
    logger.debug("Running iterator for features")
    iterator = get_features_iterator(parallel_args, run_args)
    with pool as process:
        results = process.starmap(run_behave, iterator)
        return results


def get_scenarios_from_tag(tags):
    """
    Get scenarios from tags
    :param tags:
    :return:
    """
    feature_locations = [filename for filename in collect_feature_locations([Settings.TEST_PATH.get(force=True)])]
    features = parse_features(feature_locations)

    scenarios = []
    for feature in features:
        if any(check in feature.tags for check in tags):
            for scenario in feature.scenarios:
                if isinstance(scenario, ScenarioOutline):
                    for _scenario in scenario.scenarios:
                        scenarios.append(_scenario.name)
                else:
                    scenarios.append(scenario.name)
        else:
            for scenario in feature.scenarios:
                if any(check in scenario.tags for check in tags):
                    if isinstance(scenario, ScenarioOutline):
                        for _scenario in scenario.scenarios:
                            scenarios.append(_scenario.name)
                    else:
                        scenarios.append(scenario.name)
                else:
                    # If any tag isn't included in the main scenario, then check the children scenarios tags
                    if isinstance(scenario, ScenarioOutline):
                        for _scenario in scenario.scenarios:
                            if any(check in _scenario.tags for check in tags):
                                scenarios.append(_scenario.name)
    try:
        if not scenarios:
            msg = 'There is no scenario with that expression. No scenario has been run.'
            print(msg)
            logger.warning(msg)
        else:
            logger.debug('The following scenarios have been obtained for parallel execution:')
            logger.debug(f'scenarios: {scenarios}')
        return scenarios
    except Exception:
        pass
