# -*- coding: utf-8 -*-

"""
Accessibility Generic Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the evidence files.

List of steps:
######################################################################################################################
## Actions Steps:
audit the page using the context <[css class or id]> arguments '<{"argument":"value"}>'
audit the page using the arguments '<(?P<arguments>.+)>'
audit the page within the elements '<(?P<elements>.+)>' excluding '<(?P<elements_excluded>.+)>'
audit the page using the arguments '<{"argument":"value"}> or [css class or id]'
audit the page within the elements <(?P<elements>.+)>
the current page should be audited for accessibility excluding the elements '<(?P<elements_excluded>.+)>'
reset axe configuration
the current page should be audited for accessibility
the current page must be free of accessibility errors
the current page must have only <number> accessibility errors
"""
from behave import step, use_step_matcher

from arc.contrib.accessibility import axe_utils
from arc.contrib.accessibility.axe_utils import evidence_accessibility_violations
from arc.contrib.accessibility.axe_wrapper import AxeWrapper
from arc.settings.settings_manager import Settings

import logging

logger = logging.getLogger(__name__)

use_step_matcher("re")

TITLE = 'Accessibility Results'


@step(u"audit the page using the context '(?P<axe_context>.+)' arguments '(?P<arguments>.+)'")
def audit_the_page_using_the_context_and_arguments(context, axe_context, arguments):
    """
    This method allow to audit a page using determined arguments.
    Example: audit the page using the context '(?P<axe_context>.+)' arguments '(?P<arguments>.+)'
    Where axe_context should be a string like #wrapper_id and arguments a should be a dict with key values
    :param context:
    :param axe_context:
    :param arguments:
    :return:
    """
    title = context.driver.title
    axe = AxeWrapper(context.driver)
    axe.inject()
    results = axe.run(context=axe_context, options=arguments)

    _, file_name = axe_utils.write_results(results, title)

    context.func.evidences.add_custom_table(
        TITLE,
        inapplicable=len(results['inapplicable']),
        incomplete=len(results['incomplete']),
        passes=len(results['passes']),
        violations=len(results['violations']),
        details=file_name
    )


@step(u"audit the page using the arguments '(?P<arguments>.+)'")
def audit_the_page_using_the_arguments(context, arguments):
    """
    This method allow to audit a page using determined arguments.
    Example: audit the page using the arguments '${{datas:arguments}}'
    Where arguments should be a string .
    :param context:
    :param arguments:
    :return:
    """
    title = context.driver.title
    axe = AxeWrapper(context.driver)
    axe.inject()
    results = axe.run(options=arguments)

    _, file_name = axe_utils.write_results(results, title)

    context.func.evidences.add_custom_table(
        TITLE,
        inapplicable=len(results['inapplicable']),
        incomplete=len(results['incomplete']),
        passes=len(results['passes']),
        violations=len(results['violations']),
        details=file_name
    )


@step(u"audit the page within the elements '(?P<elements>.+)' excluding '(?P<elements_excluded>.+)'")
def audit_the_page_within_the_elements_excluding(context, elements, elements_excluded):
    """
    This method allow to audit a page using determined arguments.
    Example: audit the page using the arguments '${{datas:elements}}' excluding '#button, #another_id'
    Where elements could be an array with some css classes or id to identify the element to audit
     and elements_excluded a string
    :param context:
    :param elements:
    :param elements_excluded:
    :return:
    """
    _elements = '{}'.format(elements)
    _elements_excluded = "{exclude: '%s'}" % elements_excluded
    audit_the_page_using_the_context_and_arguments(context, axe_context=_elements, arguments=_elements_excluded)


@step(u"audit the page within the elements '(?P<elements>.+)'")
def audit_the_page_within_the_elements(context, elements):
    """
    This method allow to audit a page using determined arguments.
    Example: audit the page using the arguments '${{datas:elements}}'
    Where elements should be a string like #id_item, .content-wrapper.
    :param context:
    :param elements:
    :return:
    """
    _elements = ['{}'.format(elements)]
    audit_the_page_using_the_arguments(context, arguments=_elements)


