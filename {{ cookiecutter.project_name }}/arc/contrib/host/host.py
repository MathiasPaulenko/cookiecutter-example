# -*- coding: utf-8 -*-
"""
Module of classes and functionalities for Personal Communication or Host testing.
"""
import logging
import subprocess

from arc.core.test_method.exceptions import TalosTestError
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


class Host:
    """
    Wrapper class for automatic host actions using visual basic control.
    """

    def __init__(self, ws_path, cscript):  # noqa
        self.cscript = cscript  # noqa
        self.ws_path = ws_path
        self.vs_middleware = Settings.VS_MIDDLEWARE.get(force=True)
        self.execute = subprocess.Popen

    def open_emulator(self):
        """
        Open a host emulator window.
        :return:
        """
        logger.info('Starting host emulator')
        output, err, code = self.execute_command('open', [self.ws_path, ])
        assert code == 0, "The execution of the open script returned a return code 1."
        return output, err, code

    def close_emulator(self):
        """
        Close current host emulator window.
        :return:
        """
        logger.info('Closing host emulator')
        output, err, code = self.execute_command('close')
        assert code == 0, "The execution of the close script returned a return code 1."
        return output, err, code

    def put_value(self, row, column, value):
        """
        Put a value into a row and column location.
        :param row:
        :param column:
        :param value:
        :return:
        """
        logger.info(f"Entering the value {value} in column {column} and row {row}")
        output, err, code = self.execute_command('put', [row, column, value])
        return output, err, code

    def wait(self, row, column, length, value):
        """
        Wait for a value in a row and column with length appears.
        :param row:
        :param column:
        :param length:
        :param value:
        :return:
        """
        logger.info(f"Wait the value {value} in column {column} and row {row} and length {length}")
        output, err, code = self.execute_command('wait', [row, column, length, value])
        return output, err, code

    def send_key(self, key):
        """
        Send a simulated press key to emulator.
        :param key:
        :return:
        """
        logger.info(f'Pressing key: {key}')
        output, err, code = self.execute_command('key', [key, ])
        return output, err, code

    def get(self, row, column, length):
        """
        Return the text in row and column with length.
        :param row:
        :param column:
        :param length:
        :return:
        """
        logger.info(f'Obtaining the value in column {column}, row {row} and length {length}')
        output, err, code = self.execute_command('get', [row, column, length])
        return output, err, code

    def ftp(self, operation_type, pc_file_name, host_file_name):
        """
        Extract a file from ftp
        :param operation_type:
        :param pc_file_name:
        :param host_file_name:
        :return:
        """
        logger.info(f'Performing a {operation_type} operation file {host_file_name} from host ftp')
        output, err, code = self.execute_command('ftp', [operation_type, pc_file_name, host_file_name])
        return output, err, code

    def execute_command(self, command, vs_args=None):
        """
        Execute visual basic script command
        :param command:
        :param vs_args:
        :return:
        """
        if vs_args is None:
            vs_args = []

        logger.info(f'Executing the host script command: {command}')
        p = self.execute(
            [self.cscript, self.vs_middleware, command] + vs_args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, err = p.communicate()
        code = p.returncode

        return output, err, code

    def perform_actions(self, command, params):
        """
        Perform a action passed by parameter with the params configured.
        :param command:
        :param params:
        :return:
        """
        logger.info(f'Performing a {command} with params: {params}')
        if command == 'put':
            if len(params) == 3:
                return self.put_value(params[1], params[2], params[0])
            else:
                msg = "3 parameters expected for PUT command. " \
                      "Mandatory parameters: value, row and column. " \
                      "For example: aValue;24;2"
                logger.error(msg)
                raise TalosTestError(msg)
        elif command == 'wait':
            if len(params) == 4:
                return self.wait(params[1], params[2], params[3], params[0])

            else:
                msg = "4 parameters expected for WAIT command. " \
                      "Mandatory parameters: value, row, column and length. " \
                      "For example: aValue;23;3;6"
                logger.error(msg)
                raise TalosTestError(msg)
        elif command == 'key':
            if len(params) == 1:
                return self.send_key(params[0])

            else:
                msg = "1 parameters expected for KEY command. Mandatory parameters: key. For example: enter"
                logger.error(msg)
                raise TalosTestError(msg)
        elif command == 'get':
            if len(params) == 3:
                return self.get(params[0], params[1], params[3])
            else:
                msg = "3 parameters expected for GET command. " \
                      "Mandatory parameters: row, column and length. " \
                      "For example: 23;32;6"
                logger.error(msg)
                raise TalosTestError(msg)

        else:
            msg = "Command not allowed. Accepted commands:: put, wait, key and get"
            logger.error(msg)
            raise TalosTestError(msg)
