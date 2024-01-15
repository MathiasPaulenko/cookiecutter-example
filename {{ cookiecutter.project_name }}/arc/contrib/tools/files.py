# -*- coding: utf-8 -*-
"""
Module of useful functions for file management and handling.
"""
import inspect
import json
import logging
import os
import yaml
import warnings
import functools

from arc.settings.settings_manager import Settings
from copy import deepcopy

global files_to_edit
files_to_edit = {}

string_types = (type(b''), type(u''))


def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    if isinstance(reason, string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2
                )
                warnings.simplefilter('default', DeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(
                fmt2.format(name=func2.__name__),
                category=DeprecationWarning,
                stacklevel=2
            )
            warnings.simplefilter('default', DeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))


logger = logging.getLogger(__name__)

PROFILE_PATH = "settings/profiles"


def is_file_exist(file_path):
    """
    Check if a file exist.
    :param file_path:
    :return:
    """
    _check = os.path.isfile(file_path)
    logger.debug(f'Check if file {file_path} exist: {_check}')
    return _check


def yaml_to_dict(file_path):
    """
    Convert a yaml file to dict.
    :param file_path:
    :return:
    """
    logger.debug(f'Converting yaml to dict: {file_path}')
    yaml_file = open(file_path, encoding='utf8')
    return yaml.load(yaml_file, Loader=yaml.FullLoader)


def json_to_dict(file_path):
    """
    Convert a json file to dict.
    :param file_path:
    :return:
    """
    logger.debug(f'Converting json to dict: {file_path}')
    with open(file_path, encoding='utf8') as file:
        return json.load(file)


def get_json_value_key_path(param_path_key, file_path, sep_char: str = "."):
    """
    Return a json value from dot-separated key path.
    :param param_path_key:
    :param file_path:
    :param sep_char:
    :return:
    """
    params_list = param_path_key.split(sep_char)
    dict_json = json_to_dict(file_path)
    aux_json = deepcopy(dict_json)

    for param in params_list:
        if type(aux_json) is list:
            aux_json = aux_json[int(param)]
        else:
            aux_json = aux_json[param]
    logger.debug(f'json value return: {aux_json} from file: {file_path}')
    return aux_json


@deprecated
def set_value_json_path(file_path, key, value):
    """
    Set a value in json file in a key.
    :param file_path:
    :param key:
    :param value:
    :return:
    """

    logger.debug(f'Including value {value} in key {key} in file: {file_path}')
    with open(file_path, encoding='utf8') as json_file:
        json_decoded = json.load(json_file)

    keys = key.split('.')
    last_key = keys[-1]
    json_decoded = update_dict_value_by_key(json_decoded, last_key, keys, value)

    with open(file_path, 'w', encoding='utf8') as json_file:
        json.dump(json_decoded, json_file)


@deprecated
def replace_value_json_path(file_path, key, string_to_search, value):
    """
    Replace a json file value from new value and a string to search.
    :param file_path:
    :param key:
    :param string_to_search:
    :param value:
    :return:
    """
    logger.debug(f'Replacing value {value} in key {key} in file: {file_path}')
    with open(file_path, 'r', encoding='utf8') as json_file:
        json_decoded = json.load(json_file)
    keys = key.split('.')
    last_key = keys[-1]
    json_decoded = replace_dict_value_by_key(json_decoded, last_key, string_to_search, keys, value)

    with open(file_path, 'w', encoding='utf8') as json_file:
        json.dump(json_decoded, json_file)


@deprecated
def replace_dict_value_by_key(json_decoded, last_key, search_string, keys, value):
    """
    Replace a value of a dict by key.
    :param json_decoded:
    :param last_key:
    :param search_string:
    :param keys:
    :param value:
    :return:
    """
    logger.debug(f'Replacing value {value} in key {keys} in json')
    for key in keys:
        if json_decoded.get(key):
            if key == last_key:
                search_string = search_string.replace('\\', '')
                json_decoded[last_key] = json_decoded[last_key].replace(search_string, value)
            else:
                keys = keys[1:]
                replace_dict_value_by_key(json_decoded[key], last_key, search_string, keys, value)
    return json_decoded


@deprecated
def delete_value_json_path(file_path, key):
    """
    Delete a value in a json file from a passed key.
    :param file_path:
    :param key:
    :return:
    """
    logger.debug(f"Deleting value with key {key} in file: {file_path}")
    with open(file_path, encoding='utf8') as json_file:
        json_decoded = json.load(json_file)

    del json_decoded[key]

    with open(file_path, 'w', encoding='utf8') as json_file:
        json.dump(json_decoded, json_file)


