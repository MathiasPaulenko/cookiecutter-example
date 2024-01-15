# -*- coding: utf-8 -*-
"""
Module for obtaining data on the user's steps.
"""
import importlib
import os
from importlib import util

from arc.reports.catalog.pydoc_formatter import get_pydoc_info
from arc.settings.settings_manager import Settings

STEPS_PATH = TEST_PATH = os.path.join(Settings.BASE_PATH.get(force=True), f'test{os.sep}steps')


def get_user_step_imports():
    """
    Get user step imported.
    :return:
    """
    imports = []
    for root, dirs, files in os.walk(STEPS_PATH):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                spec = importlib.util.spec_from_file_location("*", file_path)
                modules = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modules)
                imports.append(modules)
    return imports


def get_list_user_steps():
    """
    Get list of user steps.
    :return:
    """
    imports = get_user_step_imports()
    data_list = []
    for imp in imports:
        data_list.append(get_pydoc_info(imp))
    return data_list
