# -*- coding: utf-8 -*-
"""
Customised Behave compatible formatters module for customised Talos for the purpose of output.
"""
import base64
import datetime
import json
import os
import platform
import random
import traceback
import logging
import re
from copy import deepcopy

import six

from arc import __VERSION__
from behave.textutil import select_best_encoding, ensure_stream_with_encoder as _ensure_stream_with_encoder
from colorama import Fore

from arc.contrib.tools.formatters import replace_chars
from arc.reports.html.utils import get_short_name, get_doc_pdf_scenario_name, attach_html_files, attach_docx_files, \
    attach_pdf_files
from arc.settings.settings_manager import Settings
from arc.web.app.utils import print_portal_console

from arc.core.behave.template_var import replace_template_var, get_value_from_profiles, get_value_from_repositories
from urllib3.packages import six  # noqa
from behave.formatter.ansi_escapes import escapes, up
from behave.formatter.base import Formatter
from behave.model_core import Status
from behave.model_describe import escape_cell, escape_triple_quotes
from behave.textutil import indent, text as _text
from six.moves import range, zip

logger = logging.getLogger(__name__)


def get_json_report_args_for_parallel():
    """
    Return arguments needed in order to create the json report for parallel execution.
    """
    ext = random.randrange(1000000000, 9999999999)
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    args = f" -f arc.reports.custom_formatters:CustomJSONFormatter " \
           f"-o output/reports/talos_report_{now}_{ext}.json -f arc.reports.custom_formatters:CustomParallelFormatter"
    logger.debug(f"Arguments of execution for json report generation: {args}")
    return args


def get_json_report_args_for_portal():
    """
    Return arguments needed in order to create the json report for parallel execution.
    """
    args = f" -f arc.reports.custom_formatters:CustomPortalFormatter -o output/reports/talos_report.json "
    logger.debug(f"Arguments of execution for json report generation: {args}")
    return args


def get_json_report_args():
    """
    Return arguments needed in order to create the json report for sequential execution.
    """
    args = " -f arc.reports.custom_formatters:CustomJSONFormatter -o output/reports/talos_report.json --format pretty"
    logger.debug(f"Arguments of execution for json report generation: {args}")
    return args


def _get_obtained_result(step):
    """
    Return obtained result parsed.
    """
    if str(step.status) == 'Status.passed':
        if step.obtained_result_passed:
            obtained_result = str(step.obtained_result_passed)
        else:
            obtained_result = "Operation with correct result"
    elif str(step.status) == "Status.failed":
        if step.obtained_result_failed:
            obtained_result = str(step.obtained_result_failed)
        else:
            obtained_result = "Operation with incorrect result"
    else:
        if step.obtained_result_skipped:
            obtained_result = str(step.obtained_result_skipped)
        else:
            obtained_result = "Operation skipped"
    return obtained_result


def _get_expected_result(step):
    """
    Return expected result parsed.
    """
    if step.result_expected:
        expected_result = str(step.result_expected)
    else:
        expected_result = str(replace_template_var(step.name))
    return expected_result


class StreamOpener(object):
    """
    Provides a transport vehicle to open the formatter output stream
    when the formatter needs it.
    In addition, it provides the formatter with more control:

      * when a stream is opened
      * if a stream is opened at all
      * the name (filename/dirname) of the output stream
      * let it decide if directory mode is used instead of file mode
    """
    # FORMER: default_encoding = "UTF-8"
    default_encoding = select_best_encoding()

    def __init__(self, filename=None, stream=None, encoding=None):
        if not encoding:
            encoding = self.default_encoding
        if stream:
            stream = self.ensure_stream_with_encoder(stream, encoding)
        self.name = filename
        self.stream = stream
        self.encoding = encoding
        self.should_close_stream = not stream  # Only for not pre-opened ones.

    @staticmethod
    def ensure_dir_exists(directory):
        """
        Create directory if this does not exists.
        """
        if directory and not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except (Exception,) as ex:
                logger.warning(ex)

    @classmethod
    def ensure_stream_with_encoder(cls, stream, encoding=None):
        """
        Ensure stream execution with encoder.
        """
        return _ensure_stream_with_encoder(stream, encoding)

    def open(self):
        """
        Open and return stream.
        """
        if not self.stream or self.stream.closed:
            self.ensure_dir_exists(os.path.dirname(self.name))
            stream = open(self.name, "w", encoding=self.encoding)
            stream = self.ensure_stream_with_encoder(stream, self.encoding)
            self.stream = stream  # -- Keep stream for house-keeping.
            self.should_close_stream = True
            assert self.should_close_stream
        return self.stream

    def close(self):
        """
        Close the stream, if it was opened by this stream_opener.
        Skip closing for sys.stdout and pre-opened streams.
        :return: True, if stream was closed.
        """
        closed = False
        if self.stream and self.should_close_stream:
            closed = getattr(self.stream, "closed", False)
            if not closed:
                self.stream.close()
                closed = True
            self.stream = None
        return closed