def set_value_yaml_path(file_path, key, values):
    """
    Set a value in a yaml file passed file path.
    :param file_path:
    :param key:
    :param values:
    :return:
    """
    logger.debug(f'Including value {values} in key {key} in file: {file_path}')
    with open(file_path, encoding='utf8') as f:
        doc = yaml.load(f, Loader=yaml.FullLoader)

    doc[key] = values

    with open(file_path, 'w', encoding='utf8') as f:
        yaml.dump(doc, f)


def update_dict_value_by_key(json_decoded, last_key, keys, value):
    """
    Update a value in a dict by key.
    :param json_decoded:
    :param last_key:
    :param keys:
    :param value:
    :return:
    """
    logger.debug(f'Updating value {value} in key {keys} in json')
    if len(keys) == 1:
        if type(json_decoded) is list:
            key = int(keys[0])
        else:
            key = keys[0]
        json_decoded[key] = value
    else:
        key = keys[0]
        if type(json_decoded) is list:
            key = int(key)
        if type(json_decoded) is list or json_decoded.get(key):
            if key == last_key:
                json_decoded[last_key] = value
            else:
                keys = keys[1:]
                update_dict_value_by_key(json_decoded[key], last_key, keys, value)
        else:
            if key == last_key:
                json_decoded[last_key] = value
            else:
                json_decoded[key] = {}
                keys = keys[1:]
                update_dict_value_by_key(json_decoded[key], last_key, keys, value)
    return json_decoded


def delete_value_yaml_path(file_path, key):
    """
    Delete a value in a yaml file passed the file path by key.
    :param file_path:
    :param key:
    :return:
    """
    logger.debug(f'Deleting key {key} in file:{file_path}')
    with open(file_path, encoding='utf8') as f:
        doc = yaml.load(f, Loader=yaml.FullLoader)

    del doc[key]

    with open(file_path, 'w', encoding='utf8') as f:
        yaml.dump(doc, f)


@deprecated
def set_profile_data_value(file_name, key, value, change_all_profiles=True):
    """
    Set a value in profile json data by file name and key and value.
    :param file_name:
    :param key:
    :param value:
    :param change_all_profiles:
    :return:
    """

    directory_list = []
    file_names = []
    logger.debug(f"Including value {value} in key {key} in profile file: {file_name}")
    for root, dirs, files in os.walk(PROFILE_PATH, topdown=False):
        for file in files:
            if file not in file_names:
                file_names.append(file)
        for name in dirs:
            directory_list.append(name)
    if change_all_profiles:
        for directory in directory_list:
            for file in file_names:
                if file.split(".")[0] == file_name:
                    try:
                        path = PROFILE_PATH + directory + "/" + file
                        if file.split(".")[1] == "json":
                            set_value_json_path(path, key, value)
                        elif file.split(".")[1] == "yaml":
                            set_value_yaml_path(path, key, value)
                    except FileNotFoundError:
                        pass
    else:
        for file in file_names:
            if file.split(".")[0] == file_name:
                try:
                    path = PROFILE_PATH + Settings.PYTALOS_PROFILES.get('environment') + "/" + file
                    if file.split(".")[1] == "json":
                        set_value_json_path(path, key, value)
                    elif file.split(".")[1] == "yaml":
                        set_value_yaml_path(path, key, value)
                except FileNotFoundError:
                    pass


@deprecated
def replace_profile_data_value(file_name, key, string_to_search, value, change_all_profiles=True):
    """
    Replace a value in profile json data by file name and key and value.
    :param file_name:
    :param key:
    :param string_to_search:
    :param value:
    :param change_all_profiles:
    :return:
    """
    logger.debug(f"Replacing value {string_to_search} in key {key} for {value} in profile file: {file_name}")
    directory_list = []
    file_names = []

    for root, dirs, files in os.walk(PROFILE_PATH, topdown=False):
        for file in files:
            if file not in file_names:
                file_names.append(file)
        for name in dirs:
            directory_list.append(name)
    if change_all_profiles:
        for directory in directory_list:
            for file in file_names:
                if file.split(".")[0] == file_name:
                    try:
                        path = PROFILE_PATH + "/" + directory + "/" + file
                        if file.split(".")[1] == "json":
                            replace_value_json_path(path, key, string_to_search, value)
                        elif file.split(".")[1] == "yaml":
                            set_value_yaml_path(path, key, value)
                    except FileNotFoundError:
                        pass
    else:
        for file in file_names:
            if file.split(".")[0] == file_name:
                try:
                    path = PROFILE_PATH + "/" + Settings.PYTALOS_PROFILES.get('environment') + "/" + file
                    if file.split(".")[1] == "json":
                        replace_value_json_path(path, key, string_to_search, value)
                    elif file.split(".")[1] == "yaml":
                        set_value_yaml_path(path, key, value)
                except FileNotFoundError:
                    pass


