# -*- coding: utf-8 -*-
"""
SSH Generic Default Keywords
Default SSH steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the evidence files.

List of steps:
######################################################################################################################
## Generic Steps:
    establish SSH connection with username {username}, password {password}, port {port} and host {host}
    establish SSH connection with the following data table
    execute command {command} in SSH shell
    close SSH connection
    get file from server with path {remote_path} and save it in local path {local_path}
    enter into the SSH server path {remote_path}

######################################################################################################################
"""
import logging

from behave import use_step_matcher, step
from arc.contrib.services.ssh import SSHWrapper
from arc.core.test_method.exceptions import TalosTestError

logger = logging.getLogger(__name__)
use_step_matcher("re")


def evidence_output(context):
    """
    Add the shell console output of the ssh service as evidence in reports.
    :param context:
    :return:
    """
    context.runtime.ssh_output = context.ssh.get_shell_output()
    context.func.evidences.add_text("Shell Output:")
    context.func.evidences.add_text(context.ssh.format_lines(context.runtime.ssh_output))
    context.func.evidences.add_text(context.ssh.format_last_line(context.runtime.ssh_output))


def connect_ssh(context, username, password, port, host):
    """
    Connection to the ssh service via data passed in the steps.
    :param context:
    :param username:
    :param password:
    :param port:
    :param host:
    :return:
    """
    context.ssh = SSHWrapper()
    context.ssh.connect(username=str(username), password=str(password), port=int(port), host=str(host))
    context.ssh.open_shell()
    evidence_output(context)


#######################################################################################################################
#                                        Generic Steps                                                                #
#######################################################################################################################
@step(u"establish SSH connection with username '(?P<username>.+)', password '(?P<password>.+)', port '(?P<port>.+)' "
      u"and host '(?P<host>.+)'")
def connect_ssh(context, username, password, port, host):
    """
    This step establishes SSH connection with the given parameters.
    IMPORTANT: Host parameter could be the Host Address or the Hostname, both in string format.

    :example
        Given establish SSH connection with username 'user', password 'pwd', port '##' and host '###.##.##.###'
    :
    :tag SSH step:
    :param context:
    :param username:
    :param password:
    :param host:
    :param port:
    :return:
    """
    connect_ssh(context, username, password, port, host)


@step(u"establish SSH connection with the following data table")
def connecting_ssh_table(context):
    """
    This step establishes SSH connection with the parameters passed on the given data table.
    Data table needs to have the minimum access parameters: username, password, port and host.
    Host parameter could be the Host Address or the Hostname, both in string format.
    NOTE: Parameters could be entered directly or referenced from json dictionary with '${{' and '}}'.

    :example
        Given establish SSH connection with the following data table
            | param      | value                            |
            | username   | ${{datas:transfer_ssh.username}} |
            | password   | ${{datas:transfer_ssh.password}} |
            | port       | 22                               |
            | host       | ${{datas:transfer_ssh.host}}     |
    :
    :tag SSH step:
    :param context:
    :return:
    """
    username = ""
    password = ""
    port = 0
    host = ""

    if context.table:
        for row in context.table:
            param = row['param']
            value = row['value']
            if param == 'username':
                username = value
            elif param == 'password':
                password = value
            elif param == 'host':
                host = value
            elif param == 'port':
                port = value
            else:
                message = "Param " + str(param) + " is a not valid param."
                logger.error(message)
                raise TalosTestError(message)

        connect_ssh(context, username, password, port, host)

    else:
        message = "There is no table to extract data."
        logger.error(message)
        raise TalosTestError(message)


@step(u"execute command '(?P<command>.+)' in SSH shell")
def execute_command_ssh(context, command):
    """
    This step executes the given command on the previous SSH connection.
    The output of the command sending is going to be visible in the console of the execution and in the final report.

    :example
        And execute the command 'show host route' in SSH shell
    :
    :tag SSH step:
    :param context:
    :param command:
    :return:
    """
    context.ssh.send_shell(str(command))
    context.runtime.ssh_output = context.ssh.get_shell_output()
    context.func.evidences.add_text("Shell Output:")
    context.func.evidences.add_text(context.ssh.format_lines(context.runtime.ssh_output))


