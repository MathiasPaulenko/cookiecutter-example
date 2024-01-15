# -*- coding: utf-8 -*-
"""
File of configuration and implementation of the template variables.
"""
import logging
import re
from copy import deepcopy
from colorama import Fore

from arc.settings.settings_manager import Settings

global template_var_dict
template_var_dict = {}

logger = logging.getLogger(__name__)


def find_match(self, step):
    """
    Function of localization of steps and passage of values of the template var to the arguments of the steps.
    :param self:
    :param step:
    :return:
    """
    candidates = self.steps[step.step_type]
    more_steps = self.steps["step"]
    if step.table:
        template_var_tables_steps(step.table)
    if step.step_type != "step" and more_steps:
        # -- ENSURE: self.step_type lists are not modified/extended.
        candidates = list(candidates)
        candidates += more_steps
    for step_definition in candidates:
        result = step_definition.match(step.name)
        if result:
            for argument in result.arguments:
                argument.value = get_template_var_value(argument.value)
            return result
    return None


def get_template_var_value(argument):
    """
    Send to step de template var value with the format
    :param argument:
    :return:
    """
    logger.debug('Getting template var data values')
    regex_profiles = r"\${{(.*?)\}\}"
    matchers_profiles = re.findall(regex_profiles, argument)
    regex_repositories = r"\&{{(.*?)\}\}"
    matchers_repositories = re.findall(regex_repositories, argument)
    if matchers_profiles:
        for match in matchers_profiles:
            value = get_value_from_profiles(match)
            if len(argument) > len(match) + 5:
                start = argument.find("${{" + match + "}}")
                end = start + 3 + len(match) + 2
                argument = argument[:start] + value + argument[end:]
            else:
                argument = value
    if matchers_repositories:
        for match in matchers_repositories:
            value = get_value_from_repositories(match)
            if len(argument) > len(match) + 5:
                start = argument.find("&{{" + match + "}}")
                end = start + 3 + len(match) + 2
                argument = argument[:start] + value + argument[end:]
            else:
                argument = value
    logger.debug(f"Passing the template var value: {argument}")
    return argument


def replace_template_var(text):
    """
    Given the current line (step or scenario name) search the number of template vars and return the name
    with the substituted template var
    :param text:
    :return:
    """
    text = get_template_var_profiles(text)
    text = get_template_var_repositories(text)
    return text


def get_template_var_profiles(text):
    """
    Get the template var from profiles
    """
    regex = r"\${{(.*?)\}\}"
    matchers = re.findall(regex, text)
    for match in matchers:
        start = text.find("${{" + match + "}}")
        end = start + 3 + len(match) + 2
        template_var = text[start:end]
        value = get_value_from_profiles(match)
        text = format_string(value, text, template_var, start, end)
    return text


def get_value_from_profiles(template_var):
    """
    Obtaining values from the data of the profiles files.
    :param template_var:
    :return:
    """
    template_var = template_var.strip()
    list_files = template_var_dict.get('profiles')
    if ':' in template_var:
        aux = template_var.split(':')
        profile_file = aux[0]
        logger.debug(f'Getting template var value from: {profile_file}')
        match = aux[1]
    else:
        profile_file = Settings.PYTALOS_PROFILES.get('master_file')
        logger.debug(f'Getting template var value from: {profile_file}')
        match = template_var
    params_list = match.split('.')
    if str(profile_file).__contains__('.'):
        aux = profile_file.split('.')
        for current_file in aux:
            list_files = list_files.get(current_file)
        dict_json = list_files
    else:
        dict_json = list_files.get(profile_file)
    if dict_json:
        aux_json = deepcopy(dict_json)
        for param in params_list:
            if type(aux_json) is list:
                try:
                    aux_json = aux_json[int(param)]
                except IndexError:
                    logger.warning(Fore.YELLOW +
                        f"Processing template var: {template_var}. Index out of range.")
            else:
                aux_json = aux_json.get(param)
                if aux_json is None:
                    logger.warning(f"Processing template var: {template_var}. {param} is not created in file {profile_file}.")
                    print(Fore.YELLOW +
                        f"Processing template var: {template_var}. {param} is not created in file {profile_file}.")
        return aux_json
    else:
        print(Fore.YELLOW +
              f"Processing template var: {template_var}. {profile_file} is not created in this environment.")
        logger.warning(f"Processing template var: {template_var}. {profile_file} is not created in this environment.")


def get_template_var_repositories(text):
    """
    Get the template var from repositories
    """
    regex = r"\&{{(.*?)\}\}"
    matchers = re.findall(regex, text)
    for match in matchers:
        start = text.find(match) - 3
        end = text.find(match) + len(match) + 2
        template_var = text[start:end]
        value = get_value_from_repositories(match)
        text = format_string(value, text, template_var, start, end)
    return text


def get_value_from_repositories(template_var):
    """
    Given the value ${{value}} or &{{value}} return the corresponding value
    """
    template_var = template_var.strip()
    list_files = template_var_dict.get('repositories')
    if ':' in template_var:
        aux = template_var.split(':')
        template_file = aux[0]
        match = aux[1]
        params_list = match.split('.')
        if str(template_file).__contains__('.'):
            aux = template_file.split('.')
            for current_file in aux:
                list_files = list_files.get(current_file)
            dict_json = list_files
        else:
            dict_json = list_files.get(template_file)
        if dict_json:
            aux_json = deepcopy(dict_json)
            for param in params_list:
                if type(aux_json) is list:
                    try:
                        aux_json = aux_json[int(param)]
                    except IndexError:
                        logger.warning(Fore.YELLOW +
                            f"Processing template var: {template_var}. Index out of range.")
                else:
                    aux_json = aux_json.get(param)
                    if aux_json is None:
                        print(Fore.YELLOW +
                            f"Processing template var: {template_var}. {param} is not created in file {template_file}.")
                        logger.warning(f"Processing template var: {template_var}. {param} is not "
                            f"created in file {template_file}.")
            return aux_json
        else:
            print(Fore.YELLOW +
                f"\nProcessing template var: {template_var}. {template_file} is not created in this environment.")
            logger.warning(f"Processing template var: {template_var}. {template_file} is not created in this environment.")
    else:
        print(Fore.YELLOW +
            f"\nProcessing template var: {template_var}. File is not defined in template var")

        logger.warning(f"Processing template var: {template_var}. File is not defined in template var")


def format_string(value, text, template_value, start, end):
    """
    Given the value check the length of the template var and replace it with the value if it is less than 50
    characters or <type>=(template var) if it is more than 50 characters
    """
    if type(value) is list and len(str(value)) > 50:
        final_value = f"list={template_value[3:-2]}"
    elif type(value) is dict:
        final_value = f"dict={template_value[3:-2]}"
    elif type(value) is tuple:
        final_value = f"tuple={template_value[3:-2]}"
    else:
        final_value = str(value)
    text = f"{text[:start]}{final_value}{text[end:]}"

    return text


def template_var_tables_steps(table):
    """
    Replace the template var of the table, can be replaced from header or row
    """
    # Check template var in headers
    for current_header in range(0, len(table.headings)):
        value = table.headings[current_header]
        table.headings[current_header] = str(get_template_var_value(value))

    # Check template var in rows
    for current_row in range(0, len(table.rows)):
        for current_cell in range(0, len(table.rows[current_row].cells)):
            value = table.rows[current_row].cells[current_cell]
            table.rows[current_row].cells[current_cell] = str(get_template_var_value(value))


def get_global():
    return template_var_dict
