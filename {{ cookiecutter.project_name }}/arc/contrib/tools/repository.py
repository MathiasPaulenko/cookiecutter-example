# -*- coding: utf-8 -*-
"""
Data and element repository class and functions module.
"""
import json
import os
import logging

from functools import reduce
from arc.contrib.tools import files
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


class Repository:
    """
    Read class of repository data files
    """

    def __init__(self):
        self.data = {}
        self.elements = {}
        self.literals = {}
        self.lang = Settings.PYTALOS_PROFILES.get('language')
        self._get_files()

    def get_texts(self, file_name, lang=Settings.PYTALOS_PROFILES.get('language')):
        """
        Return text from repository file name.
        :param file_name:
        :param lang:
        :return:
        """
        logger.debug(f"Getting texts from file name {file_name} in lang {lang}")
        if file_name in self.data:
            return self.data[file_name].get(lang, self.data[file_name])
        return None

    def _get_files(self):
        """
        Get the files inside the text_repositories folder.
        :param:
        :return:
        """
        try:
            env_dir = os.path.abspath("settings/repositories") + os.sep
            start_path = env_dir.rfind(os.sep) + 1
            list_files = []
            dict_paths = {}
            for path, dirs, filenames in os.walk(env_dir):
                folders = path[start_path:].split(os.sep)
                parent = reduce(dict.get, folders[:-1], self.data)
                parent2 = reduce(dict.get, folders[:-1], dict_paths)
                files_dict = {}
                files_path = {}
                if folders[0] != '':
                    subdir = dict.fromkeys(filenames)
                    parent[folders[-1]] = subdir
                    parent2[folders[-1]] = subdir
                for current_file in filenames:
                    list_files.append(current_file)
                    index_extension = current_file.rfind('.')
                    if os.path.isfile(os.path.join(path + os.sep + current_file)):
                        if current_file.endswith(".json"):
                            aux = json.load(
                                open(path + os.sep + current_file, encoding="utf8"))
                            files_dict[current_file[:index_extension]] = aux
                            files_path[current_file] = aux
                        elif current_file.endswith(".yaml"):
                            value = files.yaml_to_dict(path + os.sep + current_file)
                            if current_file == 'elements.yaml':
                                self.elements = value
                                files_path[current_file] = value
                            elif current_file == 'literals.yaml':
                                self.literals = value
                                files_path[current_file] = value
                            else:
                                files_dict[current_file[:index_extension]] = value
                                files_path[current_file] = value
                        else:
                            pass
                if folders[-1] != '':
                    parent[folders[-1]] = files_dict
                    parent2[folders[-1]] = files_path
                else:
                    self.data = files_dict
                    dict_paths = files_path

            self.data.setdefault('profile_paths', {})
            self.data['repositories_paths'] = dict_paths
        except FileNotFoundError:
            pass

    @staticmethod
    def format_text(element, text=None, **kwargs):
        """
        Format text from element with te text and kwargs to parsed.
        :param element:
        :param text:
        :param kwargs:
        :return:
        """
        logger.debug(f'Formatting element {element} with kwargs {kwargs}')
        if text is None:
            return element.format(**kwargs)
        return element.format(text)