@deprecated
def delete_profile_data_value(file_name, key, change_all_profiles=True):
    """
    Delete a value in profile json data by file name and key and value.
    :param file_name:
    :param key:
    :param change_all_profiles:
    :return:
    """
    logger.debug(f'Deleting the key {key} in profile file: {file_name}')
    directory_list = []
    file_names = []

    for root, dirs, files in os.walk(PROFILE_PATH, topdown=False):
        for file in files:
            if file not in file_names:
                file_names.append(file)
        for name in dirs:
            directory_list.append(name)
    if change_all_profiles:
        for directory in directory_list:
            for file in file_names:
                if file.split(".")[0] == file_name:
                    try:
                        path = "settings/profiles/" + directory + "/" + file
                        if file.split(".")[1] == "json":
                            delete_value_json_path(path, key)
                        elif file.split(".")[1] == "yaml":
                            delete_value_yaml_path(path, key)
                    except FileNotFoundError:
                        pass
    else:
        for file in file_names:
            if file.split(".")[0] == file_name:
                try:
                    path = "settings/profiles/" + Settings.PYTALOS_PROFILES.get('environment') + "/" + file
                    if file.split(".")[1] == "json":
                        delete_value_json_path(path, key)
                    elif file.split(".")[1] == "yaml":
                        delete_value_yaml_path(path, key)
                except FileNotFoundError:
                    pass


def delete_key_json(json_decoded, last_key, keys):
    if len(keys) == 1:
        if type(json_decoded) is list:
            key = int(keys[0])
        else:
            key = keys[0]
        del json_decoded[key]
    else:
        key = keys[0]
        if type(json_decoded) is list:
            key = int(key)
        if type(json_decoded) is list or json_decoded.get(key):
            if key == last_key:
                del json_decoded[last_key]
            else:
                keys = keys[1:]
                delete_key_json(json_decoded[key], last_key, keys)
    return json_decoded


def delete_data_value(context, settings_type, file_name, key):
    files_dir = context.config.userdata
    files_dir = files_dir.get(settings_type)
    path = ""
    file_path = ""
    env = Settings.PYTALOS_PROFILES.get('environment')
    if settings_type == 'profiles':
        path = files_dir['profiles_paths'][env]
        file_path = os.path.join(Settings.SETTINGS_PATH.get(force=True), settings_type, env)
    elif settings_type == 'repositories':
        path = files_dir['repositories_paths']
        file_path = os.path.join(Settings.SETTINGS_PATH.get(force=True), settings_type)
    if str(file_name).__contains__('.'):
        aux = file_name.split('.')
        file_name = aux[-1]
        count = 1
        for current_file in aux:
            files_dir = files_dir.get(current_file)
            if count < len(aux):
                path = path.get(current_file)
                file_path = os.path.join(file_path, current_file)
            count += 1

    else:
        files_dir = files_dir.get(file_name)
    keys = key.split('.')
    last_key = keys[-1]
    json_deleted = delete_key_json(files_dir, last_key, keys)

    for current_file in path:
        if str(current_file).__contains__(file_name):
            file_path = os.path.join(file_path, current_file)
            break

    files_to_edit[file_path] = json_deleted


def update_data_value(context, settings_type, file_name, key, value):
    files_dir = context.config.userdata
    files_dir = files_dir.get(settings_type)
    path = ""
    file_path = ""
    env = Settings.PYTALOS_PROFILES.get('environment')
    if settings_type == 'profiles':
        path = files_dir['profiles_paths'][env]
        file_path = os.path.join(Settings.SETTINGS_PATH.get(force=True), settings_type, env)
    elif settings_type == 'repositories':
        path = files_dir['repositories_paths']
        file_path = os.path.join(Settings.SETTINGS_PATH.get(force=True), settings_type)
    if str(file_name).__contains__('.'):
        aux = file_name.split('.')
        file_name = aux[-1]
        count = 1
        for current_file in aux:
            files_dir = files_dir.get(current_file)
            if count < len(aux):
                path = path.get(current_file)
                file_path = os.path.join(file_path, current_file)
            count += 1
    else:
        files_dir = files_dir.get(file_name)
    keys = key.split('.')
    last_key = keys[-1]
    json_updated = update_dict_value_by_key(files_dir, last_key, keys, value)

    for current_file in path:
        if str(current_file).__contains__(file_name):
            file_path = os.path.join(file_path, current_file)
            break

    files_to_edit[file_path] = deepcopy(json_updated)


def get_files_to_edit():
    return files_to_edit
