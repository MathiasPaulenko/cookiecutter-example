# -*- coding: utf-8 -*-
"""
Module with SQLite database control classes.
"""
import logging

from colorama import Fore

from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

try:
    import sqlite3
    from sqlite3.dbapi2 import Connection
except ModuleNotFoundError as e:
    logger.warning("Can't find SQLITE module."
                   "If you are going to use Sqlite then please install the needed module.")
    print(Fore.YELLOW + "Can't find SQLITE module."
                        "If you are going to use Sqlite then please install the needed module.")


def sqlite_db():
    """
    Return a SQLite connection instance.
    :return:
    """
    if Settings.SQLITE.get('enabled'):
        logger.info('SQLite context instance is enabled')
        try:
            sqlite_home = Settings.SQLITE.get('sqlite_home')
            logger.info(f"Creating a SQLite connection from: {sqlite_home}")
            connection: Connection = sqlite3.connect(sqlite_home)
            logger.debug(f"The sqlite db was generated correctly in the path: {sqlite_home}")
            return connection
        except (Exception,) as ex:
            logger.warning(f"There was an error initializing the sqlite db instance: {ex}")
            return None
