"""
Host Default Keywords

List of steps:
######################################################################################################################

"""
import time

from behave import use_step_matcher, step

use_step_matcher("re")

EVIDENCE_TITLE = 'Returned Values'


#######################################################################################################################
#                                                  Functional Steps                                                    #
#######################################################################################################################
@step(u"open host emulator")
def open_host_emulator(context):
    """
    TODO: description
    :example
        Given open host emulator
    :
    :tag Host step:
    :param context:
    :return:
    """
    output, err, code = context.host.open_emulator()
    context.host.response = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }

    assert b'Ok' in output


@step(u"wait for value '(?P<value>.+)' in row '(?P<row>.+)', column '(?P<column>.+)' and length '(?P<length>.+)'")
def wait_for_value_in_row_column_and_length(context, value, row, column, length):
    """
    TODO: description
    :example
        Given wait for value 'Text' in row '23', column '2' and length '6'
    :
    :tag Host step:
    :param context:
    :param value:
    :param row:
    :param column:
    :param length:
    :return:
    """
    output, err, code = context.host.wait(row, column, length, value)
    context.host.response = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    assert b'Ok' in output


@step(u"put the value '(?P<value>.+)' in row '(?P<row>.+)' and column '(?P<column>.+)' in emulator")
def put_the_value_in_row_and_column_in_emulator(context, value, row, column):
    """
    TODO: description
    :example
        Given put the value 'Value' in row '24' and column '2' in emulator
    :
    :tag Host step:
    :param context:
    :param value:
    :param row:
    :param column:
    :return:
    """
    output, err, code = context.host.put_value(row, column, value)
    context.host.response = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    assert b'Ok' in output


@step(u"put multiple values in emulator")
def put_multiple_value_emulator(context):
    """
    TODO: description
    :example
        Given put multiple values in emulator
          | value | row | column | interval |
          | S     | 24  | 2      | 0.5      |
          | A     | 24  | 2      | 2        |
          | B     | 24  | 2      | 1        |
    :
    :tag Host step:
    :param context:
    :return:
    """
    context.host.response = {}
    evidence = []
    if context.table:
        for index, row_table in enumerate(context.table):
            value = row_table["value"]
            row = row_table["row"]
            column = row_table["column"]
            output, err, code = context.host.put_value(row, column, value)

            context.host.response[index] = {
                'output': str(output),
                'err': str(err),
                'code': str(code)
            }

            try:
                interval = float(row_table["interval"])
                time.sleep(interval)

            except (Exception,):
                time.sleep(1)

    for key, value in context.host.response.items():
        assert 'Ok' in value['output']


@step(u"press '(?P<key>.+)' key in emulator")
def press_key_emulator(context, key):
    """
    TODO: description
    :example
        Given press 'enter' key in emulator

    :
    :tag Host step:
    :param context:
    :param key:
    :return:
    """
    output, err, code = context.host.send_key(key)
    context.host.response = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    assert b'Ok' in output


@step(u"press multiple keys in emulator")
def press_multiple_keys_emulator(context):
    """
    TODO: description
    :example
        Given press multiple keys in emulator
          | key   | interval |
          | enter | 0.5      |
          | tab   | 2        |
          | enter | 1        |

    :
    :tag Host step:
    :param context:
    :return:
    """
    context.host.response = {}
    if context.table:
        for index, row_table in enumerate(context.table):
            key = row_table["key"]
            output, err, code = context.host.send_key(key)

            context.host.response[index] = {
                'output': str(output),
                'err': str(err),
                'code': str(code)
            }
            try:
                interval = float(row_table["interval"])
                time.sleep(interval)

            except (Exception,):
                time.sleep(1)

    for key, value in context.host.response.items():
        assert 'Ok' in value['output']


@step(u"get with row '(?P<row>.+)', column '(?P<column>.+)' and length '(?P<length>.+)' in emulator")
def get_with_row_column_and_length_in_emulator(context, row, column, length):
    """
    TODO: description
    :example
        Given get with row '14', column '24' and length '8' in emulator

    :
    :tag Host step:
    :param context:
    :param row:
    :param column:
    :param length:
    :return:
    """
    output, err, code = context.host.get(row, column, length)
    context.host.get_value = output
    context.host.response = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    assert b'Ok' in output


@step(u"put in ftp '(?P<local_file>.+)' to '(?P<ftp_file>.+)' with emulator")
def put_in_ftp_to_with_emulator(context, local_file, ftp_file):
    """
    TODO: description
    :example
        TODO: example

    :
    :param context:
    :param local_file:
    :param ftp_file:
    :return:
    """
    output, err, code = context.host.ftp('put', local_file, ftp_file)
    context.host.response = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    assert b'Ok' in output


@step(u"get from ftp '(?P<ftp_file>.+)' to '(?P<local_file>.+)' with emulator")
def get_from_ftp_to_with_emulator(context, ftp_file, local_file):
    """
    TODO: description
    :example
        TODO: example

    :
    :param context:
    :param ftp_file:
    :param local_file:
    :return:
    """
    output, err, code = context.host.ftp('get', local_file, ftp_file)
    context.host.response = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    assert b'Ok' in output


@step(u"perform the following actions in the emulator")
def perform_the_following_actions_in_the_emulator(context):
    """
    TODO: description
    :example
         Given perform the following actions in the emulator
              | command | params        |
              | wait    | Username;23;2;6 |
              | put     | S;24;2        |
              | key     | enter         |

    :
    :tag Host step:
    :param context:
    :return:
    """
    context.host.get_value = []
    context.host.response = {}
    if context.table:
        for index, row_table in enumerate(context.table):
            command = row_table['command']
            params = row_table['params']

            params_list = str(params).split(';')

            output, err, code = context.host.perform_actions(command, params_list)
            context.host.response[index] = {
                'output': str(output),
                'err': str(err),
                'code': str(code)
            }
            context.func.evidences.add_screenshot(capture_name=index)
            if command == 'get':
                context.host.get_value.append(output)

            try:
                interval = float(row_table["interval"])
                time.sleep(interval)

            except (Exception,):
                time.sleep(1)

    for key, value in context.host.response.items():
        assert 'Ok' in value['output']
