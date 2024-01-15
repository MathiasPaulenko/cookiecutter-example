# -*- coding: utf-8 -*-
"""
Talos logger configuration module.
"""
import logging.config
import os
import yaml
import shutil

from arc.settings.settings_manager import Settings

LOGGER_OUTPUT_DIR = os.path.join(Settings.OUTPUT_PATH.get(), 'logs')


def config_logger():
    """
    This function configure the logger module.
    :return:
    """
    if Settings.PYTALOS_GENERAL.get('logger').get('clear_log'):
        if os.path.isdir(os.path.join(Settings.BASE_PATH.get(force=True), LOGGER_OUTPUT_DIR)):
            shutil.rmtree(os.path.join(Settings.BASE_PATH.get(force=True), LOGGER_OUTPUT_DIR), ignore_errors=True)
    if not os.path.isdir(LOGGER_OUTPUT_DIR):
        os.makedirs(LOGGER_OUTPUT_DIR, exist_ok=True)
    config_file = get_config_dict()
    file_level = Settings.PYTALOS_GENERAL.get('logger').get('file_level')
    console_level = Settings.PYTALOS_GENERAL.get('logger').get('console_level')
    format_file = Settings.PYTALOS_GENERAL.get('logger').get('format_file')
    format_console = Settings.PYTALOS_GENERAL.get('logger').get('format_console')
    date_format = Settings.PYTALOS_GENERAL.get('logger').get('date_format')
    config_file['formatters']['fileFormatter']['format'] = format_file
    config_file['formatters']['consoleFormatter']['format'] = format_console
    config_file['formatters']['fileFormatter']['datefmt'] = date_format
    config_file['formatters']['consoleFormatter']['datefmt'] = date_format
    config_file['handlers']['fileHandler']['level'] = file_level
    config_file['handlers']['fileHandler']['filename'] = Settings.BASE_PATH.get(force=True).joinpath(
        config_file['handlers']['fileHandler']['filename']
    )
    config_file['handlers']['consoleHandler']['level'] = console_level
    if Settings.PYTALOS_GENERAL.get('logger').get('disable_console_log') is True:
        del config_file['handlers']['consoleHandler']
        del config_file['loggers']['root']['handlers'][1]
    logging.config.dictConfig(config_file)


def get_config_dict():
    """
    Return logger configuration from yaml.
    :return:
    """
    with open(f"{Settings.BASE_PATH.get(force=True)}/arc/settings/logging.yaml", 'r') as f:
        config_dict = yaml.safe_load(f)
    return config_dict
