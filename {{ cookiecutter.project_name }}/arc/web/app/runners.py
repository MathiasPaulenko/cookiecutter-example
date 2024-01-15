import os
from multiprocessing.pool import ThreadPool
from arc.core.behave.runner import make_behave_argv, main
from arc.reports.custom_formatters import get_json_report_args_for_portal


def execute_feature(feature: str, conf_file: str):
    """
    This function receives a feature name and a conf_file name.
    Prepare the arguments and then execute the main function for Talos_BDD also, send a copy of the current environ
    variables
    :param feature:
    :param conf_file:
    :return:
    """
    params = make_behave_argv(includes=[f"{feature}.feature"], conf_properties=conf_file)
    params += get_json_report_args_for_portal()
    myenv = os.environ.copy()
    pool = ThreadPool(1)
    with pool as process:
        results = process.starmap(main, [(params, myenv)])
        return results


def execute_features(features, conf_file: str):
    """
    This function receives multiple feature names and a conf_file name.
    Prepare the arguments and then execute the main function for Talos_BDD also, send a copy of the current environ
    variables
    :param features:
    :param conf_file:
    :return:
    """
    params = make_behave_argv(includes=features, conf_properties=conf_file)
    params += get_json_report_args_for_portal()
    myenv = os.environ.copy()
    pool = ThreadPool(1)
    with pool as process:
        results = process.starmap(main, [(params, myenv)])
        return results


def execute_by_tags(tags: str, conf_file: str, params: str):
    """
    This function receives a str of tags, a conf_file and a string of params
    Prepare the arguments and then execute the main function for Talos_BDD also, send a copy of the current environ
    variables
    :param tags:
    :param conf_file:
    :param params:
    :return:
    """
    params += make_behave_argv(tags=tags, conf_properties=conf_file)
    params += get_json_report_args_for_portal()
    myenv = os.environ.copy()
    pool = ThreadPool(1)
    with pool as process:
        results = process.starmap(main, [(params, myenv)])
        return results


def execute_by_scenario_names(scenario_names: list, conf_file: str, params: str):
    """
    This function receives a str of scenario names, a conf_file and a string of params
    Prepare the arguments and then execute the main function for Talos_BDD also, send a copy of the current environ
    variables
    :param scenario_names:
    :param conf_file:
    :param params:
    :return:
    """
    params += make_behave_argv(scenario_names=scenario_names, conf_properties=conf_file)
    params += get_json_report_args_for_portal()
    myenv = os.environ.copy()
    pool = ThreadPool(1)
    with pool as process:
        results = process.starmap(main, [(params, myenv)])
        return results
