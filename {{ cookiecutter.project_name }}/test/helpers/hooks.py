# -*- coding: utf-8 -*-
"""
TalosBDD users hooks.
In this file, the hooks are executed in sequential order according to the execution time.
The order of execution of the hooks are:
 - before execution
 - before all
 - before feature
 - before scenario
  - before_tag
 - before step
 - after step
 - after scenario
 - after feature
 - after_tag
 - after all
 - after execution
"""


def before_execution():
    """Clean method that will be executed before execution is finished"""
    pass


def before_all(context):
    """Initialization method that will be executed before the test execution
    :param context: behave context
    """


def before_feature(context, feature):
    """Feature initialization
    :param context: behave context
    :param feature: running feature
    """


def before_scenario(context, scenario):
    """Scenario initialization
    :param context: behave context
    :param scenario: running scenario
    """


def after_scenario(context, scenario):
    """Clean method that will be executed after each scenario
    :param context: behave context
    :param scenario: running scenario
    """


def after_feature(context, feature):
    """Clean method that will be executed after each feature
    :param context: behave context
    :param feature: running feature
    """


def after_all(context):
    """Clean method that will be executed after all features are finished
    :param context: behave context
    """


def before_step(context, step):
    """Clean method that will be executed before step are finished
    :param step:
    :param context: behave context
    """


def after_step(context, step):
    """Clean method that will be executed after step are finished
    :param step:
    :param context: behave context
    """


def before_tag(context, tag):
    """Clean method that will be executed before tag are finished
    :param context:
    :param tag:
    :return:
    """


def after_tag(context, tag):
    """Clean method that will be executed fter tag are finished
    :param context:
    :param tag:
    :return:
    """


def after_execution(context):
    """Clean method that will be executed after execution is finished"""
    pass


def before_reports(json_data):
    """Clean method that will be executed before reports generations"""
    pass
