# -*- coding: utf-8 -*-
"""
Talos profile data collection file functions.
"""
import json
import logging
import os.path

from functools import reduce
from os import walk
from arc.contrib.tools import files, excel, csv
from arc.core.test_method.exceptions import TalosErrorReadFile, TalosResourceNotFound
from arc.settings.settings_manager import Settings
from arc.web.app.utils import send_alert_portal

logger = logging.getLogger(__name__)


def get_profile_data():
    """
    Load and return userdata from JSON configuration file.
    """
    logger.debug("Obtaining data from profile data")
    userdata = {'Config_environment': os.environ.get('Config_environment', Settings.PYTALOS_PROFILES.get('environment'))}
    json_total = get_dict_from_files(userdata)
    return json_total


def get_dict_from_files(userdata):
    """
    Reading of the profile files according to the configured environment.
    Converts the information in the files into a data dictionary.
    :param userdata:
    :return dict:
    """
    c_file = None
    try:
        json_total = {}
        dict_paths = {}
        env = Settings.PYTALOS_PROFILES.get('environment')
        env_dir = os.path.abspath("settings/profiles") + os.sep + env + os.sep
        logger.debug(f"Reading profile data from {env_dir}")
        start_path = env_dir.rfind(os.sep) + 1
        list_files = []
        for path, dirs, filenames in walk(env_dir):
            folders = path[start_path:].split(os.sep)
            parent = reduce(dict.get, folders[:-1], json_total)
            parent2 = reduce(dict.get, folders[:-1], dict_paths)
            files_dict = {}
            files_path = {}
            if folders[0] != '':
                subdir = dict.fromkeys(filenames)
                parent[folders[-1]] = subdir
                parent2[folders[-1]] = subdir
            logger.debug(f"Profile files found in {env}: {filenames}")
            for current_file in filenames:
                c_file = current_file
                list_files.append(current_file)
                index_extension = current_file.rfind('.')
                if os.path.isfile(os.path.join(path + os.sep + current_file)):
                    if current_file.endswith(".json"):
                        aux = json.load(open(path + os.sep + current_file, encoding="utf8"))
                        files_dict[current_file[:index_extension]] = aux
                        files_path[current_file] = aux
                    elif current_file.endswith(".yaml"):
                        aux = files.yaml_to_dict(path + os.sep + current_file)
                        files_dict[current_file[:index_extension]] = aux
                        files_path[current_file] = aux
                    elif current_file.endswith(".xlsx"):
                        excel_wrapper = excel.ExcelWrapper(path + os.sep + current_file)
                        excel_wrapper.set_all_sheets_header(1)
                        aux = excel_wrapper.all_sheets_to_dict()
                        files_dict[current_file[:index_extension]] = aux
                        files_path[current_file] = aux
                    elif current_file.endswith(".csv"):
                        csv_wrapper = csv.CSVWrapper(path + os.sep + current_file)
                        csv_wrapper.set_sheet_header(1)
                        aux = csv_wrapper.current_sheet_to_dict()
                        files_dict[current_file[:index_extension]] = aux
                        files_path[current_file] = aux
                    else:
                        pass

            if folders[-1] != '':
                parent[folders[-1]] = files_dict
                parent2[folders[-1]] = files_path
            else:
                json_total = files_dict
                dict_paths = files_path

        logger.debug("Generating data dictionary")
        json_total.setdefault('profiles_paths', {})
        json_total['profiles_paths'][env] = dict_paths
        for file in list_files:
            index = file.rfind('.')
            key_name = file[:index]
            if key_name in userdata:
                del userdata[key_name]

        return json_total

    except Exception as ex:
        msg = f"Error in {c_file}: Data could not be imported. {ex}"
        logger.exception(msg)
        if os.environ.get('EXECUTION_TYPE') == 'Portal':
            send_alert_portal(msg)
        raise TalosErrorReadFile(msg)


def check_exist_environment_path():
    """
    Check if the environment configured in the settings exists as a profile folder. If the folder with the name of the
    environment does not exist, throw a TalosResourcesNotFound exception.
    """
    env = Settings.PYTALOS_PROFILES.get('environment')
    logger.info(f"Environment configured: {env}")
    env_dir = os.path.abspath("settings/profiles") + os.sep + env + os.sep
    if os.path.exists(env_dir) is False:
        msg = f"The environment {env} does not exist in settings/profiles. " \
              f"Please change it in settings file in section PYTALOS_PROFILES"
        logger.exception(msg, exc_info=False)
        raise TalosResourceNotFound(msg)
