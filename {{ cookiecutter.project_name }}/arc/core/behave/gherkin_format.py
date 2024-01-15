# -*- coding: utf-8 -*-
"""
Functions for parsing and obtaining behave parameter within the description.
The Behave parameters of the scenarios outlines that appear <param> with within the description will be changed to
the value of the iteration of the example table that corresponds to the parameter.
"""
import logging

logger = logging.getLogger(__name__)


def generate_scenario_description(scenario):
    """
    Generating and parsing description values and setting within the scenario.description attribute.
    :param scenario:
    :return:
    """
    try:
        if scenario.keyword == "Scenario":
            line_num = _get_scenario_line(scenario, scenario.name)
            description = _get_scenario_description(scenario, line_num)
            final_description = _parse_list(description)
            scenario.description = final_description
        elif scenario.keyword == "Scenario Outline":
            headers_name = _get_example_table_headers(scenario)
            data_table = _parse_data_to_list(scenario, len(headers_name))
            example_data_dict = _combine_headers_with_data(headers_name, data_table)
            scenario_name = _get_scenario_outline_name(scenario, example_data_dict)
            line_num = _get_scenario_line(scenario, scenario_name)
            description = _get_scenario_description(scenario, line_num)
            description_parsed = _parse_example_value(description, example_data_dict)
            final_description = _parse_list(description_parsed)
            scenario.description = final_description
            logger.debug(f"Scenario description generated: {final_description}")
    except TypeError as ex:
        logger.debug(ex)
    except (Exception,) as ex:
        logger.debug(ex)


def _parse_list(initial_list):
    """
    Parser initial list
    :param initial_list:
    :return:
    """
    final_list = []
    for line in initial_list:
        line = line.replace("\"\"\"", "").strip()
        if line != '':
            final_list.append(line)

    return final_list


def _get_scenario_description(scenario, line_num):
    """
    Gets scenario description from scenario and line number
    :param scenario:
    :param line_num:
    :return:
    """
    verbs = ('given', 'when', 'then', 'and', 'but', 'scenario', 'background', 'examples', 'feature', '#')
    feature_file = open(scenario.feature.filename, encoding='utf8')
    lines = feature_file.readlines()
    description = []
    line_cont = 0
    while True:
        line_text = lines[line_num + line_cont].rstrip().strip()
        if line_text.lower().startswith(verbs):
            break
        else:
            description.append(line_text)
        line_cont += 1

    return description


def _parse_example_value(desc_list, example_dict):
    """
    Parse of scenario example table
    :param desc_list:
    :param example_dict:
    :return:
    """
    aux_list = []
    for line in desc_list:
        words = line.split(" ")
        _aux = ""
        for word in words:
            if _contain_re(word):
                words_split = word.split('<')[1].split('>')[0]
                word = word.replace(f'<{words_split}>', example_dict[words_split])
            _aux += " " + word
        aux_list.append(_aux)
    return aux_list


def _get_scenario_outline_name(scenario, example_data_dict):
    """
    Gets scenario outline name from example table
    :param scenario:
    :param example_data_dict:
    :return:
    """
    sc = str(scenario.name).split('--')[0].strip()
    scenario_name = f'{scenario.keyword}: {sc}'
    for data_value in example_data_dict.values():
        if data_value in scenario_name:
            key = list(example_data_dict.keys())[list(example_data_dict.values()).index(data_value)]
            scenario_name = scenario_name.replace(data_value, f'<{key}>')

    return scenario_name


def _combine_headers_with_data(headers_list, data_list):
    """
    Union of the headers of the example table with their corresponding data.
    :param headers_list:
    :param data_list:
    :return:
    """
    example_data = {}
    for index, headers in enumerate(headers_list, 0):
        example_data[headers] = data_list[index]

    return example_data


def _parse_data_to_list(scenario, headers_len):
    """
    Parse data from scenario to list
    :param scenario:
    :param headers_len:
    :return:
    """
    scenario_file = open(scenario.feature.filename, encoding='utf8')
    lines = scenario_file.readlines()
    data_table = str(lines[scenario.line - 1]).rstrip().split('|')
    data = []
    first_data_index = None
    for index, header in enumerate(data_table, 0):
        if header.isspace():
            header = header.replace(" ", "")
        header = header.strip()
        if header != '':
            if first_data_index is None:
                first_data_index = index
            data.append(header)
            headers_len -= 1
        if header == '' and first_data_index and headers_len != 0:
            data.append(header)
            headers_len -= 1

    return data


def _get_example_table_headers(scenario):
    """
    Get example table headers from scenario
    :param scenario:
    :return:
    """
    scenario_file = open(scenario.feature.filename, encoding='utf8')
    lines = scenario_file.readlines()
    headers = []
    cont = 1
    while True:
        example_line = scenario.line - cont
        if 'Examples' in lines[example_line]:
            example_header = lines[example_line + 1].rstrip().split('|')
            for header in example_header:
                header = header.replace(" ", "")
                header.split()
                if header != '':
                    headers.append(header)
            break
        cont += 1
    return headers


def _get_scenario_line(scenario, scenario_name):
    """
    Get file line number from scenario file and scenario name
    :param scenario:
    :param scenario_name:
    :return:
    """
    with open(scenario.feature.filename, encoding='utf8') as file:
        for num, line in enumerate(file, 1):
            if scenario_name in line:
                return num


def _contain_re(initial_value):
    """
    Check if a description have < and > chars
    :param initial_value:
    :return:
    """
    if "<" in str(initial_value) and ">" in str(initial_value):
        return True
    else:
        return False
