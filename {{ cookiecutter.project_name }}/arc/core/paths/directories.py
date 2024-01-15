# -*- coding: utf-8 -*-
"""
In this file you will find the necessary functions for the creation of default folders that Talos needs to work,
as well as other useful functionalities to manage the folder structure of the framework.
"""
import logging
import os
import shutil

from arc.contrib.utilities import load_modules
from arc.core.test_method.exceptions import TalosConfigurationError
from arc.settings.settings_manager import Settings
from datetime import datetime

logger = logging.getLogger(__name__)

OUTPUT_BASEDIR = Settings.OUTPUT_PATH.get()
SETTINGS_BASEDIR = Settings.SETTINGS_PATH.get(force=True)
PROJECT_BASEDIR = Settings.BASE_PATH.get(force=True)


def generate_needed_dir():
    """
    This function create all dir needed for Talos execution.
    :return:
    """
    out_dir_names = ['json', 'logs', 'reports', 'screenshots', 'videos', 'info', 'json/input', 'json/output',
                     'reports/html', 'reports/html/assets', 'reports/html/assets/imgs', 'reports/accessibility',
                     'reports/accessibility/html', 'reports/doc', 'reports/pdf']
    try:
        logger.debug("Generating default folders:")
        if Settings.PYTALOS_GENERAL.get('auto_generate_output_dir'):
            _make_directory(OUTPUT_BASEDIR)
            _make_directory(SETTINGS_BASEDIR)
            for name in out_dir_names:
                dir_path = os.path.join(OUTPUT_BASEDIR, name)
                _make_directory(dir_path)
    except (Exception,) as ex:
        logger.warning(ex)


def _make_directory(dir_path):
    if 'videos' in dir_path:
        if Settings.PYTALOS_REPORTS.get('generate_video') \
                and Settings.PYTALOS_REPORTS.get('generate_video').get('enabled'):
            os.mkdir(dir_path)
            logger.debug(f"{dir_path}")
    elif 'html' in dir_path:
        if Settings.PYTALOS_REPORTS.get('generate_html') or Settings.PYTALOS_ALM.get('attachments').get(
                'html') or Settings.PYTALOS_JIRA.get('report').get('upload_html_evidence'):
            os.mkdir(dir_path)
            logger.debug(f"{dir_path}")
    elif 'doc' in dir_path:
        if Settings.PYTALOS_REPORTS.get('generate_docx') or Settings.PYTALOS_ALM.get('attachments').get(
                'docx') or Settings.PYTALOS_JIRA.get('report').get('upload_doc_evidence'):
            os.mkdir(dir_path)
            logger.debug(f"{dir_path}")
    elif 'pdf' in dir_path:
        if Settings.PYTALOS_REPORTS.get('generate_pdf') or Settings.PYTALOS_ALM.get('attachments').get(
                'pdf') or Settings.PYTALOS_JIRA.get('report').get('upload_pdf_evidence'):
            os.mkdir(dir_path)
            logger.debug(f"{dir_path}")
    elif 'screenshots' in dir_path:
        if Settings.PYTALOS_REPORTS.get('generate_screenshot'):
            os.mkdir(dir_path)
            logger.debug(f"{dir_path}")
    elif not os.path.isdir(dir_path):
        os.mkdir(dir_path)
        logger.debug(f"{dir_path}")


def delete_old_reports():
    """
    This functions remove all files and dir in the output folder.
    :return:
    """
    logger.info(f"Removing output directory: {OUTPUT_BASEDIR}")
    shutil.rmtree(OUTPUT_BASEDIR, ignore_errors=True)


def enable_delete_old_reports(activate):
    """
    Execute delete old report function if enabled.
    :param activate:
    :return:
    """
    if activate:
        logger.debug("delete old reports enabled")
        delete_old_reports()


def save_old_reports(output_path, file_format):
    """
    This function generates a compressed (zip) file from the output folder to save the reports in a temp folder if
    this setting is enabled.
    :param output_path:
    :param file_format:
    :return:
    """
    if not output_path:
        output_path = os.path.join(PROJECT_BASEDIR, 'temp')
    if os.path.exists(output_path) is False:
        os.makedirs(output_path, exist_ok=True)
        logger.debug(f"Temp folder created: {output_path}")
    if not str(output_path).endswith(os.sep):
        output_path = f"{output_path}{os.sep}"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = os.path.join(output_path, f"output_{timestamp}")
    shutil.make_archive(file_name, file_format, OUTPUT_BASEDIR)
    logger.debug(f"Output zip created with file name: {file_name}")


def enable_save_old_reports(save_reports):
    """
    This function execute save old report function if enabled
    :param save_reports:
    :return:
    """
    if save_reports['enabled'] and os.path.exists(OUTPUT_BASEDIR):
        logger.debug("save old report enabled")
        save_old_reports(save_reports['output_path'], save_reports['format'])


def get_steps_dir(step_dir):
    """
    Load user step modules with step definitions from step dir.
    """
    step_dir = os.path.abspath(step_dir) + os.sep
    steps_dir = []
    for path, _, _ in os.walk(step_dir):
        if '__pycache__' not in path:
            steps_dir.append(path)

    return steps_dir


def import_default_steps_dir():
    """
    Load default step modules with step definitions from contrib/steps directories.
    """
    if isinstance(Settings.PYTALOS_STEPS.get(), list):
        default_steps = Settings.PYTALOS_STEPS.get()
        default_steps_paths = []
        for steps in default_steps:
            steps = steps.replace('.py', '')
            steps_dir = steps.replace('.', '/')
            steps_dir = steps_dir + '.py'
            steps_dir = os.path.abspath(steps_dir)
            default_steps_paths.append(steps_dir)
            try:
                load_modules(steps_dir)
            except (FileNotFoundError,):
                msg = f'The steps to be imported do not exist in the specified path: {steps_dir}'
                logger.error(msg)
                raise TalosConfigurationError(msg)
        return default_steps_paths
    return []


def get_default_steps_path():
    paths = os.walk(f"{Settings.BASE_PATH.get(force=True)}/arc/contrib/steps/")
    file_paths = {}
    for path in paths:
        # "walk" every folder looking for files.
        path_name = path[0]
        if len(path[2]) > 0 and "__pycache__" not in path_name:
            # If folder have files, then create the key in the files_by_path dictionary.
            for file_name in path[2]:
                if file_name not in ['__init__.py']:
                    _file_name = file_name.replace('.py', '')
                    _clean_path = path[0].split('/')[-4:]
                    _path = '.'.join(_clean_path) + '.' + _file_name
                    file_paths[_file_name] = _path
    return file_paths
