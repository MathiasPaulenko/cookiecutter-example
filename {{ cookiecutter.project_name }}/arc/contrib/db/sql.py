# -*- coding: utf-8 -*-
"""
Module with any sql database control classes.
"""
import logging

from colorama import Fore

from arc.core.test_method.exceptions import TalosNotThirdPartyAppInstalled, TalosTestError

logger = logging.getLogger(__name__)

try:
    import sqlite3
    from sqlite3.dbapi2 import Connection
except ModuleNotFoundError as e:
    msg = "Can't find SQLITE module." \
          "If you are going to use Sqlite then please install the needed module."
    logger.warning(msg)
    print(Fore.YELLOW + msg)

try:
    import psycopg2  # noqa
except ModuleNotFoundError:
    msg = "Please install the psycopg2 module to use this functionality"
    logger.error(msg)
    raise TalosNotThirdPartyAppInstalled(msg)

try:
    import mysql.connector  # noqa
    from mysql.connector import errorcode  # noqa
except ModuleNotFoundError:
    msg = "Please install the mysql-connector module to use this functionality"
    logger.error(msg)
    raise TalosNotThirdPartyAppInstalled(msg)

MYSQL = "mysql"
SQLITE = "sqlite"
POSTGRESQL = "postgresql"


class SQLWrapper:
    """
    SQL database control class.
    Currently implemented and tested with the following databases:
    - MySQL
    - SQLite
    - PostgreSQL
    """
    host = None
    user = None
    password = None
    db_name = None
    db_sql_type = None
    session = None
    connection = None
    query = None
    port = None

    def __init__(self, db_sql_type, db_name, host=None, user=None, password=None, port=None):
        """
        Create an object for SQLWrapper class
        :param db_sql_type:
        :param db_name:
        :param host:
        :param user:
        :param password:
        :param port:
        :return:
        """
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.db_sql_type = db_sql_type
        self.port = port

    def connect(self):
        """
        Establish connection to database
        :return self.session:
        """
        if self.db_sql_type == MYSQL:
            try:
                self.connection = mysql.connector.connect(
                    database=self.db_name,
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )
                self.session = self.connection.cursor(buffered=True)  # noqa
            except mysql.connector.Error as ex:
                logger.error(format(ex))
                raise TalosTestError(format(ex))
        elif self.db_sql_type == SQLITE:
            try:
                self.connection = sqlite3.connect(self.db_name)
                self.session = self.connection.cursor()
            except sqlite3.Error as ex:
                logger.error(format(ex))
                raise TalosTestError(format(ex))

        elif self.db_sql_type == POSTGRESQL:
            try:
                self.connection = psycopg2.connect(
                    host=self.host,
                    database=self.db_name,
                    user=self.user,
                    password=self.password,
                )
                self.session = self.connection.cursor()
            except psycopg2.Error as ex:
                logger.error(format(ex))
                raise TalosTestError(format(ex))

        logger.info(f'Successful connection to {self.db_sql_type} DataBase:')
        logger.info(f"user: {self.user}")
        logger.info(f"host: {self.host}")
        logger.info(f"db name: {self.db_name}")
        logger.info(f"port: {self.port}")

        return self.session

    def launch_query(self, query):
        """
        Make a query
        :param query:
        :return self.query:
        """
        logger.info(f'Performing the query to the database: {query}')
        if self.db_sql_type == MYSQL:
            try:
                query_result = self.session.execute(query)
                self.connection.commit()
                return query_result
            except mysql.connector.Error as ex:
                if ex.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    logger.error('Username and/or password entered incorrectly')
                elif ex.errno == errorcode.ER_BAD_DB_ERROR:
                    logger.error('Required database not found')
                elif ex.errno == errorcode.CR_CONN_HOST_ERROR:
                    logger.error('Wrong host required')
                elif ex.errno == errorcode.ER_IS_QUERY_INVALID_CLAUSE:
                    logger.error('Poorly formulated query')
                else:
                    logger.error(format(ex))
                    raise TalosTestError(format(ex))

            except (Exception,) as ex:
                logger.error(format(ex))
                raise TalosTestError(format(ex))

        elif self.db_sql_type == SQLITE:
            try:
                query_result = self.session.execute(query)
                self.connection.commit()
                return query_result
            except sqlite3.Error as ex:
                logger.error(format(ex))
                raise TalosTestError(format(ex))

        elif self.db_sql_type == POSTGRESQL:
            try:
                query_result = self.session.execute(query)
                self.connection.commit()
                return query_result
            except psycopg2.Error as ex:
                logger.error(format(ex))
                raise TalosTestError(format(ex))
        else:
            logger.error('Database is not implemented')
            raise TalosTestError('Database is not implemented')

        return None

    def disconnect(self):
        """
        Disconnect from database
        :param:
        :return self.connection:
        """
        logger.info('Closing Database connection')
        self.session.close()
        self.connection.close()
