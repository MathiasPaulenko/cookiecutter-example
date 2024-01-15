import logging
import os
import re
import time
from copy import deepcopy
from os.path import isfile, isdir

import requests

from behave.parser import parse_file
from flask import flash

from arc.core.paths.directories import get_default_steps_path
from arc.settings.settings_manager import Settings
from arc.web.extensions import db
from arc.web.models.models import TalosSettings, SettingsValue, DataType
from behave.parser import ParserError

logger = logging.getLogger(__name__)
global messages
messages = []
global alerts
alerts = []
global info
info = []


def get_total_features_and_scenarios():
    """
        Return the total of feature files, scenarios and steps in the project
    :return:
    """
    logger.info("Getting total features, scenarios and steps.")

    path_files = os.walk(f"{Settings.TEST_PATH.get(force=True)}")
    file_paths = []
    total_scenarios = 0
    total_steps = 0
    failed_features = []
    for path in path_files:
        # "walk" every folder looking for files.
        path_name = path[0]
        if len(path[2]) > 0 and "__pycache__" not in path_name:
            # If folder have files, then create the key in the files_by_path dictionary.
            for file_name in path[2]:
                # If any file match the extension and file_mode then, add the file to the dictionary.
                logger.info(f"Processing file {file_name} in path {path_name}")
                if file_name.endswith(".feature"):
                    feature_data = None
                    logger.info(f"Parsing feature {os.path.abspath(f'{path_name}/{file_name}')}")
                    try:
                        feature_data = parse_file(os.path.abspath(f"{path_name}/{file_name}"))
                    except(ParserError,) as e:
                        failed_features.append(str(e))
                        logger.error(f"It was impossible to parse '{file_name}', Exception error: {e}")
                    if feature_data:
                        file_paths.append(f"{path_name}/{file_name}")
                        total_scenarios += len(feature_data.scenarios)
                        for scenario in feature_data.scenarios:
                            total_steps += len(scenario.steps)
    logger.info(f"Total features: {len(file_paths)}, total scenarios: {total_scenarios}, total steps: {total_steps}")
    return len(file_paths), total_scenarios, total_steps, failed_features


def get_feature_files():
    """
    This function return a dict with the feature files as key with all the feature and scenario data.
    :return:
    """
    logger.info("Processing feature files to get scenarios and tags info for run page.")
    path_files = os.walk(f"{Settings.TEST_PATH.get(force=True)}")
    files = {}
    failed_features = []
    for path in path_files:
        # "walk" every folder looking for files.
        path_name = path[0]
        if len(path[2]) > 0 and "__pycache__" not in path_name:
            # If folder have files, then create the key in the files_by_path dictionary.
            for file_name in path[2]:
                logger.info(f"Processing file {file_name} in path {path_name}")
                # If any file match the extension and file_mode then, add the file to the dictionary.
                if file_name.endswith(".feature"):
                    logger.info(f"Parsing feature {os.path.abspath(f'{path_name}/{file_name}')}")
                    # Parse the feature file and return a feature objects with all the information about it, the
                    # scenarios and the steps.
                    feature_data = None
                    try:
                        feature_data = parse_file(os.path.abspath(f"{path_name}/{file_name}"))
                    except(ParserError,) as e:
                        failed_features.append(str(e))
                        logger.error(f"It was impossible to parse '{file_name}', Exception error: {e}")
                    if feature_data is None:
                        continue
                    filename = str(file_name).replace(".feature", "")
                    filepath = os.path.abspath(f"{path_name}/{file_name}")
                    last_mod_date = time.strftime("%d/%m/%Y", time.gmtime(os.path.getmtime(filepath)))

                    # Set feature tags and description
                    feature_tags = feature_data.tags
                    feature_description = feature_data.description

                    # Set feature background data.
                    background = feature_data.background
                    background_steps = []
                    if background is not None:
                        for step in background.steps:
                            background_steps.append([step.keyword, step.name])

                    scenarios = {}

                    for index, scenario in enumerate(feature_data.scenarios):
                        scenarios.update({
                            "scenario_" + str(index): {
                                "scenario_type": scenario.keyword,
                                "scenario_name": scenario.name,
                                "scenario_description": scenario.description,
                                "scenario_tags": scenario.tags,
                                "scenario_steps": extract_scenario_steps(scenario.steps),
                                "scenario_examples": extract_scenario_examples(scenario)
                            }
                        })
                    files.update({
                        file_name:
                            {
                                "filename": filename,
                                "filepath": filepath,
                                "modification_date": last_mod_date,
                                "feature_background": background_steps,
                                "feature_tags": feature_tags,
                                "feature_description": feature_description,
                                "scenarios": scenarios
                            }
                    })
    logger.info("Feature files processed")
    return files, failed_features