@step(u"the current page should be audited for accessibility excluding the elements '(?P<elements_excluded>.+)'")
def audit_the_page_excluding(context, elements_excluded):
    """
    This method allow to audit a page using determined arguments.
    Example: the current page should be audited for accessibility excluding the elements '#div_1, .another_wrapper'
    Where elements_excluded should be a string
    :param context:
    :param elements_excluded:
    :return:
    """
    _elements_excluded = "{exclude: '%s'}" % elements_excluded
    title = context.driver.title
    axe = AxeWrapper(context.driver)
    axe.inject()
    results = axe.run(document=True, options=_elements_excluded)

    _, file_name = axe_utils.write_results(results, title)

    context.func.evidences.add_custom_table(
        TITLE,
        inapplicable=len(results['inapplicable']),
        incomplete=len(results['incomplete']),
        passes=len(results['passes']),
        violations=len(results['violations']),
        details=file_name
    )


@step("reset axe configuration")
def reset_axe_configuration(context):
    """
    This step allow to reset the axe configuration.
    It does not return anything.
    :param context:
    :return:
    """
    axe = AxeWrapper(context.driver)
    axe.inject()
    axe.reset()
    logger.info("Axe configuration reset.")


@step(u"the current page should be audited for accessibility")
def the_current_page_should_be_audited_for_accessibility(context):
    """
    This step performs an accessibility audit analysis on the current page.
    In case of violation of any accessibility rule, it does not return an exception so the step does not fail.
    It generates the necessary evidence in the evidence documents.
    :example
        Then the current page should be audited for accessibility
    :
    :tag Accessibility Steps:
    :param context:
    """
    axe = AxeWrapper(context.driver)
    axe.inject()
    results = axe.run()
    if Settings.PYTALOS_ACCESSIBILITY.get("take_screenshot"):
        results = axe.take_screenshots_from_response(context, results)
    _, file_name = axe_utils.write_results(results, context.scenario.name)

    context.func.evidences.add_custom_table(
        TITLE,
        inapplicable=len(results['inapplicable']),
        incomplete=len(results['incomplete']),
        passes=len(results['passes']),
        violations=len(results['violations']),
        details=file_name
    )


@step(u"the current page must be free of accessibility errors")
def the_current_page_must_be_free_of_accessibility_errors(context):
    """
    This step performs an accessibility audit analysis on the current page.
    This step fails the test in case of any violation of any Accessibility rule.
    It generates the necessary evidence in the evidence documents.
    :example
        Then the current page must be free of accessibility errors
    :
    :tag Accessibility Steps:
    :param context:
    """
    title = context.driver.title  # noqa
    axe = AxeWrapper(context.driver)
    axe.inject()
    results = axe.run()
    _, file_name = axe_utils.write_results(results, title)

    violations = results['violations']
    current = len(violations)
    expected = 0
    error_msg = f"Found {len(violations)} accessibility violations"
    result = expected == current

    context.func.evidences.add_unit_table(
        TITLE,
        "Violations",
        current,
        expected,
        result,
        error_msg=error_msg,
        details=file_name

    )

    evidence_accessibility_violations(context, violations)
    assert result, axe_utils.report(violations)


@step(u"the current page must have only '(?P<number>.+)' accessibility errors")
def the_current_page_must_have_only_num_accessibility_errors(context, number):
    """
    This step performs an accessibility audit analysis on the current page.
    This step fails in the event that the number of violations of accessibility rules is equal to the number
    passed by parameter.
    It generates the necessary evidence in the evidence documents.
    :example
        Then the current page must have only '3' accessibility errors
    :
    :tag Accessibility Steps:
    :param context:
    :param number:
    """
    title = context.driver.title  # noqa
    axe = AxeWrapper(context.driver)
    axe.inject()
    results = axe.run()
    _, file_name = axe_utils.write_results(results, title)

    violations = results['violations']
    current = len(violations)
    expected = int(number)
    error_msg = f"Found {len(violations)} accessibility violations"
    result = expected == current

    context.func.evidences.add_unit_table(
        'Accessibility Results',
        "Violations",
        current,
        expected,
        result,
        error_msg=error_msg,
        details=file_name
    )

    if result is False:
        evidence_accessibility_violations(context, violations)

    assert result, axe_utils.report(violations)