class CustomJSONFormatter(Formatter):
    """
    This is a custom json formatter to generate the talos_report.json
    """
    name = "json"
    description = "JSON dump of test run"
    dumps_kwargs = {"ensure_ascii": False, "indent": 4}
    split_text_into_lines = True  # EXPERIMENT for better readability.

    json_number_types = six.integer_types + (float,)
    json_scalar_types = json_number_types + (six.text_type, bool, type(None))

    def __init__(self, stream_opener, config):
        super().__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.feature_count = 0
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0
        self.features_storage = []

    def open(self):
        """
        Ensure that the output stream is open.
        Triggers the stream opener protocol (if necessary).

        :return: Output stream to use (just opened or already open).
        """
        if not self.stream:
            self.stream = self.stream_opener.open()
        return self.stream

    def reset(self):
        """
        Rest needed properties.
        """
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0

    # -- FORMATTER API:
    def uri(self, uri):
        """
        Called before processing a file (normally a feature file).
        :param uri:  URI or filename (as string).
        """
        pass

    def feature(self, feature):
        """
        This method generate feature data BEFORE executing it.
        So there is no way to add new data using this method.
        :param feature:
        :type feature:
        :return:
        :rtype:
        """
        self.reset()
        self.current_feature = feature
        self.current_feature_data = {
            "keyword": feature.keyword,
            "name": replace_template_var(feature.name),
            "tags": list(feature.tags),
            "location": six.text_type(feature.location),
            "status": None,  # Not known before feature run.
        }
        element = self.current_feature_data
        if feature.description:
            for i in range(len(feature.description)):
                feature.description[i] = replace_template_var(feature.description[i])
            element["description"] = feature.description
        element['attachments'] = []
        if attach_html_files():
            feature_html_path = f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/feature_{get_short_name(element['name'])}.html"
            element['attachments'].append(feature_html_path)

    def background(self, background):
        """
        This method generate background data BEFORE executing it.
        So there is no way to add new data using this method.
        :param background:
        :type background:
        :return:
        :rtype:
        """
        if os.environ['RUN_TYPE'] == 'sequential':
            element = self.add_feature_element({
                "type": "background",
                "keyword": background.keyword,
                "name": background.name,
                "location": six.text_type(background.location),
                "steps": [],
            })
            if background.name:
                element["name"] = background.name
            self._step_index = 0

            # -- ADD BACKGROUND STEPS: Support *.feature file regeneration.
            for step_ in background.steps:
                self.step(step_)

    def scenario(self, scenario):
        """
        This method generate scenario data BEFORE executing it.
        So there is no way to add new data using this method.
        :param scenario:
        :type scenario:
        :return:
        :rtype:
        """
        self.finish_current_scenario()
        self.current_scenario = scenario
        if '@' in scenario.name:
            scenario.name = str(scenario.name).replace('@', '')
        element = self.add_feature_element({
            "type": "scenario",
            "keyword": scenario.keyword,
            "name": replace_template_var(scenario.name),
            "raw_name": self.get_raw_name(scenario),
            "match": self.add_dict_match(scenario),
            "tags": scenario.tags,
            "location": six.text_type(scenario.location),
            "steps": [],
            "status": None,
        })
        if scenario.description:
            for i in range(len(scenario.description)):
                scenario.description[i] = replace_template_var(scenario.description[i])
            element["description"] = scenario.description

        element['attachments'] = []
        if attach_html_files():
            if Settings.PYTALOS_OCTANE.get('post_to_octane'):
                element['attachments'].append(
                    f"{Settings.BASE_PATH.get(force=True)}/output/scenario_{get_short_name(element['name'])}.zip")
            else:
                element['attachments'].append(
                    f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/scenario_{get_short_name(element['name'])}.html")
        if attach_docx_files():
            docx_path = get_doc_pdf_scenario_name(element['name'], self.current_feature.driver, file_type='docx')
            element['attachments'].append(docx_path)
        if attach_pdf_files():
            pdf_path = get_doc_pdf_scenario_name(element['name'], self.current_feature.driver, file_type='pdf')
            element['attachments'].append(pdf_path)
        setattr(scenario, 'start_time', datetime.datetime.now().timestamp())

        self._step_index = 0

    @staticmethod
    def get_raw_name(scenario):
        scenario_name = scenario.name
        feature = scenario.feature
        for current_scenario in feature.scenarios:
            raw_name = current_scenario.name
            if hasattr(current_scenario, 'scenarios'):
                for scenarios_parser in current_scenario.scenarios:
                    if scenario_name == scenarios_parser.name:
                        return raw_name
            else:
                if scenario_name == raw_name:
                    return raw_name

    def add_dict_match(self, scenario):
        profile_dict = self.get_dict_template_var_profiles(scenario.name)
        repository_dict = self.get_dict_template_var_repositories(scenario.name)
        example_table_dict = self.get_example_table(scenario)
        match_dict = {"template_var_profile": profile_dict,
                      "template_var_repository": repository_dict,
                      "example_table": example_table_dict}
        return match_dict

    @staticmethod
    def get_dict_template_var_profiles(scenario_name):
        """
        Get the template var from profiles
        """
        dict_template_var_profile = []
        regex = r"\${{(.*?)\}\}"
        matchers = re.findall(regex, scenario_name)
        template_var_dict = {}
        for match in matchers:
            copy_dict = deepcopy(template_var_dict)
            value = get_value_from_profiles(match)
            copy_dict['name'] = match
            copy_dict['value'] = value
            dict_template_var_profile.append(copy_dict)
        return dict_template_var_profile

    @staticmethod
    def get_dict_template_var_repositories(scenario_name):
        """
        Get the template var from repositories
        """
        dict_template_var_repository = []
        regex = r"\&{{(.*?)\}\}"
        matchers = re.findall(regex, scenario_name)
        template_var_dict = {}
        for match in matchers:
            copy_dict = deepcopy(template_var_dict)
            value = get_value_from_repositories(match)
            copy_dict['name'] = match
            copy_dict['value'] = value
            dict_template_var_repository.append(copy_dict)
        return dict_template_var_repository

    @staticmethod
    def get_example_table(scenario):
        """
        Get example tables
        """
        list_example_table = []
        dict_example_table = {}
        feature = scenario.feature

        for current_scenario in feature.scenarios:
            if hasattr(current_scenario, 'examples'):
                for example in current_scenario.examples:
                    for row in example.table.rows:
                        for i in range(0, len(row)):
                            aux_dict = deepcopy(dict_example_table)
                            aux_dict['name'] = example.table.headings[i]
                            aux_dict['value'] = row.cells[i]
                            list_example_table.append(aux_dict)
        return list_example_table

    @classmethod
    def make_table(cls, table):
        """
        Create table from headers and rows.
        :param table:
        :return:
        """
        headings = []
        rows = []
        for header in table.headings:
            headings.append(replace_template_var(header))
        for row in table.rows:
            aux = []
            for cell in row.cells:
                aux.append(replace_template_var(cell))
            rows.append(aux)

        table_data = {
            "headings": headings,
            "rows": rows
        }
        return table_data

    def step(self, step):
        """
        Set step data.
        :param step:
        :return:
        """
        s = {
            "keyword": step.keyword,
            "step_type": step.step_type,
            "name": step.name,
            "location": six.text_type(step.location),
        }

        if step.text:
            text = step.text
            if self.split_text_into_lines and "\n" in text:
                text = text.splitlines()
            s["text"] = text
        if step.table:
            s["table"] = self.make_table(step.table)
        element = self.current_feature_element
        element["steps"].append(s)

    def match(self, match):
        """
        Match steps arguments.
        :param match:
        :return:
        """
        args = []
        for argument in match.arguments:
            argument_value = argument.value
            if not isinstance(argument_value, self.json_scalar_types):
                # -- OOPS: Avoid invalid JSON format w/ custom types.
                # Use raw string (original) instead.
                argument_value = argument.original
            assert isinstance(argument_value, self.json_scalar_types)
            arg = {
                "value": argument_value,
            }
            if argument.name:
                arg["name"] = argument.name
            args.append(arg)

        match_data = {  # noqa
            "location": six.text_type(match.location) or "",
            "arguments": args,
        }

        if match.location:
            # -- NOTE: match.location=None occurs for undefined steps.
            steps = self.current_feature_element["steps"]
            steps[self._step_index]["match"] = match_data

    def result(self, step):
        """
        When a step end, the result data is generated here.
        :param step:
        :type step:
        :return:
        :rtype:
        """
        if str(step.status) != 'Status.undefined':
            steps = self.current_feature_element["steps"]
            steps[self._step_index]["result"] = {
                "status": step.status.name,
                "duration": step.duration,
                "expected_result": _get_expected_result(step),
                "obtained_result": _get_obtained_result(step)
            }
            steps[self._step_index]['name'] = replace_template_var(step.name)
            if steps[self._step_index].get('text'):
                if isinstance(steps[self._step_index]['text'], list):
                    for i in range(len(steps[self._step_index]['text'])):
                        steps[self._step_index]['text'][i] = replace_template_var(steps[self._step_index]['text'][i])
                else:
                    steps[self._step_index]['text'] = replace_template_var(steps[self._step_index]['text'])
            # Extra data.
            steps[self._step_index]['start_time'] = step.start_time
            steps[self._step_index]['end_time'] = step.end_time
            steps[self._step_index]["screenshots"] = step.screenshots
            steps[self._step_index]["additional_text"] = step.additional_text
            steps[self._step_index]["additional_html"] = step.additional_html
            steps[self._step_index]["request"] = step.request
            steps[self._step_index]["response_content"] = step.response_content
            steps[self._step_index]["response_headers"] = step.response_headers
            steps[self._step_index]["jsons"] = step.jsons
            steps[self._step_index]["api_info"] = step.api_info
            steps[self._step_index]["unit_tables"] = step.unit_tables
            steps[self._step_index]["sub_steps"] = self.get_sub_steps(step)

            if step.error_message and step.status == Status.failed:
                # -- OPTIONAL: Provided for failed steps.
                # error_message = step.error_message
                # if self.split_text_into_lines and "\n" in error_message:
                #     error_message = error_message.splitlines()
                result_element = steps[self._step_index]["result"]
                result_element["error_message"] = step.exception.__str__()
            self._step_index += 1

    def get_sub_steps(self, step):
        _sub_steps = []
        if hasattr(step, 'sub_steps') and len(step.sub_steps) > 0:
            for sub_step in step.sub_steps:
                if sub_step.status == 'untested':
                    _sub_steps.append({
                        'keyword': sub_step.keyword,
                        'step_type': sub_step.step_type,
                        'name': replace_template_var(sub_step.name),
                        'sub_steps': self.get_sub_steps(sub_step)
                    })
                else:
                    _sub_steps.append({
                        'keyword': sub_step.keyword,
                        'step_type': sub_step.step_type,
                        'name': replace_template_var(sub_step.name),
                        'result': {
                            "status": sub_step.status.name,
                            "duration": sub_step.duration,
                            "expected_result": _get_expected_result(sub_step),
                            "obtained_result": _get_obtained_result(sub_step)
                        },
                        'start_time': sub_step.start_time,
                        'end_time': sub_step.end_time,
                        'screenshots': sub_step.screenshots,
                        'additional_text': sub_step.additional_text,
                        'additional_html': sub_step.additional_html,
                        'request': sub_step.request,
                        'response_content': sub_step.response_content,
                        'response_headers': sub_step.response_headers,
                        'jsons': sub_step.jsons,
                        'api_info': sub_step.api_info,
                        'unit_tables': sub_step.unit_tables,
                        'sub_steps': self.get_sub_steps(sub_step)
                    })
        else:
            return []
        return _sub_steps

    def embedding(self, mime_type, data):
        """
        Create a embeddings element into step dict.
        :param mime_type:
        :param data:
        :return:
        """
        step = self.current_feature_element["steps"][-1]
        step["embeddings"].append({
            "mime_type": mime_type,
            "data": base64.b64encode(data).replace("\n", ""),  # noqa
        })

    def eof(self):
        """
        This method writes the feature data when the feature execution ended.
        End of feature
        """
        if not self.current_feature_data:
            return

        if 'no_evidences' in self.current_feature.tags:
            return

        self.get_template_var()
        self.add_scenario_data()
        self.add_feature_data()
        # -- NORMAL CASE: Write collected data of current feature.
        self.finish_current_scenario()
        self.update_status_data()

        if self.feature_count == 0:
            # -- FIRST FEATURE:
            self.write_json_header()
        else:
            # -- NEXT FEATURE:
            self.write_json_feature_separator()

        self.write_json_feature(self.current_feature_data)
        self.reset()
        self.feature_count += 1

    def close(self):
        """
        Close the stream.
        :return:
        :rtype:
        """
        if self.feature_count == 0:
            # -- FIRST FEATURE: Corner case when no features are provided.
            self.write_json_header()
        self.write_json_footer()
        self.close_stream()

    # -- JSON-DATA COLLECTION:
    def add_feature_element(self, element):
        """
        Add element to feature.
        :param element:
        :return:
        """
        assert self.current_feature_data is not None
        if "elements" not in self.current_feature_data:
            self.current_feature_data["elements"] = []
        self.current_feature_data["elements"].append(element)
        return element

    @property
    def current_feature_element(self):
        """
        Return current feature elements data.
        :return:
        """
        assert self.current_feature_data is not None
        return self.current_feature_data["elements"][-1]

    def update_status_data(self):
        """
        Update status of feature.
        :return:
        """
        assert self.current_feature
        assert self.current_feature_data
        self.current_feature_data["status"] = self.current_feature.status.name

    def finish_current_scenario(self):
        """
        finish curren scenario data.
        :return:
        """
        if self.current_scenario:
            status_name = self.current_scenario.status.name
            self.current_feature_element["status"] = status_name

    # -- JSON-WRITER:
    def write_json_header(self):
        """
        Write into json the header needed.
        :return:
        """
        self.stream.write("{\n \"features\":[")

    def write_json_footer(self):
        """
        This method end the features list and add the global data.
        :return:
        :rtype:
        """
        self.stream.write("],")
        self.stream.write(self.add_global_data())
        self.stream.write(",")
        self.stream.write(self.add_octane())
        self.stream.write("\n}\n")

    def write_json_feature(self, feature_data):
        """
        This method write the feature data to the json file
        :param feature_data:
        :type feature_data:
        :return:
        :rtype:
        """
        self.stream.write(json.dumps(feature_data, **self.dumps_kwargs))
        self.stream.flush()

    def write_json_feature_separator(self):
        """
        Write separator by feature into json.
        :return:
        """
        self.stream.write(",\n\n")

    def get_template_var(self):
        """
        This method replace the template var in scenarios skipped.
        :return:
        :rtype:
        """
        for elem in self.current_feature_data.get('elements', []):
            if elem['type'] == 'scenario':
                for step in elem['steps']:
                    if not step.get('result'):
                        step['name'] = replace_template_var(step['name'])

    def add_scenario_data(self):
        """
        This method add scenario data from the current_feature to the current_feature_data.
        :return:
        :rtype:
        """
        info_scenarios = {}
        count = 0
        for elem in self.current_feature_data['elements']:
            if elem["location"] not in info_scenarios.keys():
                info_scenarios[elem["location"]] = []
                count = 0
            count += 1
            info_scenarios[elem["location"]] = count

        for key in info_scenarios:
            count_scenarios = 1
            for idx, _element in enumerate(self.current_feature_data['elements']):
                while key in _element['location'] and count_scenarios < info_scenarios[key]:
                    del self.current_feature_data['elements'][idx]
                    count_scenarios += 1

        scenarios_feature_data = [element for element in self.current_feature_data['elements']
                                  if element.get("status") != "skipped" and
                                  element.get("type") in ['scenario', 'scenario_outline']]

        scenarios_list = []
        index_outline_scenarios = []
        count_total_scenario = 0
        for scenario in self.current_feature.scenarios:
            if scenario.type == "scenario":
                if scenario.status.name != "skipped":
                    scenarios_feature_data[count_total_scenario] = update_feature_scenario_data(
                        scenarios_feature_data[count_total_scenario], scenario)
                    count_total_scenario += 1
            elif scenario.type == "scenario_outline":
                if scenario.status.name != "skipped":
                    new_scenarios = [_scenario for _scenario in scenario.scenarios if
                                     _scenario.status.name != "skipped"]
                    scenarios_list += new_scenarios
                    for i in range(0, len(new_scenarios)):
                        index_outline_scenarios.append(count_total_scenario + i)
                    count_total_scenario += len(new_scenarios)

        if len(scenarios_list) > 0:
            count_total_scenario = 0
            for scenario in scenarios_list:
                if scenario.status != "skipped":
                    scenarios_feature_data[
                        index_outline_scenarios[count_total_scenario]] = update_feature_scenario_data(
                        scenarios_feature_data[index_outline_scenarios[count_total_scenario]], scenario)
                    count_total_scenario = count_total_scenario + 1

    def add_feature_data(self):
        """
        This method add feature data from the current_feature to the current_feature_data
        :return:
        :rtype:
        """
        self.current_feature_data['total_scenarios'] = self.current_feature.total_scenarios
        self.current_feature_data['passed_scenarios'] = self.current_feature.passed_scenarios
        self.current_feature_data['failed_scenarios'] = self.current_feature.failed_scenarios
        self.current_feature_data['scenarios_passed_percent'] = self.current_feature.scenarios_passed_percent
        self.current_feature_data['scenarios_failed_percent'] = self.current_feature.scenarios_failed_percent
        self.current_feature_data['total_steps'] = self.current_feature.total_steps
        self.current_feature_data['steps_passed'] = self.current_feature.steps_passed
        self.current_feature_data['steps_failed'] = self.current_feature.steps_failed
        self.current_feature_data['steps_skipped'] = self.current_feature.steps_skipped
        self.current_feature_data['steps_passed_percent'] = self.current_feature.steps_passed_percent
        self.current_feature_data['steps_failed_percent'] = self.current_feature.steps_failed_percent
        self.current_feature_data['steps_skipped_percent'] = self.current_feature.steps_skipped_percent
        self.current_feature_data['start_time'] = self.current_feature.start_time
        self.current_feature_data['end_time'] = self.current_feature.end_time
        self.current_feature_data['duration'] = self.current_feature.duration
        self.current_feature_data['operating_system'] = f"{platform.system()} {platform.release()}"
        self.current_feature_data['driver'] = self.current_feature.driver
        self.current_feature_data['config_environment'] = self.current_feature.config_environment

        self.features_storage.append(self.current_feature_data)

    def calculate_global_results(self):
        """
        This method calculate the following values for the global data section:
        - Start time of the execution
        - End time of the execution
        - Features passed
        - Features failed
        - Total scenarios
        - Scenarios passed
        :return:
        :rtype:
        """
        global_result = {
            "total_features": len(self.features_storage),
            "features_passed": 0,
            "features_failed": 0,
            "total_scenarios": 0,
            "passed_scenarios": 0,
            "failed_scenarios": 0,
            "total_steps": 0,
            "steps_passed": 0,
            "steps_failed": 0,
            "steps_skipped": 0,
            "features_passed_percent": 0,
            "features_failed_percent": 0,
            "scenarios_passed_percent": 0,
            "scenarios_failed_percent": 0,
            "start_time": 0,
            "end_time": 0
        }
        for idx, feature in enumerate(self.features_storage):
            if len(self.features_storage) == 1:
                global_result['start_time'] = feature.get('start_time')
                global_result['end_time'] = feature.get('end_time')
            elif idx == 0:
                global_result['start_time'] = feature.get('start_time')
            elif idx == len(self.features_storage) - 1:
                global_result['end_time'] = feature.get('end_time')

            if feature.get('status') == "passed":
                global_result['features_passed'] += 1
            else:
                global_result['features_failed'] += 1

            global_result['total_scenarios'] += feature.get('total_scenarios')
            global_result['passed_scenarios'] += feature.get('passed_scenarios')
            global_result['failed_scenarios'] += feature.get('failed_scenarios')

            global_result['total_steps'] += feature.get('total_steps')

            global_result['steps_passed'] += feature.get('steps_passed')
            global_result['steps_failed'] += feature.get('steps_failed')
            global_result['steps_skipped'] += feature.get('steps_skipped')

        global_result[  # noqa
            'scenarios_passed_percent'
        ] = "0" if global_result['passed_scenarios'] == 0 else format_decimal(
            (global_result['passed_scenarios'] * 100) / global_result['total_scenarios'])

        global_result['scenarios_failed_percent'] = "0" if global_result['failed_scenarios'] == 0 else format_decimal(
            (global_result['failed_scenarios'] * 100) / global_result['total_scenarios'])

        global_result['features_passed_percent'] = "0" if global_result['features_passed'] == 0 else format_decimal(
            (global_result['features_passed'] * 100) / global_result['total_features']
        )
        global_result['features_failed_percent'] = "0" if global_result['features_failed'] == 0 else format_decimal(
            (global_result['features_failed'] * 100) / global_result['total_features']
        )

        return global_result

    def add_global_data(self):
        """
        This method add global data for other purposes.
        :return:
        :rtype:
        """
        global_results = self.calculate_global_results()
        data = '"global_data":' + json.dumps({
            'keyword': 'global_data',
            'date': datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
            'application': Settings.PROJECT_INFO.get('application'),
            'business_area': Settings.PROJECT_INFO.get('business_area'),
            'entity': Settings.PROJECT_INFO.get('entity'),
            'user_code': Settings.PROJECT_INFO.get('user_code'),
            'environment': Settings.PYTALOS_PROFILES.get('environment'),
            'version': __VERSION__,
            'results': global_results
        }, **self.dumps_kwargs)

        return data

    def add_octane(self):
        """
        This method add octane data.
        :return:
        :rtype:
        """

        return '"octane":' + json.dumps({
            'server': Settings.PYTALOS_OCTANE.get('server'),
            'username': Settings.PROJECT_INFO.get('user_code'),
            'clientid': Settings.PYTALOS_OCTANE.get('client_id'),
            'secret': Settings.PYTALOS_OCTANE.get('secret'),
            'sharedspace': Settings.PYTALOS_OCTANE.get('shared_space'),
            'workspace': Settings.PYTALOS_OCTANE.get('workspace')
        }, **self.dumps_kwargs)


class CustomParallelFormatter(Formatter):
    """
    This is a custom formatter in order to print console output for parallel execution.
    """
    name = "parallel"
    description = "Formatter for parallel executions"
    driver = ''

    def __init__(self, stream_opener, config):
        super().__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        try:
            self.stream = self.open()
        except FileExistsError:
            traceback.print_exc()

        self.feature_name = ''
        self.scenario_name = ''
        self.background_name = ''
        self.step_name = ''

    def feature(self, feature):
        """
        Called before a feature is executed.
        :param feature:  Feature object (as :class:`behave.model.Feature`)
        """
        self.feature_name = feature.name
        self.driver = feature.driver.upper()

        line = f"--\t{self.driver}\t-\t{'FEATURE'}\t-\t{self.feature_name}\t-\tSTARTED\n"
        self.stream.write(Fore.MAGENTA + line)

    def background(self, background):
        """
        Called when a (Feature) Background is provided.
        Called after :method:`feature()` is called.
        Called before processing any scenarios or scenario outlines.
        :param background:  Background object (as :class:`behave.model.Background`)
        """
        self.background_name = background.name

    def scenario(self, scenario):
        """
        Called before a scenario is executed (or ScenarioOutline scenarios).
        :param scenario:  Scenario object (as :class:`behave.model.Scenario`)
        """
        self.scenario_name = scenario.name
        line = f"--\t{self.driver}\t-\t{'SCENARIO'}\t-\t{self.feature_name}\t-\t{self.scenario_name}\t-\tSTARTED\n"
        self.stream.write(Fore.YELLOW + line)

    def step(self, step):
        """
        Called before a step is executed (and matched).
        NOTE: Normally called before scenario is executed for all its steps.
        :param step: Step object (as :class:`behave.model.Step`)
        """
        self.step_name = step.name
        status = 'RUNNING'

        line = f"--\t{self.driver}\t-\t{'STEP'}\t-\t{self.feature_name}" \
               f"\t-\t{self.scenario_name}\t-\t{self.step_name}\t-\t{status}\n"

        self.stream.write(Fore.CYAN + line)

    def result(self, step):
        """
        Called after processing a step (when the step result is known).
        :param step:  Step object with result (after being executed/skipped).
        """
        self.step_name = step.name
        status = step.status.__str__().split('.')[1].upper()
        color = Fore.GREEN if status == 'PASSED' else Fore.RED

        line = f"--\t{self.driver}\t-\t{'STEP'}\t-\t{self.feature_name}" \
               f"\t-\t{self.scenario_name}\t-\t{self.step_name}\t-\t{status}\n"

        self.stream.write(color + line)

    def eof(self):
        """Called after processing a feature (or a feature file)."""
        line = f"--\t{self.driver}\t-\t{'FEATURE'}\t-\t{self.feature_name}\t-\tFINISHED\n"

        self.stream.write(Fore.MAGENTA + line)


class CustomPortalFormatter(Formatter):
    # pylint: disable=too-many-instance-attributes
    name = "portalFormatter"
    description = "Standard colourised portal formatter"

    def __init__(self, stream_opener, config):
        super(CustomPortalFormatter, self).__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.monochrome = not config.color
        self.show_source = config.show_source
        self.show_timings = config.show_timings
        self.show_multiline = config.show_multiline
        self.formats = None

        # -- UNUSED: self.tag_statement = None
        self.steps = []
        self._uri = None
        self._match = None
        self.statement = None
        self.indentations = []
        self.step_lines = 0

    def reset(self):
        # -- UNUSED: self.tag_statement = None
        self.steps = []
        self._uri = None
        self._match = None
        self.statement = None
        self.indentations = []
        self.step_lines = 0

    def uri(self, uri):
        self.reset()
        self._uri = uri

    def feature(self, feature):
        self.print_tags(feature.tags, '')
        print_portal_console(u"%s: %s" % (feature.keyword, feature.name))
        if self.show_source:
            # pylint: disable=redefined-builtin
            print_portal_console(u" # %s" % feature.location)
        print_portal_console("\n")
        self.print_description(feature.description, "  ", False)

    def background(self, background):
        self.replay()
        self.statement = background

    def scenario(self, scenario):
        self.replay()
        self.statement = scenario

    def replay(self):
        self.print_statement()
        self.print_steps()

    def step(self, step):
        self.steps.append(step)

    def match(self, match):
        self._match = match
        self.print_statement()
        self.print_step(Status.executing, self._match.arguments,
                        self._match.location, self.monochrome)

    def result(self, step):
        if not self.monochrome:
            lines = self.step_lines + 1
            if self.show_multiline:
                if step.table:
                    lines += len(step.table.rows) + 1
                if step.text:
                    lines += len(step.text.splitlines()) + 2
            print_portal_console(up(lines))
            arguments = []
            location = None
            if self._match:
                arguments = self._match.arguments
                location = self._match.location
            self.print_step(step.status, arguments, location, True)
        if step.error_message:
            print_portal_console(indent(step.error_message.strip(), u"      "))
            print_portal_console("\n\n")

    def eof(self):
        self.replay()
        print_portal_console("\n")

    def table(self, table):
        cell_lengths = []
        all_rows = [table.headings] + table.rows
        for row in all_rows:
            lengths = [len(escape_cell(c)) for c in row]
            cell_lengths.append(lengths)

        max_lengths = []
        for col in range(0, len(cell_lengths[0])):
            max_lengths.append(max([c[col] for c in cell_lengths]))

        for i, row in enumerate(all_rows):
            print_portal_console("      |")
            for j, (cell, max_length) in enumerate(zip(row, max_lengths)):
                print_portal_console(" ")
                print_portal_console(self.color(cell, None, j))
                print_portal_console(" " * (max_length - cell_lengths[i][j]))
                print_portal_console(" |")
            print_portal_console("\n")

    def doc_string(self, doc_string):
        doc_string = _text(doc_string)
        prefix = u"      "
        print_portal_console(u'%s"""\n' % prefix)
        doc_string = escape_triple_quotes(indent(doc_string, prefix))
        print_portal_console(doc_string)
        print_portal_console(u'\n%s"""\n' % prefix)

    def color(self, cell, statuses, _color):  # pylint: disable=no-self-use
        if statuses:
            return escapes["color"] + escapes["reset"]
        # -- OTHERWISE:
        return escape_cell(cell)

    def indented_text(self, text, proceed):
        if not text:
            return u""

        if proceed:
            indentation = self.indentations.pop(0)
        else:
            indentation = self.indentations[0]

        indentation = u" " * indentation
        return u"%s # %s" % (indentation, text)

    def calculate_location_indentations(self):
        line_widths = []
        for s in [self.statement] + self.steps:
            string = s.keyword + " " + s.name
            line_widths.append(len(string))
        max_line_width = max(line_widths)
        self.indentations = [max_line_width - width for width in line_widths]

    def print_statement(self):
        if self.statement is None:
            return

        self.calculate_location_indentations()
        print_portal_console(u"\n")
        # self.print_comments(self.statement.comments, "  ")
        if hasattr(self.statement, "tags"):
            self.print_tags(self.statement.tags, u"  ")
        print_portal_console(u"  %s: %s " % (self.statement.keyword, self.statement.name))

        location = self.indented_text(six.text_type(self.statement.location), True)
        if self.show_source:
            print_portal_console(location)
        print_portal_console("\n")
        # self.print_description(self.statement.description, u"    ")
        self.statement = None

    def print_steps(self):
        while self.steps:
            self.print_step(Status.skipped, [], None, True)

    def print_step(self, status, arguments, location, proceed):
        if proceed:
            step = self.steps.pop(0)
        else:
            step = self.steps[0]

        print_portal_console("    ")
        print_portal_console(step.keyword + " ")
        line_length = 5 + len(step.keyword)

        step_name = six.text_type(step.name)

        text_start = 0
        for arg in arguments:
            if arg.end <= text_start:
                # -- SKIP-OVER: Optional and nested regexp args
                #    - Optional regexp args (unmatched: None).
                #    - Nested regexp args that are already processed.
                continue
                # -- VALID, MATCHED ARGUMENT:
            assert arg.original is not None
            text = step_name[text_start:arg.start]
            print_portal_console(text)
            line_length += len(text)
            print_portal_console(arg.original)
            line_length += len(arg.original)
            text_start = arg.end

        if text_start != len(step_name):
            text = step_name[text_start:]
            print_portal_console(text)
            line_length += (len(text))

        if self.show_source:
            location = six.text_type(location)
            if self.show_timings and status in (Status.passed, Status.failed):
                location += " %0.3fs" % step.duration
            location = self.indented_text(location, proceed)
            print_portal_console(location)
            line_length += len(location)
        elif self.show_timings and status in (Status.passed, Status.failed):
            timing = "%0.3fs" % step.duration
            timing = self.indented_text(timing, proceed)
            print_portal_console(timing)
            line_length += len(timing)
        print_portal_console("\n")

        self.step_lines = int((line_length - 1))

        if self.show_multiline:
            if step.text:
                self.doc_string(step.text)
            if step.table:
                self.table(step.table)

    def print_tags(self, tags, indentation):
        if not tags:
            return
        line = " ".join("@" + tag for tag in tags)
        print_portal_console(indentation + line + "\n")

    def print_comments(self, comments, indentation):
        if not comments:
            return

        print_portal_console(indent([c.value for c in comments], indentation))
        print_portal_console("\n")

    def print_description(self, description, indentation, newline=True):
        if not description:
            return
        print_portal_console(indent(description, indentation))
        if newline:
            print_portal_console("\n")


def update_feature_scenario_data(old_scenario, new_scenario):
    """
    This method updates the data from the old_scenario.
    :param old_scenario:
    :type old_scenario:
    :param new_scenario:
    :type new_scenario:
    :return:
    :rtype:
    """
    try:
        data = {
            "total_steps": new_scenario.total_steps,
            "steps_passed": new_scenario.steps_passed,
            "steps_failed": new_scenario.steps_failed,
            "steps_skipped": new_scenario.steps_skipped,
            "steps_passed_percent": new_scenario.steps_passed_percent,
            "steps_failed_percent": new_scenario.steps_failed_percent,
            "steps_skipped_percent": new_scenario.steps_skipped_percent,
            "start_time": new_scenario.start_time,
            "end_time": new_scenario.end_time,
            "duration": new_scenario.duration
        }
        return old_scenario.update(data)
    except AttributeError as error:
        logger.error(error)


def format_decimal(value):
    """
    This method transform a float/int to a float with 2 decimal places.
    :param value:
    :type value:
    :return:
    :rtype:
    """
    return f"{value:.2f}"