def extract_scenario_steps(steps):
    """
    This function extract the scenario steps data.

    :param steps:
    :return:
    """
    _scenario_steps = []
    for steps in steps:
        step_data = [steps.keyword, steps.name]
        table = []
        if steps.table is not None:
            table.append(steps.table.headings)
            for row in steps.table.rows:
                row_data = []
                for data in row:
                    row_data.append(data)
                table.append(row_data)
        step_data.append(table)
        _scenario_steps.append(step_data)
    return _scenario_steps


def extract_scenario_examples(scenario):
    """
    This function extract the scenario example values

    :param scenario:
    :return:
    """
    if not hasattr(scenario, 'examples'):
        return {}
    _examples = {}
    for idx, example_data in enumerate(scenario.examples):
        table = [example_data.table.headings]
        for row in example_data.table.rows:
            row_data = []
            for data in row:
                row_data.append(data)
            table.append(row_data)
        _examples.update({
            "example_" + str(idx): {
                "name": example_data.name,
                "tags": example_data.tags,
                "table": table
            }
        })
    return _examples


def get_cfg_files():
    """
    This function return all the cfg files available.

    :return:
    """
    return [file_name for file_name in os.listdir(Settings.CONF_PATH.get(force=True)) if isfile(os.path.join(Settings.CONF_PATH.get(force=True), file_name))]


def get_available_profiles():
    """
    This function return the available profiles.

    :return:
    """
    return [folder_name for folder_name in os.listdir(Settings.PROFILES_PATH.get(force=True)) if isdir(os.path.join(Settings.PROFILES_PATH.get(force=True), folder_name))]


def get_all_tags():
    """
    This function return all the tags in the project.

    :return:
    """
    tags = []
    files, failed = get_feature_files()
    for feature in files.values():
        if type(feature['feature_tags']) == list:
            tags += feature['feature_tags']
        for scenario in feature['scenarios'].values():
            if type(scenario['scenario_tags']) == list:
                tags += scenario['scenario_tags']
                for example in scenario['scenario_examples'].values():
                    tags += example['tags']
    return tags, failed


def check_settings_exists():
    """
    This function check if there is a settings configuration.

    :return:
    """
    if db.session.query(TalosSettings).first() is None:
        create_default_talos_settings()


def create_default_talos_settings():
    """
    This function create an initial settings configuration.
    :return:
    """
    talos_settings = TalosSettings(**{
        "name": "Default Settings",
        "active": True
    })
    db.session.add(talos_settings)
    db.session.commit()
    create_default_talos_settings_values(talos_settings.id)