@step(u"close SSH connection")
def close_connection(context):
    """
    This step closes the previous SSH connection.

    :example
        And close SSH connection
    :
    :tag SSH step:
    :param context:
    :return:
    """
    context.ssh.close()
    context.func.evidences.add_text("SSH connection closed successfully.")


@step(u"enter into the SSH server path '(?P<remote_path>.+)'")
def enter_server_path(context, remote_path):
    """
    This step enters into the given remote path of the server.
    IMPORTANT: Its needs to have a previous connection to the server to work.

    :example
        And enter into the SSH server path '/home'
    :
    :tag SSH step:
    :param context:
    :param remote_path:
    :return:
    """
    context.ssh.send_shell('cd ' + str(remote_path))
    evidence_output(context)


#######################################################################################################################
#                                               File Steps                                                            #
#######################################################################################################################
@step(u"get file from server with path '(?P<remote_path>.+)' and save it in local path '(?P<local_path>.+)'")
def get_file_from_server_local(context, remote_path, local_path):
    """
    This step gets a file from the given remote path of the server and saves it in the given local path.
    IMPORTANT: remote_path parameter needs to have the exact name with the exact extension of the file to get from
    the server at the end of the path, in other case the step doesn't work correctly. The same for local_path parameter,
    it needs to have the name and extension with which you want to save it at the end of the path.
    NOTE: this step needs a previous SSH connection to work.

    :example
        And get file from server with path '/path/to/file/name_of_file.extension' and save it in local path
        'path/name_of_file.extension'
    :
    :tag SSH step:
    :param context:
    :param remote_path:
    :param local_path:
    :return:
    """
    sftp_client = context.ssh.open_sftp()
    sftp_client.get(str(remote_path), str(local_path))


@step(u"upload file from local path '(?P<local_path>.+)' to server in remote path '(?P<remote_path>.+)'")
def put_file_from_local_server(context, local_path, remote_path):
    """
    This step puts a file from the given local path to the given remote path in the server.
    IMPORTANT: this step needs a previous SSH connection to work.

    :example
        And upload file from local path 'path/name_of_file.extension' to server in remote path
            '/path/to/file/name_of_file.extension'
    :
    :tag SSH step:
    :param context:
    :param remote_path:
    :param local_path:
    :return:
    """
    sftp_client = context.ssh.open_sftp()
    sftp_client.put(str(local_path), str(remote_path))


@step(u"change permissions of file in server with path '(?P<remote_path>.+)' to '(?P<permissions_code>.+)'")
def change_permissions_server(context, remote_path, permissions_code):
    """
    This step changes permissions of the given file in server with the given permission code in octal format
    number using the 'chmod' command.
    Octal format number needs 3 digits:
        1) User(File owner).
        2) Group(File group).
        3) Others(rest of users).
    Each digit is a combination of three permissions types: read(4), write(2) and execute(1). By adding these
    numbers together, it could be possible to create the three-digit permissions code in octal format.

    :example
        And change permissions of file in server with path 'path/in/server/file.txt' to '755'
    :
    In this example the octal number 755 is used. The fist digit(7) sets the permissions for the owner,
    allowing read, write and execute access(4+2+1). The second digit(5) sets the permissions of the group,
    allowing read and execute access(4+1). The third digit(5) sets teh permissions for the other users, also
    allowing read ane execute access(4+1).

    :tag SSH step:
    :param context:
    :param remote_path:
    :param permissions_code:
    :return:
    """
    sftp_client = context.ssh.open_sftp()
    new_mode = int(str(permissions_code), 8)
    sftp_client.chmod(str(remote_path), new_mode)
