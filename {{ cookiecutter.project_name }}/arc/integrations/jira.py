# -*- coding: utf-8 -*-
"""
File containing Jira integration class and plugins.
"""
import logging
import os
import requests
import urllib3  # noqa
import datetime

from colorama import Fore

from arc.contrib.tools.formatters import replace_chars
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

LOG_PATH = os.path.join(Settings.OUTPUT_PATH.get(), 'logs' + os.sep + 'pytalos.log')


class Jira:
    """
    Integration class with Jira.
    """
    scenarios_list = []

    def __init__(self):
        logger.info('Jira report is enabled')
        self.username = Settings.PYTALOS_JIRA.get('username')
        self.password = Settings.PYTALOS_JIRA.get('password')
        self.base_url = Settings.PYTALOS_JIRA.get('base_url')
        self.attach_log = True
        logger.debug(f"Jira username {self.username}")
        logger.debug(f"Jira base url: {self.base_url}")
        if Settings.PYTALOS_JIRA.get('connection_proxy').get('enabled'):
            logger.debug("Jira proxy enabled")
            self.proxy = {
                'http': Settings.PYTALOS_JIRA.get('connection_proxy').get('proxy').get('http_proxy'),
                'https': Settings.PYTALOS_JIRA.get('connection_proxy').get('proxy').get('https_proxy')
            }
        else:
            self.proxy = None

    def _set_scenario(self, feature, html_files, pdf_files, doc_files):
        """
        Set scenario information.
        :param feature:
        :param html_files:
        :param pdf_files:
        :param doc_files:
        :return:
        """
        feature_name = feature['name']
        feature_filename = feature["location"]
        logger.debug(f"Setting feature information to Jira report: {feature_name} in {feature_filename}")
        for scenario in feature['elements']:
            if scenario['type'] == 'scenario':
                tags = self._get_jira_tag(scenario['tags'])
                for tag in tags:
                    scenario_name = scenario['name']
                    steps = self._format_scenario_step(scenario['steps'])
                    if scenario.get('description'):
                        description = self._format_scenario_data(scenario.get('description'))
                    else:
                        description = '-'
                    scenario_result = str(scenario['status'])
                    dictionary = {tag: {
                        'feature_name': feature_name,
                        'feature_filename': feature_filename,
                        'scenario_name': scenario_name,
                        'steps': steps,
                        'description': description,
                        'scenario_result': scenario_result,
                        'date': str(datetime.datetime.today().strftime('%d-%m-%Y')),
                        'duration': datetime.timedelta(seconds=scenario['duration'])
                    }}
                    evidence = []
                    scenario_name_parsed = replace_chars(scenario['name'])
                    if Settings.PYTALOS_JIRA.get('report').get('upload_html_evidence'):
                        for html in html_files:
                            if scenario_name_parsed in html:
                                evidence.append(html)
                    if Settings.PYTALOS_JIRA.get('report').get('upload_pdf_evidence'):
                        for pdf in pdf_files:
                            if scenario_name_parsed in pdf:
                                evidence.append(pdf)
                    if Settings.PYTALOS_JIRA.get('report').get('upload_doc_evidence'):
                        for doc in doc_files:
                            if scenario_name_parsed in doc:
                                evidence.append(doc)
                    dictionary[tag].update({'evidence': evidence})
                    self.scenarios_list.append(dictionary)

    def post_to_jira(self, feature, html_files, pdf_files, doc_files):
        """
        Posting to Jira feature information.
        :param feature:
        :param html_files:
        :param pdf_files:
        :param doc_files:
        :return:
        """
        self._set_scenario(feature, html_files, pdf_files, doc_files)
        if Settings.PYTALOS_JIRA.get('report').get('comment_execution'):
            logger.debug("Adding execution comment")
            self._add_total_comment_in_issue()
        self._add_issue_evidence()
        self.scenarios_list = []

    @staticmethod
    def _get_jira_tag(tags):
        """
        Return Jira with format tag.
        All Jira tags in behave start with JIRA-
        :param tags:
        :return:
        """
        final_tags = []
        for tag in tags:
            if str(tag).startswith('JIRA-'):
                final_tags.append(tag)

        logger.debug(f"Jira tags found: {final_tags}")
        return final_tags

    @staticmethod
    def _format_scenario_data(data):
        """
        Format scenario data.
        :param data:
        :return:
        """
        return "\n".join(str(x) for x in data)

    @staticmethod
    def _format_scenario_step(data):
        """
        Format scenario step data.
        :param data:
        :return:
        """
        steps = "\n".join(str(x) for x in data)
        steps = steps \
            .replace('given', '--- {color:purple}*Given*{color}') \
            .replace('when', '--- {color:orange}*When*{color}') \
            .replace('then', '--- {color:violet}*Then*{color}') \
            .replace('\"', "")
        return steps

    def _add_total_comment_in_issue(self):
        """
        This function add execution summary to Jira issue depending of its Jira tag.
        :return:
        """
        scenario_dict = self._join_scenarios()
        for scenario_tag in scenario_dict:
            comment = self._parse_total_comment(scenario_dict[scenario_tag])
            api = f'{self.base_url}/rest/api/2/issue/{self._parse_tag(scenario_tag)}/comment'
            headers = {'Content-Type': 'application/json'}
            body = {'body': comment}
            logger.debug(f'Adding comment to: {self._parse_tag(scenario_tag)}')
            response = requests.post(
                api, auth=(self.username, self.password), json=body,
                headers=headers, verify=False, proxies=self.proxy
            )
            if response.status_code in [200, 201]:
                msg = "Added comment to Jira issue\n"
                logger.debug(msg)
                print(msg)
            else:
                msg = (f"There was an error adding the comment to the Jira issue.\n"
                       f"Response status code: {response.status_code}\n"
                       f"Response result: {response.text}\n")
                logger.error(msg)
                print(Fore.RED + msg)

    def _add_issue_evidence(self):
        """
        Add evidences reports to issue depending its Jira tag.
        :return:
        """
        api = None
        headers = None
        for scenario in self.scenarios_list:
            for key in scenario.keys():
                api = f'{self.base_url}/rest/api/2/issue/{self._parse_tag(key)}/attachments'
                headers = {"X-Atlassian-Token": "nocheck"}
                for attach in scenario[key]['evidence']:
                    self._delete_attachment(attach.split(os.sep)[-1])
                    files = [('file', open(attach, 'rb'))]
                    logger.debug(f"Adding evidence report to: {self._parse_tag(key)}")
                    response = requests.post(api, auth=(self.username, self.password), files=files,
                                  headers=headers, verify=False, proxies=self.proxy)

                    if response.status_code in [200, 201]:
                        msg = "Evidence reports added to Jira Issue\n"
                        logger.debug(msg)
                        print(msg)
                    else:
                        msg = (f"There was an error during the upload of the evidences reports to the Jira issue.\n"
                               f"Response status code: {response.status_code}\n"
                               f"Response result: {response.text}\n")
                        logger.error(msg)
                        print(Fore.RED + msg)
        if api and Settings.PYTALOS_JIRA.get('report').get('upload_log_evidence') and self.attach_log is True:
            files = [('file', open(LOG_PATH, 'rb'))]
            response = requests.post(api, auth=(self.username, self.password), files=files,
                          headers=headers, verify=False, proxies=self.proxy)
            if response.status_code in [200, 201]:
                msg = "Log evidences uploaded\n"
                logger.debug(msg)
                print(msg)
            else:
                msg = (f"There was an error during the upload of the evidences logs to the Jira issue\n"
                       f"Response status code: {response.status_code}\n"
                       f"Response result: {response.text}\n")
                logger.error(msg)
                print(Fore.RED + msg)
            self.attach_log = False

    @staticmethod
    def _format_feature_filename_to_html(feature_filename):
        """
        Format feature file name extension to html extension.
        :param feature_filename:
        :return:
        """
        feature_filename = str(feature_filename).replace(".feature", ".html")
        feature_filename = str(feature_filename).replace("/", ".")
        final_filename = f'TESTS-{feature_filename}'
        return final_filename

    def _get_attachment_data(self):
        """
        Get attachment data from Jira tag.
        :return:
        """
        headers = {"X-Atlassian-Token": "nocheck"}
        scenario_dict = self._join_scenarios()
        current_attachments = []
        for scenario_tag in scenario_dict:
            tag = self._parse_tag(scenario_tag)
            api = f'{self.base_url}/rest/api/2/issue/{self._parse_tag(tag)}'
            response = requests.get(api, auth=(self.username, self.password), headers=headers,
                                    verify=False, proxies=self.proxy)
            issues_attachments = self._get_issue_id_name_attachment(response)
            current_attachments.append(issues_attachments)

        return current_attachments

    @staticmethod
    def _get_issue_id_name_attachment(response):
        """
        Get issue id name from attachment.
        :param response:
        :return:
        """
        response_json = response.json()
        attachments = response_json.get('fields', {}).get('attachment', {})
        current_attachment = []
        for attach in attachments:
            current_attachment.append({
                'id': attach['id'],
                'name': attach['filename']
            })
        return current_attachment

    def _delete_attachment(self, attachment_to_delete):
        """
        Delete current attachments in issue
        :param attachment_to_delete:
        :return:
        """
        current_attachments = self._get_attachment_data()
        attach_id = ""
        for attachments in current_attachments:
            for attachment in attachments:
                if attachment['name'] == attachment_to_delete:
                    attach_id = attachment['id']

        if attach_id != "":
            headers = {"X-Atlassian-Token": "nocheck"}
            api = f'{self.base_url}/rest/api/2/attachment/{attach_id}'
            logger.debug(f'Remove Jira attachment in issue with id: {attach_id}')
            requests.delete(api, auth=(self.username, self.password), headers=headers,
                            verify=False, proxies=self.proxy)

    @staticmethod
    def _parse_tag(tag):
        """
        Return tag parsed.
        :param tag:
        :return:
        """
        return str(tag).replace('JIRA-', '')

    def _parse_total_comment(self, scenarios_list):
        """
        Return parsed total summary of the execution comment.
        :param scenarios_list:
        :return:
        """
        execution_title = "Automated Test Execution Summary."
        execution_result = self._get_scenario_result(scenarios_list)
        execution_date = str(datetime.datetime.today().strftime('%d-%m-%Y'))
        tc_title = "Test Case Executed:"
        tcs_info = self._get_total_scenario_name(scenarios_list)
        execution_info_title = "Execution Information:"
        total_scenario = len(scenarios_list)
        scenario_passed = self._count_scenario_result(scenarios_list)['passed']
        scenario_failed = self._count_scenario_result(scenarios_list)['failed']
        scenario_skipped = self._count_scenario_result(scenarios_list)['skipped']
        scenario_success_rate = f"{(scenario_passed * 100) / total_scenario}"
        execution_duration = self._get_total_duration(scenarios_list)
        coe_text = '--- CoE Testing Automation --- Automation Toolkit'
        ln = '\n'
        strong = '*'
        sep = '-' * 80

        return f'h1. {execution_title}{ln}{ln}{ln}{ln}' \
               f'* {strong}Execution Result:{strong} {execution_result}{ln}' \
               f'* {strong}Execution Date:{strong} {execution_date}{ln}{ln}{ln}' \
               f'h3. {strong}{tc_title}{strong}{ln}' \
               f'{strong}{sep}{strong}{ln}' \
               f'{tcs_info}{ln}' \
               f'{ln}{strong}{sep}{strong}{ln}{ln}{ln}' \
               f'h3.{strong}{execution_info_title}{strong}{ln}' \
               f'{strong}{sep}{strong}{ln}' \
               f'* {strong}Total Executed Scenario:{strong} {total_scenario}{ln}' \
               f'* {strong}Passed Scenario:{strong} {scenario_passed}{ln}' \
               f'* {strong}Failed Scenario:{strong} {scenario_failed}{ln}' \
               f'* {strong}Skipped Scenario:{strong} {scenario_skipped}{ln}' \
               f'* {strong}Scenario Success Rate:{strong} {scenario_success_rate}%{ln}' \
               f'* {strong}Execution Duration:{strong} {execution_duration}{ln}' \
               f'{ln}{strong}{sep}{strong}{ln}{ln}{ln}{ln}' \
               f'h6. Report created programmatically by: {strong}TalosBDD Automation Framework{strong} {coe_text}'

    @staticmethod
    def _get_total_duration(scenario_list):
        """
        Return total duration from scenario list.
        :param scenario_list:
        :return:
        """
        total_duration = datetime.timedelta(seconds=0)
        for scenario_data in scenario_list:
            total_duration += scenario_data['duration']

        return total_duration

    def _get_total_scenario_name(self, scenario_list):
        """
        Get total scenario name from scenario list.
        :param scenario_list:
        :return:
        """
        scenario_name = []
        slash = os.sep
        nl = '\n'
        count_scenario = 0
        for scenario_data in scenario_list:
            evidence = ""
            count_scenario += 1
            for current_evidence in scenario_data['evidence']:
                evidence += f'[{current_evidence.split(slash)[-1]}|^{current_evidence.split(slash)[-1]}] '
            emoticon = self._get_result_emoticon(self._format_result(scenario_data["scenario_result"]))
            scenario_info = f'{count_scenario}. {emoticon} --- {scenario_data["feature_name"]} ' \
                            f'--- {scenario_data["scenario_name"]} ' \
                            f'--- {scenario_data["duration"]} ' \
                            f'--- {self._format_result(scenario_data["scenario_result"])}{nl}' \
                            f'{evidence} '

            scenario_name.append(scenario_info)

        return "\n".join(str(x) for x in scenario_name)

    @staticmethod
    def _get_result_emoticon(result):
        """
        Return result emoticon from result in string.
        :param result:
        :return:
        """
        if 'PASSED' in result:
            return '(/)'
        elif 'FAILED' in result:
            return '(x)'
        else:
            return '(!)'

    @staticmethod
    def _format_result(result):
        """
        Return parse result with color.
        :param result:
        :return:
        """
        color_close = '*{color}'
        result = str(result).upper()
        if result == 'PASSED':
            return '{color:green}*' + result + color_close
        elif result == 'FAILED':
            return '{color:red}*' + result + color_close
        else:
            return '{color:blue}*' + result + color_close

    @staticmethod
    def _get_scenario_result(scenario_list):
        """
        Return scenario result with color and parsed.
        :param scenario_list:
        :return:
        """
        result_list = []
        for scenario_data in scenario_list:
            result = str(scenario_data['scenario_result']).upper()
            result_list.append(result)

        if 'FAILED' in result_list and 'SKIPPED' not in result_list:
            return '{color:red}*FAILED*{color} :('
        elif 'FAILED' not in result_list and 'SKIPPED' not in result_list:
            return '{color:green}*PASSED*{color} :D'
        else:
            return '{color:blue}*SKIPPED*{color} :P'

    def _count_scenario_result(self, scenario_list):
        """
        Return total passed, failed and skip scenario count.
        :param scenario_list:
        :return:
        """
        passed = 0
        failed = 0
        skipped = 0
        for scenario_data in scenario_list:
            result = self._format_result(scenario_data["scenario_result"])
            if 'PASSED' in result:
                passed += 1
            elif 'FAILED' in result:
                failed += 1
            else:
                skipped += 1

        return {
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'total': passed + failed + skipped
        }

    def _join_scenarios(self):
        """
        Join all scenarios in a dict
        :return:
        """
        final_dict = {}
        for scenario_dict in self.scenarios_list:
            for tag in scenario_dict.keys():
                if tag not in final_dict.keys():
                    final_dict.update({tag: []})
                final_dict[tag].append(scenario_dict[tag])
        return final_dict
