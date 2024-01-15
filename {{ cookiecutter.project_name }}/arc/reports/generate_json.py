# -*- coding: utf-8 -*-
"""
Module for generating json files with the information required by the ALM connector from the Talos alm config CSV
and test execution data.
"""
import json as j
import logging
import os
import datetime
import re

from arc.contrib.tools.formatters import replace_chars
from arc.reports.csv_formmater import CSVFormatter
from arc.reports.html.utils import BASE_DIR
from arc.settings.settings_manager import Settings
from arc.reports.html.utils import get_short_name
from arc.core.behave.template_var import replace_template_var

logger = logging.getLogger(__name__)

JSON_PATH = os.path.join(Settings.OUTPUT_PATH.get(), 'json/input/')


class GenerateJson:
    """
    Class of generation of the json files for the ALM connector.
    """
    alm = {}
    json_name = ''
    scenario_name = ''
    csv: CSVFormatter
    csv_data = {}
    csv_heading = []
    step_controller = []
    step_dict = {}
    step_cont = 0
    cd = datetime.datetime.now()
    path_list = []
    location_scenario = ""

    def __init__(self, scenario):
        self.csv = CSVFormatter()
        self.set_csv_data_config(scenario)
        self.set_alm_part()
        self.set_tc_part()
        self.set_ts_part()
        self.step_controller = []
        self.step_dict = {}
        self.extra_step_data = {}
        self.extra_run_info = {}
        self.extra_attach = []

    def generate_json_after_scenario(self, scenario, driver, generate_html_report, generate_docx_report,
                                     generate_pdf_report):
        """
        Generate json data after scenario execution.
        this part contain run data information about scenario executed and finish json.
        :param scenario:
        :param driver:
        :param generate_html_report:
        :param generate_docx_report:
        :param generate_pdf_report:
        :return:
        """
        self.set_scenario_steps(scenario.steps)
        self.add_skipped_steps(scenario)
        self.set_run_part(scenario, driver, generate_html_report, generate_docx_report, generate_pdf_report)
        self.finish_json()

    def set_names(self, scenario):
        """
        Set feature name and scenario name.
        :param scenario:
        :return:
        """
        self.set_feature_name(scenario)
        self.set_scenario_name(scenario)

    def set_feature_name(self, scenario):
        """
        Set feature name from scenario.
        :param scenario:
        :return:
        """
        _ = self.csv.format_feature_name(scenario)
        aux = re.sub('[-#%<>@ ]', "", scenario.name)
        aux = re.sub('[.]', "-", aux)
        self.json_name += aux + f"_{str(datetime.datetime.now()).replace('-', '').replace(' ', '')}"
        self.json_name = self.json_name.replace(" ", "-")

    def set_scenario_name(self, scenario):
        """
        Set scenario name from scenario.
        :param scenario:
        :return:
        """
        self.csv.set_scenario_data(scenario)
        self.scenario_name = self.csv.tc_scenario_name

    def set_csv_data_config(self, scenario):
        """
        Get csv config file information.
        :param scenario:
        :return:
        """
        self.set_names(scenario)
        self.csv_data = self.csv.get_final_data()
        self.step_cont = 0

    def set_alm_part(self):
        """
        Set mandatory ALM data part from csv.
        :return:
        """
        self.alm['alm-access'] = [self.csv_data[1]]

    def set_tc_part(self):
        """
        Set test case data part from csv.
        :return:
        """
        self.alm['test-case'] = [self.csv_data[2]]

    def set_ts_part(self):
        """
        Set test set data part from csv.
        :return:
        """
        self.alm['test-set'] = [self.csv_data[3]]

    def set_run_part(self, scenario, driver, generate_html_report, generate_docx_report, generate_pdf_report):
        """
        Set run data part from csv and execution.
        :param scenario:
        :param driver:
        :param generate_html_report:
        :param generate_docx_report:
        :param generate_pdf_report:
        :return:
        """
        if str(scenario.status) == 'Status.passed':
            result = "Passed"
        elif str(scenario.status) == "Status.failed":
            result = "Failed"
        else:
            result = "Skipped"
        self.alm['run'] = []
        self.alm['run'].append({
            "run-exec-date": str(self.cd.day) + "/" + str(self.cd.month) + "/" + str(self.cd.year),
            "run-exec-time": str(self.cd.hour) + ":" + str(self.cd.minute) + ":" + str(self.cd.second),
            "run-status": result,
            "run-duration": str(round(scenario.duration, 2)),
        })
        if Settings.PYTALOS_ALM.get('scenario_name_as_run_name'):
            self.alm['run'][0]['run-name'] = self.alm['test-case'][0]['tc-name']
        attach = 1
        if generate_html_report:
            name = replace_template_var(scenario.name)
            name = '%.100s' % name
            scenario_name = replace_chars(name)
            path = str(
                f"{BASE_DIR}/output/reports/html/scenario_{scenario_name}.html").replace('/', os.sep)
            path = self.check_path(path, scenario.location)
            self.path_list.append(path)

            path = str(
                f"{BASE_DIR}/output/scenario_{scenario_name}.zip").replace('/', os.sep)
            self.alm['run'][0]['run-attach-' + str(attach)] = path
            attach = attach + 1
        name = replace_chars(replace_template_var(scenario.name))
        name = '%.100s' % name
        scenario_name = replace_chars(name)
        if generate_docx_report:
            path = str(
                f"{BASE_DIR}/output/reports/doc/{driver}-{scenario_name}.docx").replace('/', os.sep)
            path = self.check_path(path, scenario.location)
            self.path_list.append(path)
            self.alm['run'][0]['run-attach-' + str(attach)] = path
            attach = attach + 1
        if generate_pdf_report:
            path = str(
                f"{BASE_DIR}/output/reports/pdf/{driver}-{scenario_name}.pdf").replace('/', os.sep)
            path = self.check_path(path, scenario.location)
            self.path_list.append(path)
            self.alm['run'][0]['run-attach-' + str(attach)] = path
        if self.extra_attach:
            for attach_file in self.extra_attach:
                if os.path.exists(attach_file):
                    self.alm['run'][0]['run-attach-' + str(attach)] = attach_file
                    attach += 1
        if len(self.extra_run_info) > 0:
            self.alm['run'][0].update(self.extra_run_info)

        if len(self.extra_run_info) > 0:
            self.alm['run'][0].update(self.extra_run_info)

    def check_path(self, path, location):
        if path in self.path_list:
            basename, ext = os.path.splitext(path)
            path = basename + f"_{location.line}" + ext
            self.location_scenario = location.line
        else:
            self.location_scenario = ""
        return path

    def add_skipped_steps(self, scenario):
        """
            This method loop the scenario steps looking for skipped steps and then
            call the method set_step passing the skipped step in order to add it to the
            json file generated in run time.
        :param scenario:
        """
        for step in scenario.steps:
            if step.status.name == 'skipped':
                self.set_step(step)

    def set_scenario_steps(self, steps):
        """
        Add the steps to the json data and check for the sub steps too.
        :param steps:
        :return:
        """
        for step in steps:
            self.set_step(step)
            if hasattr(step, 'sub_steps') and step.sub_steps:
                self.set_scenario_steps(step.sub_steps)

    def set_step(self, step):
        """
        Set step data.
        :param step:
        :return:
        """
        date_time = datetime.datetime.now()
        self.step_cont += 1
        if str(step.status) == 'Status.passed':
            if step.obtained_result_passed:
                obt_result = str(step.obtained_result_passed).replace("'", "")
            else:
                obt_result = "Operation with correct result"
            result = "Passed"
        elif str(step.status) == "Status.failed":
            if step.obtained_result_failed:
                obt_result = str(step.obtained_result_failed).replace("'", "")
            else:
                obt_result = "Operation with incorrect result"
            result = "Failed"
        else:
            if hasattr(step, 'obtained_result_skipped'):
                obt_result = str(step.obtained_result_skipped).replace("'", "")
            else:
                obt_result = "Operation without result"

            result = "No Run"

        if hasattr(step, 'result_expected') and step.result_expected:
            result_expected = str(step.result_expected).replace("'", "")
        else:
            result_expected = str(step.name).replace("<", "").replace(">", "")

        step_description = str(step.name).replace("<", "").replace(">", "").replace("'", "").replace("\"", "")

        self.step_dict = {
            "step-number": "Step " + str(self.step_cont),
            "step-descrip": str(step.keyword) + " " + str(step_description),
            "step-exp-res": str(result_expected),
            "step-obt-res": obt_result,
            "step-exec-stat": result,
            "step-exec-date": str(date_time.day) + "/" + str(date_time.month) + "/" + str(date_time.year),
            "step-exec-time": str(round(step.duration, 2))
        }

        if len(self.extra_step_data) > 0:
            self.step_dict.update(self.extra_step_data)
            self.extra_step_data = {}

        self.step_controller.append(self.step_dict)
        self.alm['steps'] = self.step_controller

    def finish_json(self):
        """
        Finish json generation file.
        :return:
        """
        self.json_name = get_short_name(self.json_name)
        path = os.path.join(JSON_PATH, f"{self.json_name}{self.location_scenario}" + '.json')
        logger.debug(f'ALM json file generated in: {path}')
        with open(path, 'w', encoding='utf-8') as outfile:
            j.dump(self.alm, outfile, ensure_ascii=False)
