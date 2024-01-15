"""
Snowflake DataBase Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the Word evidence.


######################################################################################################################
"""
from behave import use_step_matcher, step

from arc.contrib.db.snowflake import SnowflakeWrapper
import re

use_step_matcher("re")


@step(
    u"connect Snowflake with user '(?P<user>.+)' password '(?P<password>.+)' account '(?P<account>.+)'"
    u" warehouse '(?P<warehouse>.+)' database '(?P<database>.+)' schema '(?P<schema>.+)'"
)
def connect_snowflake_with_data(context, user, password, account, warehouse, database, schema):
    """
    This step prepares connect to Snowflake DB.
    :example
        Given connect Snowflake with user 'user' password 'password' account 'account warehouse 'warehouse'
        database 'database' schema 'schema'
    :

    :tag Snowflake DB prepares the connection:
    :param context:
    :param user:
    :param password:
    :param account:
    :param warehouse:
    :param database:
    :param schema:
    """
    context.snowflake_db = SnowflakeWrapper(context)
    context.snowflake_db.set_connect(user, password, account, warehouse, database, schema)


@step(u"connect Snowflake with data table")
def connect_snowflake_with_data_table(context):
    """
    This step prepares to connect to Snowflake DB.
    :example
       When connect Snowflake with data table
         | user | password | account | warehouse | database | schema |
         | user | password | account | warehouse | database | schema |
    :
    :tag Snowflake DB prepares the connection:
    :param context:
    """
    if context.table:
        for row in context.table:
            context.snowflake_db = SnowflakeWrapper(context)
            context.snowflake_db.set_connect(
                user=row["user"],
                password=row["password"],
                account=row["account"],
                warehouse=row["warehouse"],
                database=row["database"],
                schema=row["schema"]
            )


@step(u'the Snowflake query is sent: "(?P<query>.+)"')
def the_snowflake_query_is_sent(context, query: str):
    """
    This step the Snowflake DB launches the query.
    :example

        When the Snowflake query sent: "select * from  ...."
    :
    :tag Snowflake DB prepare connection:
    :param context:
    :param query:
    :return context.SnowflakeWrapper:
    """
    if query.lower() != "empty":
        context.snowflake_db.launch_query(query)
        query_aux = re.sub(' +', ' ', query.replace("\n", " ").replace("\t", " ").strip())
        verb = query_aux.split(" ")[0].lower()
        if "select" in verb:
            context.func.evidences.add_json('Result Query', context.snowflake_db.get_results_on_dict())
        else:
            context.func.evidences.add_text(text="Query: \n" + str(query))


@step(u'Snowflake last query compare "(?P<tag>.+)" with value "(?P<value>.+)" is "(?P<status>.+)"')
def snowflake_last_query_compare(context, tag, value, status):
    """
    This step the Snowflake DB compares the tag and value with the last query.
    :example
         And snowflake last query compare "ACCOUNT_ID" with value "23223" is "visible"
         And snowflake last query compare "ACCOUNT_ID" with value "23223" is "not visible"
    :
    :tag Snowflake DB validate query:
    :param context:
    :param tag:
    :param value:
    :param status:
    """
    aux_status = True
    count: int = 0
    if str(status).lower().find('no') > -1:
        aux_status = False
    results = context.snowflake_db.get_results_on_list()
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


@step(u"close Snowflake connection")
def close_snowflake_connection(context):
    """
    This step the Snowflake DB close the connection
    :example
       And close Snowflake connection
    :
    :tag closing the Snowflake DB connection:
    """
    context.snowflake_db.close_connection()
