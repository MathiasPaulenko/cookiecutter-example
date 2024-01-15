"""
Oracle DataBase Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the Word evidence.


######################################################################################################################
"""
from behave import use_step_matcher, step

from arc.contrib.db.oracle import OracleWrapper
from arc.settings.settings_manager import Settings

use_step_matcher("re")


@step(
    u"connect Oracle with user '(?P<user>.+)' key '(?P<key>.+)' host '(?P<host>.+)'"
    u" port '(?P<port>.+)' schema '(?P<schema>.+)'"
)
def connect_oracle_with_data(context, user, key, host, port, schema):
    """
    This step prepares connect to Oracle DB.
    :example
        Given connect Oracle with user 'user' key 'pass' host '107.3.57.228' port '88888' schema 'schema'
    :

    :tag Oracle DB prepares the connection:
    :param context:
    :param user:
    :param key:
    :param host:
    :param port:
    :param schema:
    """
    path_client_absolut = Settings.ORACLE.get('client_path')
    context.oracle_db = OracleWrapper(context, path_client_absolut)
    context.oracle_db.set_connect(user=user, key=key, host=host, port=int(port), service_name=schema)


@step(u"connect Oracle with data table")
def connect_oracle_with_data_table(context):
    """
    This step prepares to connect to Oracle DB.
    :example
       When connect Oracle with data table
         | user      | key  |host|port|squema|
         | user      | key  |host|port|squema|
    :
    :tag Oracle DB prepares the connection:
    :param context:
    """
    path_client_absolut = Settings.ORACLE.get('client_path')
    if context.table:
        for row in context.table:
            if context.oracle_db is None:
                context.oracle_db = OracleWrapper(context, path_client_absolut)

            context.oracle_db.set_connect(
                user=row["user"],
                key=row["key"],
                host=row["host"],
                port=row["port"],
                service_name=row["squema"]
            )


@step(u'the Oracle query is sent: "(?P<query>.+)"')
def the_oracle_query_is_sent(context, query: str):
    """
    This step the Oracle DB launches the query.
    :example

        When the Oracle query sent: "select * from  ...."
    :
    :tag Oracle DB prepare connection:
    :param context:
    :param query:
    :return context.oracleDdQueryData:
    """
    if query.lower() != "empty":
        context.oracle_db.launch_query(query)
        aux: str = str(query).lower()
        if "select" in aux[:aux.find(" ")]:
            context.func.evidences.add_json('Result Query', context.oracle_db.get_results_on_dict())

        else:
            context.func.evidences.add_text(text="Query: \n" + str(query))


@step(u'oracle last query compare "(?P<tag>.+)" with value "(?P<value>.+)" is "(?P<status>.+)"')
def oracle_last_query_compare(context, tag, value, status):
    """
    This step the Oracle DB compares the tag and value with the last query.
    :example
         And oracle last query compare "ACCOUNT_ID" with value "23223" is "visible"
         And oracle last query compare "ACCOUNT_ID" with value "23223" is "not visible"
    :
    :tag Oracle DB validate query:
    :param context:
    :param tag:
    :param value:
    :param status:
    """
    aux_status = True
    count: int = 0
    if str(status).lower().find('no') > -1:
        aux_status = False
    results = context.oracle_db.get_results_on_list()
    context.func.evidences.add_json('Result Query', results)

    if aux_status is False and len(results) == 0:
        assert True
    elif aux_status is True and len(results) == 0:
        assert False
    else:
        for x in range(len(results)):
            get_value = results[x].get(tag)
            if aux_status is True and get_value == value:
                count = count + 1
            elif aux_status is False and get_value != value:
                count = count + 1
        assert count > 0


@step(u"close Oracle connection")
def close_oracle_connection(context):
    """
    This step the Oracle DB close the connection
    :example
       And close Oracle connection
    :
    :tag closing the Oracle DB connection:
    """
    context.oracle_db.close_connection()
