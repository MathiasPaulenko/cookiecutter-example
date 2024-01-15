# -*- coding: utf-8 -*-
"""
The following class contains all the elements needed to manage SSH connection
"""
import logging
import time
from arc.core.test_method.exceptions import TalosTestError, TalosNotThirdPartyAppInstalled

logger = logging.getLogger(__name__)

try:
    import paramiko  # noqa
except ModuleNotFoundError:
    msg = "Please install the paramiko module to use this functionality."
    logger.error(msg)
    raise TalosNotThirdPartyAppInstalled(msg)


class SSHWrapper:

    def __init__(self, encoding="utf8"):
        """
        This class manages SSH connection.
        :param encoding: encoding for SSH Output
        """
        self.encoding = encoding
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.shell = None
        self.sftp_client = None
        self.last_line = ''

    def connect(self, username, password, port: int, host):
        """
        This method establishes SSH connection with the given server.
        :param username: username to connect with server.
        :param password: key to connect with server.
        :param host: IP Address or Hostname of server to connect.
        :param port: port of server to connect.
        """
        self.client.connect(
            host,
            port=port,
            username=username,
            password=password
        )
        logger.info('Successful SSH Connection:')
        logger.info(f"user: {username}")
        logger.info(f"host: {host}")
        logger.info(f"port: {port}")
        logger.info(f"encoding: {self.encoding}")

    def close(self):
        """
        This method returns an interactive shell session on the opened channel.
        If the server allows it, the channel will then be directly connected to
        the stdin, stdout, and stderr of the shell.
        """
        logger.info('Closing SSH connection')
        self.client.close()

    def open_shell(self):
        """
        This method opens an interactive shell session on the opened channel.
        If the server allows it, the channel will then be directly connected to
        the stdin, stdout, and stderr of the shell.
        """
        self.shell = self.client.invoke_shell()
        logger.info("Invoking interactive shell session on the previous opened channel")
        return self.shell

    def get_shell_output(self):
        """
        This method returns the output, in string format, of the interactive
        shell session previously invoked.
        """
        if self.shell:
            logger.info(f'Getting shell output with encoding "{self.encoding}"')
            return str(self.shell.recv(-1), self.encoding)
        else:
            message = "Shell not started"
            logger.error(message)
            raise TalosTestError(message)

    def send_shell(self, command):
        """
        This method send the given command to the interactive
        shell session previously invoked.
        :param command: Command to execute in the interactive shell.
        """
        if self.shell:
            logger.info(f'Sending command to interactive shell: {command}')
            self.shell.send(command + "\n")
            time.sleep(2)
        else:
            message = "Shell not started"
            logger.error(message)
            raise TalosTestError(message)

    @staticmethod
    def format_text(data: str):
        """
        This method formats the current output lines of the interactive
        shell session previously invoked, excluding symbols and signs
        that may not accept the generation of reports.
        :param data: Lines of the current interactive shell.
        :return: The formatted data.
        """
        data = data.replace("\x1b", "")
        data = data.replace("\x9f", "")
        data = data.replace("[37;1m", "")
        data = data.replace("[0m", "")
        data = data.replace("[01", "")
        data = data.replace(";31m", "")
        data = data.replace(";32m", "")
        return data

    def format_lines(self, data: str):
        """
        This method formats the current output of the interactive
        shell session previously invoked.
        :param data: Output Data of the current interactive shell.
        :return: The last line of the current output. Normally the default line ready to put command.
        """
        if '\n' in data:
            lines = data.splitlines()
            if self.last_line:
                logger.info("Formatting Shell Output lines:")
                logger.info(self.last_line + lines[0])
                for i in range(1, len(lines) - 1):
                    line = self.format_text(lines[i])
                    logger.info(line)
            else:
                for i in range(0, len(lines) - 1):
                    line = self.format_text(lines[i])
                    logger.info(line)
            self.last_line = lines[len(lines) - 1]
            self.last_line = self.format_text(self.last_line)
            if data.endswith('\n'):
                logger.info(self.last_line)
                self.last_line = ''
        return self.last_line

    def format_last_line(self, data: str):
        """
        This method formats the last line of output of the interactive
        shell session previously invoked.
        :param data: Output Data of the current interactive shell.
        :return: The last line of the current output. Normally the default line ready to put command.
        """
        if '\n' in data:
            lines = data.splitlines()
            self.last_line = lines[len(lines) - 1]
            self.last_line = self.format_text(self.last_line)
            logger.info("Formatting Shell Output Last Line:")
            logger.info(self.last_line)
        return self.last_line

    def result_last_line(self, data):
        """
        This method formats the current output of the interactive shell session previously invoked and
        returns the results last line of the executed command.
        :param data: Output Data of the current interactive shell.
        :return: The last line of the current command executed result. Normally the penultimate line.
        """
        lines = data.splitlines()
        result_last_line = lines[len(lines) - 2]
        result_last_line = self.format_text(result_last_line)
        return result_last_line

    def open_sftp(self):
        """
        Open an SFTP session on the SSH server.

        :return: a new `.SFTPClient` session object
        """
        return self.client.open_sftp()
