# -*- coding: utf-8 -*-
"""
Environment core file
In this file, the hooks are executed in sequential order according to the execution time.
In each hook the necessary actions are made so that the framework performs its functionalities.
The order of execution of the hooks are:
 - before execution
 - before all
 - before feature
 - before scenario
 - before step
 - after step
 - after scenario
 - after feature
 - after all
 - after execution
"""
import logging

from arc.core.behave.env_utils import (
    utils_after_scenario,
    utils_after_all,
    utils_before_all,
    utils_before_feature,
    utils_after_feature,
    utils_before_scenario
)

try:
    from behave_pytest.hook import install_pytest_asserts
except ImportError:
    def install_pytest_asserts():  # noqa
        pass

logger = logging.getLogger(__name__)


def before_all(context):
    """
    Functions that are executed before anything of the tests.
    """
    install_pytest_asserts()
    utils_before_all(context)
    logger.debug(f"The core before all actions have been executed correctly")


def before_feature(context, feature):
    """
    Functionalities that are executed before the execution of the features.
    :param context:
    :param feature:
    """
    utils_before_feature(context, feature)
    logger.debug(f"The core before feature actions have been executed correctly")


def before_scenario(context, scenario):
    """
    Functionalities that are executed before the execution of the scenarios.
    :param context:
    :param scenario:
    """
    utils_before_scenario(context, scenario)
    logger.debug(f"The core before scenario actions have been executed correctly")


def after_scenario(context, scenario):
    """
    Functionalities that are executed after the execution of the scenarios.
    :param context:
    :param scenario:
    """
    utils_after_scenario(context, scenario, scenario.status)
    logger.debug(f"The core after scenario actions have been executed correctly")


def after_feature(context, feature):
    """
    Functionalities that are executed after the execution of the features.
    :param context:
    :param feature:
    """
    utils_after_feature(context, feature)
    logger.debug(f"The core after feature actions have been executed correctly")


def after_all(context):
    """
    Functions that are executed after anything of the tests.
    :param context:
    """
    utils_after_all(context)
    logger.debug(f"The core after all actions have been executed correctly")
