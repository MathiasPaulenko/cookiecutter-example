# -*- coding: utf-8 -*-
"""
Class and functions of utilities and context support.
"""

import six # NOQA
import re
import logging

from behave.runner import Context as _Context

from arc.core.behave.template_var import get_template_var_value
from arc.core.test_method.exceptions import TalosRunError
from arc.core.test_method.visual_test import VisualTest
from arc.integrations.alm import Alm
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


class Context(_Context):
    """
        This Context class overrides the original Context class from Behave in order to have additional behaviour in
        Talos BDD
    """

    def __init__(self, runner):
        super().__init__(runner)
        self.parent_steps_list = {}
        self.original_step = None
        self.last_original_step = None
        self.alm = Alm(self)

    def execute_steps(self, steps_text):
        """The steps identified in the "steps" text string will be parsed and
        executed in turn just as though they were defined in a feature file.

        If the execute_steps call fails (either through error or failure
        assertion) then the step invoking it will need to catch the resulting
        exceptions.

        :param steps_text:  Text with the Gherkin steps to execute (as string).
        :returns: True, if the steps executed successfully.
        :raises: AssertionError, if a step failure occurs.
        :raises: ValueError, if invoked without a feature context.
        """
        logger.debug("Executing sub steps")
        assert isinstance(steps_text, six.text_type), "Steps must be unicode."
        if not self.feature:
            raise ValueError("execute_steps() called outside of feature")


        # -- PREPARE: Save original context data for current step.
        # Needed if step definition that called this method uses .table/.text
        original_table = getattr(self, "table", None)
        original_text = getattr(self, "text", None)

        self.feature.parser.variant = "steps"
        steps_text = self.__parse_examples(steps_text)
        steps = self.feature.parser.parse_steps(steps_text)
        # Save the parent evidence object.
        original_evidences = self.func.evidences

        # If the last original step is the same as the current step then use the original step
        if self.last_original_step is not None:
            if self.last_original_step.name == self.runtime.step.name:
                self.original_step = self.runtime.step
            else:
                self.original_step = None
        # Save the original parent step so when someone run this method in a for loop the results aren't crazy
        if self.original_step is None:
            self.runtime.step.sub_steps = []
            self.runtime.scenario.sub_steps = []
            self.original_step = self.runtime.step
            self.last_original_step = self.runtime.step
        self.parent_steps_list.setdefault(self.scenario.name, []).append(self.original_step.name)
        for step in steps:
            # If the step name is in the parent steps list then raise an Exception to avoid
            # a stack overflow error due to recursion.
            if step.name in self.parent_steps_list.get(self.scenario.name):
                raise TalosRunError(f"Error: sub step '{self.runtime.step.name}' calling superior step: '{step.name}' "
                                    f"in scenario '{self.scenario.name}'. "
                                    f"Remove any call of superior steps in the sub steps.")
            if self._runner.step_registry.find_match(step):
                self.runtime.step.sub_steps.append(step)
                step.parent_step = self.runtime.step

        with self._use_with_behave_mode():
            for step in steps:
                logger.debug(f"Executing sub step {step.name}")
                print(u"\t\t%s %s" % (step.keyword, step.name))
                passed = step.run(self._runner, quiet=True, capture=True)
                if not passed:
                    logger.debug(f"Sub step failed {step.name}")
                    # -- ISSUE #96: Provide more substep info to diagnose problem.
                    step_line = u"%s %s" % (step.keyword, step.name)
                    message = "\r%s SUB-STEP: %s" % \
                              (step.status.name.upper(), step_line)
                    if step.error_message:
                        message += "\nSubstep info: %s\n" % step.error_message
                    self.original_step.status = self.original_step.status.failed
                    if not Settings.PYTALOS_RUN.get('continue_after_failed_step'):
                        assert False, message
                logger.debug(f"Sub step success {step.name}")

            # -- FINALLY: Restore original context data for current step.
            self.table = original_table
            self.text = original_text
            if Settings.PYTALOS_REPORTS.get("include_sub_steps_in_results", default=False):
                self.func.evidences = original_evidences
        # When sub step finish, then clean the parent_steps_list index
        # in order to allow to execute the same steps if needed
        self.parent_steps_list[self.scenario.name] = []
        # When finished the sub step set the original step as the runtime step
        # So when someone run this method in a for loop the results aren't crazy
        self.runtime.step = self.original_step
        self.original_step = None
        return True

    def __parse_examples(self, steps_text):
        """
            This method parse the example tables of the scenarios in sub steps.
            Allowing to use template vars in example tables of sub steps.
        :param steps_text:
        :type steps_text:
        """
        regex_table = r"<(.*?)>"
        matchers_profiles = re.findall(regex_table, steps_text)
        for match in matchers_profiles:
            _value = get_template_var_value(self.active_outline[match])
            steps_text = steps_text.replace(f"<{match}>", _value)
            logger.debug(f"Parsed example table {match} with value {_value}")
        return steps_text

    def assert_screenshot(self, element_or_selector, filename, threshold=0, exclude_elements=None, driver_wrapper=None,
                          force=False):
        """
        Comparing a screenshot to an element or selector.
        :param element_or_selector:
        :param filename:
        :param threshold:
        :param exclude_elements:
        :param driver_wrapper:
        :param force:
        :return:
        """
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(driver_wrapper, force).assert_screenshot(
            element_or_selector,
            filename,
            self.runtime.scenario.name,
            threshold,
            exclude_elements
        )

    def assert_full_screenshot(self, filename, threshold=0, exclude_elements=None, driver_wrapper=None, force=False):
        """
        Comparison of a full screenshot.
        :param filename:
        :param threshold:
        :param exclude_elements:
        :param driver_wrapper:
        :param force:
        :return:
        """
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(driver_wrapper, force).assert_screenshot(
            None,
            filename,
            self.runtime.scenario.name,
            threshold,
            exclude_elements
        )


class PyTalosContext:
    """
        Utility class for storing Talos core information and configurations within the context.
        """
    """
    Utility class for storing Talos core information and configurations within the context.
    """
    context: None

    def __init__(self, context):
        self.context = context


class RuntimeDatas:
    """
    Utility class for storing run time information within the context.
    """
    context = None

    def __init__(self, context):
        self.context = context


class TestData:
    """
    Utility class for storing test data information within the context.
    """
    context = None

    def __init__(self, context):
        self.context = context
