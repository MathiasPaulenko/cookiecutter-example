# -*- coding: utf-8 -*-
"""
Integration module with MF ALM.
It contains all the necessary functions for run the ALM connector.
"""
import inspect
import logging
import os
import shutil
from subprocess import call

from arc.core.test_method.exceptions import TalosRunError
from arc.settings.settings_manager import Settings
from zipfile import ZipFile

JSON_INPUT_PATH = os.path.abspath("output") + os.sep + 'json' + os.sep + 'input' + os.sep

logger = logging.getLogger(__name__)


class Alm(object):
    """
        This class is used to modify anc interact with the alm json generated in every scenario.
    """
    def __init__(self, context):
        self.context = context

    def add_alm_step_info(self, key=None, value=None, data=None):
        """
            Add extra data to the steps
            Only in steps and after steps.
        :param key:
        :param value:
        :param data:
        :return:
        """
        self._check_caller_function(['after_step', 'before_step'])
        if Settings.PYTALOS_ALM.get('generate_json'):
            if data:
                self.context.runtime.alm_json.extra_step_data.update(data)
            else:
                self.context.runtime.alm_json.extra_step_data[key] = value

    def add_alm_ts_info(self, key=None, value=None, data=None):
        """
            Add extra data to the test-set section
        :param key:
        :param value:
        :param data:
        :return:
        """
        self._check_caller_function(['after_scenario'])
        if Settings.PYTALOS_ALM.get('generate_json'):
            if data:
                self.context.runtime.alm_json.alm['test-set'][0].update(data)
            else:
                self.context.runtime.alm_json.alm['test-set'][0][key] = value

    def add_alm_tc_info(self, key=None, value=None, data=None):
        """
            Add extra data to the test-case section
        :param key:
        :param value:
        :param data:
        :return:
        """

        self._check_caller_function(['after_scenario'])
        if Settings.PYTALOS_ALM.get('generate_json'):
            if data:
                self.context.runtime.alm_json.alm['test-case'][0].update(data)
            else:
                self.context.runtime.alm_json.alm['test-case'][0][key] = value

    def add_alm_general_info(self, key=None, value=None, data=None):
        """
            Add extra data to the run section
        :param key:
        :param value:
        :param data:
        :return:
        """

        self._check_caller_function(['after_scenario'])
        if Settings.PYTALOS_ALM.get('generate_json'):
            if data:
                self.context.runtime.alm_json.extra_run_info.update(data)
            else:
                self.context.runtime.alm_json.extra_run_info[key] = value

    def add_alm_access_info(self, key=None, value=None, data=None):
        """
            Add extra data or update to the alm-access section
        :param key:
        :param value:
        :param data:
        :return:
        """
        self._check_caller_function(['after_scenario'])
        if Settings.PYTALOS_ALM.get('generate_json'):

            if data:
                self.context.runtime.alm_json.alm['alm-access'][0].update(data)
            else:
                self.context.runtime.alm_json.alm['alm-access'][0][key] = value
    
    @staticmethod
    def _check_caller_function(caller: list):
        """
            Check if the execution is called from any function in the caller list or from a step.
            If not, then raise a TalosRunError
        :param caller:
        :return:
        """
        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame, 2)
        if caller_frame[1][3] == 'add_alm_step_info':
            if caller_frame[2][1].__contains__('steps') is False and caller_frame[2][3] not in caller:
                raise TalosRunError(error_msg=f"You can't use the method '{caller_frame[1][3]}' in function or hook"
                                              f" '{caller_frame[2][3]}' only in the following functions/hooks {caller}"
                                              f" or in steps functions")
        elif caller_frame[2][3] not in caller:
            raise TalosRunError(error_msg=f"You can't use the method '{caller_frame[1][3]}' in function or hook"
                                          f" '{caller_frame[2][3]}' only in the following functions/hooks {caller}")

    def add_alm_attachment(self, attach):
        self.context.runtime.alm_json.extra_attach.append(attach)


def alm3_properties(flag):
    """
    Check if alm3 properties is enabled. Then, copy alm.properties to json input folder.
    :param flag:
    :return:
    """
    alm_file = 'alm3.properties'
    if flag:
        logger.info('ALM3 properties is enabled')
        alm_prop = os.path.join(Settings.INTEGRATIONS_PATH.get(force=True), alm_file)
        shutil.copy(alm_prop, JSON_INPUT_PATH)
    else:
        alm_json_path = os.path.join(JSON_INPUT_PATH, alm_file)
        if os.path.isfile(alm_json_path):
            os.remove(alm_json_path)


def run_alm_connect(attach_files):
    """
    Run ALM connect process.
    :return:
    """
    if Settings.PYTALOS_ALM.get('post_to_alm'):
        if Settings.PYTALOS_ALM.get('attachments').get('html'):
            compress_html_report(attach_files)
        logger.info('Running ALM connect')
        jar_path = 'arc/resources/'
        json_path = 'output/json/'
        alm3_properties(Settings.PYTALOS_ALM.get('alm3_properties'))
        call(['java', '-jar', jar_path + 'talos-connect-6.0.0.jar', json_path])


def compress_html_report(attach_files):
    for key, value in attach_files.items():
        name = f"output{key.split('output')[1]}"

        zip_name = name.replace('.html', '.zip').replace('reports/html/', '')

        with ZipFile(zip_name, mode="w") as archive:
            archive.write(
                name,
                arcname=name
            )
            for screenshot in value:
                screenshot_path = f"output{screenshot.split('output')[1]}"
                if Settings.PYTALOS_REPORTS.get('compress_screenshot'):
                    screenshot_path = screenshot_path.replace('screenshots', 'reports\\html\\assets\\imgs')
                    index = screenshot_path.rfind(os.sep)
                    img_name = screenshot_path[index:]
                    screenshot_path = f"{screenshot_path.split('imgs')[0]}imgs{img_name}"
                    screenshot_path = screenshot_path.replace('.png', '.webp')
                archive.write(
                    screenshot_path,
                    arcname=screenshot_path
                )
