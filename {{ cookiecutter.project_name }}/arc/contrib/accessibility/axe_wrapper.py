# -*- coding: utf-8 -*-
"""
Control for the management and call of accessibility tests with Axe.
This module makes use of Axe Core JS to perform the analysis of Accessibility tests.
To perform the requirements and run the analysis, use the axe.min library.js located at resources/modules/axe-core.

Its operation is done by JS script executions of the library mentioned above to the browser through the execute_script
function of Selenium.
"""
import logging
import os
from io import open


from selenium.webdriver.common.by import By
from arc.page_elements import Group
from selenium.common import JavascriptException

from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

_DEFAULT_SCRIPT = os.path.join(
    Settings.RESOURCES_PATH.get(force=True), "modules", "axe-core", "axe.min.js"
)


class AxeWrapper(object):
    """
    Wrapper de Axe Core JS. Functions for the execution of JS scripts and report generation.
    """

    def __init__(self, driver, script_url=_DEFAULT_SCRIPT):
        self.script_url = script_url
        self.driver = driver

    def inject(self):
        """
        Reading the axe-core.js and obtaining the functions.
        If the axe tools is already injected then don't re inject the library.
        """
        logger.info('Trying to inject axe js')
        try:
            self.driver.execute_script('axe')
        except JavascriptException as e:
            if 'axe is not defined' in e.msg:
                with open(self.script_url, "r", encoding="utf8") as f:
                    self.driver.execute_script(f.read())
                    logger.info(f'Axe script injected: {self.script_url}')
            else:
                logger.error(e.msg)
                raise e

    def run(self, document=False, context=None, options=None):
        """
        Function of execution of the scripts according to the configuration of the context and the
        options passed by parameter.
        :param document:
        :param context:
        :param options:
        """
        template = (
                "var callback = arguments[arguments.length - 1];"
                + "axe.run(%s).then(results => callback(results))"
        )
        args = ""
        if document:
            args += "%s" % "document"
            if options is not None:
                args += ",%s" % options
        else:
            # If context parameter is passed, add to args
            if context is not None:
                args += "%r" % context
            # Add comma delimiter only if both parameters are passed
            if context is not None and options is not None:
                args += ","
            # If options parameter is passed, add to args
            if options is not None:
                args += "%s" % options

        command = template % args
        logger.info(f'Execution Axe with commands: {command}')
        response = self.driver.execute_async_script(command)
        logger.debug('Response from Axe execution received')
        return response

    def get_rules(self, rule='None'):
        """
        Returns Axe Core rules to be used in script execution options.
        :param rule:
        """
        if rule is None:
            rule = []

        if type(rule) is str:
            command = f"return axe.getRules(['{rule}']);"
        elif type(rule) is list:
            command = f"return axe.getRules({rule});"
        else:
            return
        response = self.driver.execute_async_script(command)
        logger.debug(f"Accessibility rules obtained: {response}")
        return response

    @staticmethod
    def take_screenshots_from_response(context, response):
        """
            This method take the response and then make a screenshot of the element with a violation rule.
            If the element is visible, then take the screenshot and include it in the report.
        :param context:
        :param response:
        :return:
        """
        for violation in response['violations']:
            for node in violation['nodes']:
                try:
                    element = Group(By.CSS_SELECTOR, node['target'][0])
                    element.scroll_element_into_view()
                    if element.is_visible():
                        original_style = context.utilities.highlight_element(element)
                        node['screenshot'] = context.utilities.capture_screenshot(
                            f"{str(context.runtime.step.name)}_{str(violation['id'])}"
                        )
                        context.utilities.unhighlight_element(element, original_style)
                except (Exception, ) as ex:
                    logger.warning(ex)
        for incomplete in response['incomplete']:
            for node in incomplete['nodes']:
                try:
                    element = Group(By.CSS_SELECTOR, node['target'][0])
                    element.scroll_element_into_view()
                    if element.is_visible():
                        original_style = context.utilities.highlight_element(element)
                        node['screenshot'] = context.utilities.capture_screenshot(
                            f"{str(context.runtime.step.name)}_{str(incomplete['id'])}"
                        )
                        context.utilities.unhighlight_element(element, original_style)
                except (Exception, ) as ex:
                    logger.warning(ex)
        return response


    def configure(self, config: dict):
        """
        This method allow to configure the format of the data used by axe.
        This can be used to add new rules, which must be registered with the library to execute.
        Check documentation: https://github.com/dequelabs/axe-core/blob/develop/doc/API.md#purpose-1
        Dict example:
        {
          branding: String,
          reporter: 'option' | Function,
          checks: [Object],
          rules: [Object],
          standards: Object,
          locale: Object,
          axeVersion: String,
          disableOtherRules: Boolean,
          noHtml: Boolean
        }
        :param config:
        :return:
        """
        command = f"return axe.configure({str(config)});"
        response = self.driver.execute_async_script(command)
        logger.debug(f"Trying to set axe configuration with result: {response}")
        return response

    def reset(self):
        """
        This method reset the axe configuration.
        :return:
        """
        response = self.driver.execute_async_script("return axe.reset();")
        logger.debug(f"Trying to reset axe configuration with result: {response}")
        return response
