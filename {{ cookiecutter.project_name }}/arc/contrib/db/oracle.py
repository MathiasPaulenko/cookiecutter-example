# -*- coding: utf-8 -*-
"""
Module with Oracle database control classes.
"""
import logging
import os
from pathlib import Path
import json

from arc.core.test_method.exceptions import TalosNotThirdPartyAppInstalled, TalosTestError

logger = logging.getLogger(__name__)

try:
    import cx_Oracle  # noqa
except ModuleNotFoundError:
    msg = "Please install the cx_Oracle module to use this functionality."
    logger.error(msg)
    raise TalosNotThirdPartyAppInstalled(msg)


class OracleWrapper:
    """
    The following class contains all the elements needed to manage an Oracle Data Base
    """

    def __init__(self, context, path_client_absolut, encoding="UTF-8"):
        """
        This class manager an DB Oracle
        :param context: context of Behave
        :param path_client_absolut: path of client
        :param encoding: encoding to DB Oracle
        """
        self.context = context
        self.encoding = encoding
        self.connection = None
        self.cursor = None
        self._set_platform(path_client_absolut)

    def set_connect(self, user, key, host, port: int, service_name: str):
        """
        This method enable to connect with DB Oracle
        :param user: user to connect with DB Oracle
        :param key: key to connect with DB Oracle
        :param host: ip to connect with DB Oracle
        :param port: port to connect with DB Oracle
        :param service_name: service_name to connect with DB Oracle
        """
        dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        self.connection = cx_Oracle.connect(
            user=user,
            password=key,
            dsn=dsn,
            encoding=self.encoding,
            nencoding=self.encoding
        )

        logger.info('Successful connection to Oracle DataBase:')
        logger.info(f"user: {user}")
        logger.info(f"host: {host}")
        logger.info(f"port: {port}")
        logger.info(f"encoding: {self.encoding}")
        logger.info(f"service name: {service_name}")
        logger.info(f"dsn: {dsn}")

        self.cursor = self.connection.cursor()

    @classmethod
    def _set_platform(cls, path_client_absolut):
        """
        This method set the client
        :param path_client_absolut: path client
        """
        location = Path(path_client_absolut)
        os.environ["PATH"] = str(location)
        os.environ["ORACLE_HOME"] = str(location)
        logger.debug(f'Oracle client location configured in path: {path_client_absolut}')

    def set_connect_with_profile(self, connection_data):
        """
        This method enable to connect with DB Oracle
        :param connection_data: connection_data
        :returns: jira test
        """
        self.connection = cx_Oracle.connect(connection_data, encoding=self.encoding, nencoding=self.encoding)
        self.cursor = self.connection.cursor()
        logger.info('Successful profile connection to Oracle DataBase')

    def get_cursor(self):
        """
        return connection cursor
        """
        return self.cursor

    def get_connection(self):
        """
        return current connection
        """
        return self.connection

    def close_connection(self):
        """
        This method close connect with DB Oracle
        """
        logger.info('Closing Oracle Database connection')
        self.connection.close()

    def close_cursor(self):
        """
        This method close the cursor with DB Oracle
        """
        self.cursor.close()

    def launch_query(self, query):
        """
        This method launch the query on DB Oracle
        :param query: connection_data
        """
        aux: str = str(query).lower()
        logger.info(f'Performing the query to the database: {query}')
        if "select" in aux[:aux.find(" ")]:
            self.__select_query(query)
        elif "insert" in aux[:aux.find(" ")]:
            self.__update_insert_delete_query(query)
        elif "update" in aux[:aux.find(" ")]:
            self.__update_insert_delete_query(query)
        elif "delete" in aux[:aux.find(" ")]:
            self.__update_insert_delete_query(query)
        else:
            message = f"Incorrect sql verb used in query: {query}"
            logger.error(message)
            raise TalosTestError(message)

    def __select_query(self, query):
        """
        This method launch the query when this is a select
        :param query: connection_data
        """
        self.cursor.execute(query)
        self.__parser_results()

    def __update_insert_delete_query(self, query):
        """
        This method launch the query when this is insert, update or delete
        :param query: connection_data
        """
        self.cursor.execute(query)
        self.connection.commit()

    def __parser_results(self):
        """
        This method parse the result into a list
        """
        try:
            list_result = []
            self.headers: list = [row[0] for row in self.cursor.description]
            data_fetched = self.cursor.fetchall()
            for j in range(len(data_fetched)):
                name_columns_value: dict = {}
                for x in range(len(self.headers)):
                    name_columns_value[self.headers[x]] = data_fetched[j][x]
                list_result.append(name_columns_value)
            self.results = list_result
            self.context.oracleDdQueryData = list_result
            return list_result
        except(Exception,) as ex:
            message = f"Something went wrong in the query data parser: {ex}"
            logger.error(message)
            raise TalosTestError(message)

    def get_results_on_list(self) -> list:
        """
        This method return result into list
        :returns: list of result
        """
        return self.results

    def get_results_on_json(self) -> json:
        """
        This method return result on into json
        :returns: json of result
        """
        return json.dumps(self.__parse_datetime_to_string())

    def get_results_on_dict(self) -> dict:
        """
        This method return result on into dict
        :returns: dict of result
        """
        return {"results": self.__parse_datetime_to_string()}

    def get_rowcount(self):
        """
        This method return a count of rows that affected
        :returns: rows count
        """
        return self.cursor.rowcount

    def get_command_launched(self):
        """
        This method return the last query launch
        :returns: last query
        """
        return self.cursor.statement

    def __parse_datetime_to_string(self):
        """
        This method parse the datetime on string
        :returns: datetime on string
        """
        aux_results = self.results
        for h in range(len(aux_results)):
            for x, y in aux_results[h].items():
                if str(type(aux_results[h][x])).find("datetime") > -1:
                    a = str(aux_results[h][x])
                    aux_results[h][x] = a
        return aux_results
