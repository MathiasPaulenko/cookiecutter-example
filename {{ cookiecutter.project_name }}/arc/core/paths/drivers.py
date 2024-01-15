# -*- coding: utf-8 -*-
"""
Useful functions for driver directory configuration.
"""
import logging
import os

from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

DRIVERS_HOME = Settings.DRIVERS_HOME.get(force=True)


def add_drivers_directory_to_path(path=DRIVERS_HOME):
    """
    This function add to path the drivers directory.
    :param path:
    :return:
    """
    logger.debug(f"Adding driver directory to the system environment path: {path}")
    os.environ["PATH"] = path + ';' + os.environ["PATH"]
    logger.debug(f'System environment paths: {os.environ["PATH"]}')
