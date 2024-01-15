# -*- coding: utf-8 -*-
"""
File with useful environment variable configuration functions.
"""
import logging
import os

from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


def enabled_proxy(http, https):
    """
    This function set proxy configuration in environment variable for http and https url passed by parameter.
    :param http:
    :param https:
    :return:
    """
    os.environ["HTTP_PROXY"] = str(http)
    os.environ["HTTPS_PROXY"] = str(https)
    logger.info(f"Environment proxy set up with: http:{http} and https:{https}")


def disabled_environment_proxy():
    if Settings.PYTALOS_GENERAL.get('environment_proxy').get('enabled'):
        if os.environ.get('HTTP_PROXY'):
            del os.environ["HTTP_PROXY"]
        if os.environ.get('HTTPS_PROXY'):
            del os.environ["HTTPS_PROXY"]


def activate_environment_proxy():
    """
    This function call enabled_proxy function if environment proxy configuration is enabled in settings file.
    :return:
    """
    if Settings.PYTALOS_GENERAL.get('environment_proxy').get('enabled'):
        logger.info("Environment proxy is enabled.")
        http = Settings.PYTALOS_GENERAL.get('environment_proxy').get('proxy').get('http_proxy')
        https = Settings.PYTALOS_GENERAL.get('environment_proxy').get('proxy').get('https_proxy')
        enabled_proxy(http, https)
