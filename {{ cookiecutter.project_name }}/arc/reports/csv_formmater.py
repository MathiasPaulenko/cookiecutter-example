# -*- coding: utf-8 -*-
"""
Module for obtaining and converting CSV data from the ALM connector.
"""
import csv
import datetime
import logging
import os
from arc.contrib.tools import formatters
from arc.core.behave.template_var import replace_template_var
from arc.core.test_method.exceptions import TalosErrorReadFile
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

EXCEL_HOME = os.path.join(Settings.INTEGRATIONS_PATH.get(force=True), 'talosbdd-alm-config.csv')


class CSVFormatter:
    """
    Class that gets and formats the static information from the ALM connector's data collection csv for
    JSON generation.
    """
    feature_name = ''
    tc_scenario_name = ""
    results = []
    csv_data = {}
    final_data = {}
    scenario = ''
    settings = None
    tc_name_list = []

    def __init__(self):
        self.csv_data = self.get_csv_data()

    @staticmethod
    def get_csv_data():
        """
        Return data from csv.
        """
        results = []
        try:
            with open(EXCEL_HOME, encoding='utf-8') as File:
                logger.debug(f'Reading talos alm config csv: {EXCEL_HOME}')
                reader = csv.reader(
                    File, delimiter=';', quotechar=',',
                    quoting=csv.QUOTE_MINIMAL
                )
                for row in reader:
                    results.append(row)
        except FileNotFoundError as e:
            raise TalosErrorReadFile("Can't find file 'talosbdd-alm-config.csv'."
                                     " Please move the file 'talosbdd-alm-config.csv'"
                                     " from /settings/ to /settings/integrations/")

        alm = []
        for s in results[0]:
            alm.append(s)

        data = []
        for x in range(1, results.__len__()):
            alm_values = []
            for s in results[x]:
                alm_values.append(s)
            dictionary = {}
            for y in range(0, len(results[x])):
                dictionary[alm[y]] = alm_values[y]
            data.append(dictionary)
        return data

    def format_feature_name(self, scenario):
        """
        Return feature name formatted.
        """
        msg_modify = scenario.feature.filename.replace("test/features/", "")
        msg_modify = msg_modify.replace(".feature", "")
        self.scenario = scenario
        self.feature_name = msg_modify
        return msg_modify

    def set_scenario_data(self, scenario):
        """
        Set scenario name.
        """
        self.tc_scenario_name = '%.100s' % str(replace_template_var(scenario.name)).strip()

    def get_csv_heading(self):
        """
        Return csv headers.
        """
        return self.csv_data[0]

    def alm_option_controller(self):
        """
        This function controls the csv logic options according to the scenario column, feature or default row.
        """
        try:
            base = self.csv_data[0]
            if self.csv_data.__len__() == 1:
                base['feature-file'] = self.feature_name
                base['scenario'] = self.tc_scenario_name
                self.final_data = base

            if self.csv_data.__len__() > 1:
                for option in self.csv_data:
                    if option.get('feature-file') == '':
                        base['feature-file'] = self.feature_name
                        base['scenario'] = self.tc_scenario_name
                        for index in option:
                            if option.get(index) == '':
                                self.final_data[index] = base[index]
                            else:
                                self.final_data[index] = option[index]
                    elif option.get('feature-file') == self.feature_name and option.get('scenario') == '':
                        base['scenario'] = self.tc_scenario_name
                        for index in option:
                            if option.get(index) == '':
                                self.final_data[index] = base[index]
                            else:
                                self.final_data[index] = option[index]
                    elif option.get('feature-file') == self.feature_name and option.get(
                            'scenario') == self.tc_scenario_name:
                        for index in option:
                            if option.get(index) == '':
                                self.final_data[index] = base[index]
                            else:
                                self.final_data[index] = option[index]

        except (Exception,) as ex:
            logger.warning(ex)
            logger.warning('Please, fill in the ALM configuration csv properly')

        logger.debug(f'Data obtained from the CSV of Talos alm config: {self.final_data}')
        return self.final_data

    def csv_con_needed_data(self):
        """
        Return all needed data from csv.
        """
        cd = datetime.datetime.now()
        alm_data = self.alm_option_controller()
        for index in alm_data:
            if index == 'tc-path':
                if Settings.PYTALOS_ALM.get('replicate_folder_structure'):
                    alm_data[index] = alm_data[index] + '/' + str(self.feature_name)
                else:
                    alm_data[index] = alm_data['tc-path']

            if index == 'tc-descrip':
                if self.scenario.description:
                    text = self._parse_list_to_string(self.scenario.description).replace("\\n", "\n")
                else:
                    text = formatters.replace_chars(str(self.scenario.name))
                    description = text
                    for step in self.scenario.all_steps:
                        description = description + '\n' + str(step)
                    text = str(description)
                alm_data[index] = text
            if index == 'tc-name' and alm_data[index] == '':
                text = formatters.replace_chars(str(self.tc_scenario_name))
                if text in self.tc_name_list:
                    text = str(self.tc_scenario_name) + '_' + str(self.scenario.location.line)
                else:
                    text = str(self.tc_scenario_name)
                self.tc_name_list.append(text)
                alm_data[index] = text
            if index == 'ts-name' and alm_data[index] == '':
                feature_name = self._format_feature_path(self.feature_name)
                if Settings.PYTALOS_ALM.get('match_alm_execution'):
                    alm_data[index] = str(feature_name)
                else:
                    alm_data[index] = str(feature_name) + '_' + str(cd.strftime('%d-%m-%Y_%H-%M-%S'))
            elif index == 'ts-name' and alm_data[index] != '':
                if Settings.PYTALOS_ALM.get('match_alm_execution'):
                    alm_data[index] = alm_data['ts-name']
                else:
                    alm_data[index] = str(alm_data['ts-name']) + '_' + str(cd.strftime('%d-%m-%Y_%H-%M-%S'))
            if index == 'ts-descrip' and alm_data[index] == '':
                text = formatters.replace_chars(str(self.scenario.feature.description))
                alm_data[index] = text
            if index == 'ts-path' and alm_data[index] == '':
                alm_data[index] = alm_data['tc-path']
            elif index == 'ts-path' and alm_data[index] != '':
                if Settings.PYTALOS_ALM.get('replicate_folder_structure'):
                    alm_data[index] = alm_data[index] + '/' + str(self.feature_name)
                else:
                    alm_data[index] = alm_data['ts-path']

        return alm_data

    @staticmethod
    def _format_feature_path(feature_path):
        """
        Return feature path parsed.
        """
        if '/' in feature_path:
            feature_path = str(feature_path).split("/")[-1]
        if '\\' in feature_path:
            feature_path = str(feature_path).split("\\")[-1]
        return feature_path

    @staticmethod
    def _parse_list_to_string(ini_list):
        """
        Return a string pared from list.
        """
        return "\n ".join(ini_list)

    def get_final_data(self):
        """
        Return final data from csv data.
        """
        final_data_form = []
        aux_dict_alm = {}
        aux_dict_tc = {}
        aux_dict_ts = {}
        aux_dict_other = {}
        alm_data = self.csv_con_needed_data()

        for row in alm_data:
            if row.startswith("alm-"):
                aux_dict_alm[row] = alm_data[row]
            elif row.startswith("tc-"):
                aux_dict_tc[row] = alm_data[row]
            elif row.startswith("ts-"):
                aux_dict_ts[row] = alm_data[row]
            else:
                aux_dict_other[row] = alm_data[row]

        final_data_form.append(aux_dict_other)
        final_data_form.append(aux_dict_alm)
        final_data_form.append(aux_dict_tc)
        final_data_form.append(aux_dict_ts)

        return final_data_form