def create_default_talos_settings_values(talos_settings_id):
    """
    Create the settings configuration values given a talos settings id
    :param talos_settings_id:
    :return:
    """

    talos_settings_values = []
    for key, value in Settings.PROJECT_INFO.items():
        talos_settings_values.append({
            "setting_id": talos_settings_id,
            "name": key,
            "data_type": DataType.STRING,
            "value": value,
        })

    for key, value in Settings.PROXY.items():
        talos_settings_values.append({
            "setting_id": talos_settings_id,
            "name": key,
            "data_type": DataType.STRING,
            "value": value,
        })
    environment_proxy = Settings.PYTALOS_GENERAL.get('environment_proxy', default={})
    execution_proxy = Settings.PYTALOS_GENERAL.get('execution_proxy', default={})
    update_driver = Settings.PYTALOS_GENERAL.get('update_driver', default={})
    logger = Settings.PYTALOS_GENERAL.get('logger', default={})
    autoretry = Settings.PYTALOS_GENERAL.get('autoretry', default={})
    attachments = Settings.PYTALOS_GENERAL.get('attachments', default={})
    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "environment_proxy",
        "data_type": DataType.BOOLEAN,
        "value": environment_proxy.get('enabled', False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "execution_proxy",
        "data_type": DataType.BOOLEAN,
        "value": execution_proxy.get('enabled', False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "update_driver",
        "data_type": DataType.BOOLEAN,
        "value": update_driver.get('enabled_update', False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "update_driver_use_proxy",
        "data_type": DataType.BOOLEAN,
        "value": update_driver.get('enable_proxy', False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "log_level",
        "data_type": DataType.STRING,
        "value": logger.get('file_level', "INFO"),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "continue_after_failed_step",
        "data_type": DataType.BOOLEAN,
        "value": Settings.PYTALOS_RUN.get('continue_after_failed_step', default=False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "autoretry",
        "data_type": DataType.BOOLEAN,
        "value": autoretry.get('enabled', False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "autoretry_attempts",
        "data_type": DataType.INTEGER,
        "value": autoretry.get('attempts', 3),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "autoretry_attempts_wait_seconds",
        "data_type": DataType.INTEGER,
        "value": autoretry.get('attempts_wait_seconds', 1),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "environment",
        "data_type": DataType.STRING,
        "value": Settings.PYTALOS_PROFILES.get('environment', default='cer'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "language",
        "data_type": DataType.STRING,
        "value": Settings.PYTALOS_PROFILES.get('language', default='es'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "repositories",
        "data_type": DataType.BOOLEAN,
        "value": Settings.PYTALOS_PROFILES.get('repositories', default=False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "post_to_alm",
        "data_type": DataType.BOOLEAN,
        "value": Settings.PYTALOS_ALM.get('post_to_alm', default=False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "attachments_pdf",
        "data_type": DataType.BOOLEAN,
        "value": attachments.get('pdf', False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "attachments_docx",
        "data_type": DataType.BOOLEAN,
        "value": attachments.get('docx', False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "attachments_html",
        "data_type": DataType.BOOLEAN,
        "value": attachments.get('html', False),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "match_alm_execution",
        "data_type": DataType.BOOLEAN,
        "value": Settings.PYTALOS_ALM.get('match_alm_execution'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "alm3_properties",
        "data_type": DataType.BOOLEAN,
        "value": Settings.PYTALOS_ALM.get('alm3_properties'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "replicate_folder_structure",
        "data_type": DataType.BOOLEAN,
        "value": Settings.PYTALOS_ALM.get('replicate_folder_structure'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "scenario_name_as_run_name",
        "data_type": DataType.BOOLEAN,
        "value": Settings.PYTALOS_ALM.get('scenario_name_as_run_name'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "post_to_jira",
        "data_type": DataType.BOOLEAN,
        "value": Settings.PYTALOS_JIRA.get('post_to_jira'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "base_url",
        "data_type": DataType.STRING,
        "value": Settings.PYTALOS_JIRA.get('base_url'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "username",
        "data_type": DataType.STRING,
        "value": Settings.PYTALOS_JIRA.get('username'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "password",
        "data_type": DataType.PASSWORD,
        "value": Settings.PYTALOS_JIRA.get('password'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "post_to_octane",
        "data_type": DataType.BOOLEAN,
        "value": Settings.PYTALOS_OCTANE.get('post_to_octane'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "server",
        "data_type": DataType.STRING,
        "value": Settings.PYTALOS_OCTANE.get('server'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "client_id",
        "data_type": DataType.STRING,
        "value": Settings.PYTALOS_OCTANE.get('client_id'),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "secret",
        "data_type": DataType.STRING,
        "value": Settings.PYTALOS_OCTANE.get('secret', ''),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "shared_space",
        "data_type": DataType.STRING,
        "value": Settings.PYTALOS_OCTANE.get('shared_space', ''),
    })

    talos_settings_values.append({
        "setting_id": talos_settings_id,
        "name": "workspace",
        "data_type": DataType.STRING,
        "value": Settings.PYTALOS_OCTANE.get('workspace', ''),
    })

    for value in Settings.PYTALOS_STEPS.get():
        _value = value.split('.')
        talos_settings_values.append({
            "setting_id": talos_settings_id,
            "name": _value[-1],
            "data_type": DataType.BOOLEAN,
            "value": True,
        })

    for talos_settings_value_data in talos_settings_values:
        _talos_settings_value = SettingsValue(**talos_settings_value_data)
        db.session.add(_talos_settings_value)
        db.session.commit()


def kill(pid):
    """
    This function kill a process given a PID.
    :param pid:
    :return:
    """
    import psutil
    process = psutil.Process(int(pid))
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


def update_messages(message):
    """
    This function add new messages to the global variable messages.

    :param message:
    :return:
    """
    messages.append(message)
    return messages


def clean_messages():
    """
    This function clear the messages of the global variables messages.
    :return:
    """
    messages.clear()


def get_message():
    """
    This function return the messages stored in the global variable messages.
    :return:
    """
    return messages


def update_alert(alert):
    """
    This function update the alert message.
    :return:
    """
    alerts.append(alert)


def clean_alerts():
    """
    This function clear the alerts of the global variables alerts.
    :return:
    """
    alerts.clear()


def get_alert():
    """
    This function return the alert stored in the global variable alerts.
    :return:
    """
    temp_alerts = deepcopy(alerts)
    clean_alerts()
    return temp_alerts


def update_info(info_message):
    """
    This function update the alert message.
    :return:
    """
    info.append(info_message)


def clean_info():
    """
    This function clear the alerts of the global variables alerts.
    :return:
    """
    info.clear()


def get_info():
    """
    This function return the alert stored in the global variable alerts.
    :return:
    """
    temp_info = deepcopy(info)
    clean_info()
    return temp_info


def print_portal_console(line):
    """
    This function send a line of text from the CustomPortalFormatter to the real time console in the web.
    """
    try:
        send_request_portal('post', 'data', line, path='/view-executions')
    except (Exception,) as ex:
        logging.error(ex)


def send_alert_portal(line):
    """
    This function send a line of text from the CustomPortalFormatter to the real time console in the web.
    """
    try:
        send_request_portal('post', 'data', line, path='/send-alerts')
    except (Exception,) as ex:
        logging.error(ex)


def send_info_portal(line):
    """
    This function send a line of text from the CustomPortalFormatter to the real time console in the web.
    """
    try:
        send_request_portal('post', 'data', line, path='/send-info')
    except (Exception,) as ex:
        logging.error(ex)


def send_request_portal(method, data_type='', data='', path=''):
    """
    This function allow to send a request to the portal and return the response.
    :param method:
    :param data_type:
    :param data:
    :param path:
    :return:
    """
    port = Settings.PYTALOS_WEB.get('port')
    url = f'http://127.0.0.1:{port}'
    url = f'{url}{path}'
    response = ''
    if method == 'get':
        response = requests.get(url)
    if method == 'post':
        if data_type == 'json':
            response = requests.post(url=url, json=data)
        if data_type == 'data':
            response = requests.post(url=url, data=data)
    return response


def test_is_running():
    """
    This function check if there's a current PID in to environ variables.
    If so, the add a flash message and return True.
    If not, return False.
    :return:
    """
    pid = os.environ.get('pid')
    if pid is None:
        return False
    if pid != "0":
        flash("A current test is executing at this moment."
              " Please wait until it is finished in order to start another test.", "warning")
        return True
    return False


def set_setting_value(section, option, value):
    """
    This function receives a settings module, the section to update, the options and the value.
    The section would be something like PYTALOS_GENERAL
    The options would be something like environment_proxy.enabled
    The value would be a boolean, string or int.
    :param section:
    :param option:
    :param value:
    :return:
    """
    getattr(Settings, section).set(options=option, value=value)
    logger.info(f"Set value {value} to section {section} and path {option}")


def get_all_files(path):
    filelist = os.listdir(path)
    files = {}

    for i in filelist:
        filepath = path + "/" + i
        if not os.path.isfile(filepath):
            files.update({
                i: {
                    "content": get_all_files(filepath),
                    "extension": "folder",
                }
            })
        else:
            file_data = i.split(".")
            files.update({
                i: {
                    "filename": file_data[0],
                    "extension": file_data[1],
                    "path": os.path.abspath(filepath).replace("\\", "/")
                }
            })
    return files


def get_keywords_files(path):
    step_filelist = os.listdir(path)
    name_files = []
    for j in range(len(step_filelist)):
        step_filelist[j] = path + "/" + step_filelist[j]
        if step_filelist[j].endswith(".py"):
            filename = ""
            if step_filelist[j].__contains__("arc"):
                filename = step_filelist[j]
            if step_filelist[j].__contains__("test"):
                filename = step_filelist[j]
            name_files.append(filename)
    return name_files


def get_keywords_directories(path):
    filelist = os.listdir(path)
    directories = []
    for i in filelist:
        filepath = path + "/" + i
        if not os.path.isfile(filepath):
            directories.append(filepath)
            directories = directories + get_keywords_directories(filepath)
    return directories


def get_step_list():
    """
    :return:
    """

    talos_settings = db.one_or_404(db.select(TalosSettings).filter_by(active=1))
    core_steps_imported = talos_settings.get_settings_values_imported_steps()
    path_core_steps = []
    steps_paths = get_default_steps_path()
    for _setting in core_steps_imported:
        if _setting.name in steps_paths and _setting.value == "1":
            path_core_steps.append(f"{Settings.BASE_PATH.get(force=True)}/{steps_paths[_setting.name].replace('.', '/')}.py")

    path_user_steps = f"{Settings.TEST_PATH.get(force=True)}/steps"
    path_user_steps = os.path.abspath(path_user_steps)
    # return and store all path directories with files from steps folders
    directories = get_keywords_directories(path_user_steps)
    cont_steps = 0
    step_dictionary = {}
    for no_file in range(len(directories)):
        # return all files with extension .py with directories paths
        step_filelist = get_keywords_files(directories[no_file])
        step_filelist += path_core_steps
        for steps_file in step_filelist:
            try:
                # get steps with descriptions
                steps = []
                descriptions = []
                # read all file
                with open(steps_file, 'r', encoding="utf-8") as fr:
                    code = fr.readlines()
                    fr.close()
                # review line by line to search steps
                for line_code_number in range(len(code)):
                    # get decorator to indicate step definition and get info
                    if code[line_code_number].__contains__("@step"):
                        if code[line_code_number].endswith(")"):
                            step = code[line_code_number]
                            steps.append(step)
                            cont = line_code_number
                            cont += 2
                            if code[cont].__contains__("\"\"\""):
                                description = code[cont]
                                cont += 1
                                while not code[cont].__contains__("\"\"\""):
                                    description = description + code[cont]
                                    cont += 1
                                descriptions.append(description)
                            else:
                                descriptions.append("No description")
                        else:
                            cont = line_code_number
                            step = ""
                            while not code[cont].strip().startswith("def"):
                                step = step + code[cont].replace("\n", "").strip()
                                cont = cont + 1
                            step = step + "\n"
                            steps.append(step)
                            cont += 1
                            if code[cont].__contains__("\"\"\""):
                                description = code[cont].replace("\n", "")
                                cont += 1
                                while not code[cont].__contains__("\"\"\""):
                                    description = description + code[cont]
                                    cont += 1
                                descriptions.append(description)
                            else:
                                descriptions.append("No description")
                # in all steps found remove decorators and useful info
                steps_found = {}
                for x in range(len(steps)):
                    cont_steps += 1
                    text_step = steps[x]
                    text_step = text_step.strip()
                    text_step = text_step[:len(text_step) - 1]
                    text_step = text_step.replace("@step(u", "")
                    text_step = text_step.replace("@step(", "")
                    text_step = text_step.strip()
                    if text_step.startswith("\""):
                        text_step = re.findall(r'"(.*?)"', text_step)
                    elif text_step.startswith("'"):
                        text_step = re.findall(r"'(.*?)'", text_step)
                    text = ""
                    for parts in text_step:
                        text = text + parts
                    steps_found.update({"step" + str(cont_steps): {
                        "step-definition": text,
                        "description": descriptions[x].replace("\"\"\"", "")
                    }})
                # Save steps with the namefile and the steps found
                file_path = steps_file
                index_slash = ""
                for x in range(len(file_path)):
                    if str(file_path[x]) == "/":
                        index_slash = x
                file_name = file_path[(index_slash + 1):(len(file_path) - 3)]
                step_dictionary.update({file_name: steps_found})
            except OSError:
                return "Could not read File"
    return step_dictionary
