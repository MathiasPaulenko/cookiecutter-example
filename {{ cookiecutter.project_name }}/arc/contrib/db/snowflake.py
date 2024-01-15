# -*- coding: utf-8 -*-
"""
Module with Snowflake database control classes.
"""
import logging
import re
import json

from arc.core.test_method.exceptions import TalosNotThirdPartyAppInstalled, TalosTestError

logger = logging.getLogger(__name__)

try:
    import snowflake.connector  # noqa
except ModuleNotFoundError:
    msg = "Please install the snowflake-connector-python[pandas] module to use this functionality."
    logger.error(msg)
    raise TalosNotThirdPartyAppInstalled(msg)


class SnowflakeWrapper:
    """
    The following class contains all the elements needed to manage a Snowflake Data Base
    """

    def __init__(self, context, encoding="UTF-8"):
        """
        This class manager a Snowflake DB
        :param context: context of Behave
        :param encoding: encoding to DB Snowflake
        """
        self.context = context
        self.encoding = encoding
        self.connection = None
        self.cursor = None

    def set_connect(self, user, password, account, warehouse, database, schema):
        """
        This method enable to connect with DB Snowflake
        :param user: user to connect with DB Snowflake
        :param password: password to connect with DB Snowflake
        :param account: account to connect with DB Snowflake
        :param warehouse: warehouse to connect with DB Snowflake
        :param database: database to connect with DB Snowflake
        :param schema: schema to connect with DB Snowflake
        """
        self.connection = snowflake.connector.connect(  # noqa
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema

        )
        logger.info('Successful connection to Snowflake DataBase:')
        logger.info(f"user: {user}")
        logger.info(f"account: {account}")
        logger.info(f"warehouse: {warehouse}")
        logger.info(f"database: {database}")
        logger.info(f"schema: {schema}")
        logger.info(f"encoding: {self.encoding}")

        self.cursor = self.connection.cursor()

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
        This method close connection with DB Snowflake
        """
        logger.info('Closing Snowflake Database connection')
        self.connection.close()

    def close_cursor(self):
        """
        This method close the cursor with DB Snowflake
        """
        self.cursor.close()

    def launch_query(self, query_input):
        """
        This method launch the query on DB Snowflake
        :param query_input: connection_data
        """
        query = re.sub(' +', ' ', query_input.replace("\n", " ").replace("\t", " ").strip())
        verb = query.split(" ")[0].lower()
        logger.info(f'Performing the query to the database: {query}')
        if "select" in verb:
            self.__select_query(query)
        elif "insert" in verb:
            self.__update_insert_delete_query(query)
        elif "update" in verb:
            self.__update_insert_delete_query(query)
        elif "delete" in verb:
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
