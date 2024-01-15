# -*- coding: utf-8 -*-
"""
Talos Framework init.
"""
import logging

from dotenv import load_dotenv  # noqa
from arc.core.logger import config_logger
from arc.contrib.utilities import get_installed_packages

__VERSION__ = "2.4.0"
config_logger()

logger = logging.getLogger(__name__)
logger.info('Starting TalosBDD execution')
logger.info(f"TalosBDD version: {__VERSION__}")
logger.debug('TalosBDD logger configured')
logger.info(f"Installed packages: {get_installed_packages()}")


load_dotenv()
