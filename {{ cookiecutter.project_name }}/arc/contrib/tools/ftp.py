# -*- coding: utf-8 -*-
"""
Module of classes and functionalities related to FTP services.
"""
from __future__ import print_function
import datetime
import logging
from ftplib import FTP, error_perm
import os
import re
from dateutil import parser
from io import IOBase, BytesIO

from arc.core.test_method.exceptions import TalosTestError

try:
    from ftplib import FTP_TLS
except ImportError:
    FTP_TLS = None

logger = logging.getLogger(__name__)

PY2 = False
PY3 = True
file_type = IOBase
buffer_type = BytesIO
string_type = str


class dotdict(dict):  # noqa
    """
    dot.notation access to dictionary attributes
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FTPCore(object):
    """
    FTP connection core class
    """
    conn = None
    port = None
    tmp_output = None
    relative_paths = set(['.', '..'])  # noqa

    def __init__(self, host, user, password,
                 secure=False, passive=True, ftp_conn=None, **kwargs):

        if 'port' in kwargs:
            self.port = kwargs['port']
            del kwargs['port']

        if ftp_conn:
            self.conn = ftp_conn
        elif secure and FTP_TLS:
            if self.port:
                FTP_TLS.port = self.port
            self.conn = FTP_TLS(host=host, user=user, passwd=password, **kwargs)
            self.conn.prot_p()
        else:
            if self.port:
                FTP.port = self.port
            self.conn = FTP(host=host, user=user, passwd=password, **kwargs)

        if not passive:
            self.conn.set_pasv(False)

        logger.info('The connection to the FTP server was successful')

    def __getattr__(self, name):
        """
        Pass anything we don't know about, to underlying ftp connection.
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper methods.
            :param args:
            :param kwargs:
            :return:
            """
            method = getattr(self.conn, name)
            return method(*args, **kwargs)

        return wrapper

    def get(self, remote, local=None):
        """
        Gets the file from FTP server

        local can be:
            a file: opened for writing, left open
            a string: path to output file
            None: contents are returned
        """
        logger.debug('Getting files from FTP server')
        if isinstance(local, file_type):  # open file, leave open
            local_file = local
        elif local is None:
            local_file = buffer_type()
        else:  # path to file, open, write/close return None
            local_file = open(local, 'wb')

        self.conn.retrbinary("RETR %s" % remote, local_file.write)

        if isinstance(local, file_type):
            return None
        elif local is None:
            contents = local_file.getvalue()
            local_file.close()
            return contents
        else:
            local_file.close()

        logger.debug('Files get correctly')
        return None

    def put(self, local, remote, contents=None, quiet=False):
        """
        Puts a local file (or contents) on to the FTP server

        local can be:
            a string: path to inpit file
            a file: opened for reading
            None: contents are pushed
        """

        logger.debug('Putting file on the FTP server')
        remote_dir = os.path.dirname(remote)
        remote_file = os.path.basename(local) \
            if remote.endswith('/') else os.path.basename(remote)

        if contents:
            # local is ignored if contents is set
            local_file = buffer_type(contents)
        elif isinstance(local, file_type):
            local_file = local
        else:
            local_file = open(local, 'rb')

        if remote_dir:
            self.descend(remote_dir, force=True)

        size = 0
        try:
            self.conn.storbinary('STOR %s' % remote_file, local_file)
            size = self.conn.size(remote_file)
        except (Exception,) as ex:
            if not quiet:
                logger.error(ex)
                raise TalosTestError(ex)
            else:
                logger.warning(ex
                               )
        finally:
            local_file.close()
            if remote_dir:
                depth = len(remote_dir.split('/'))
                back = "/".join(['..' for _ in range(depth)])
                self.conn.cwd(back)

        logger.debug(f'Files put correctly: size: {size}')
        return size

    def upload_tree(self, src, dst, ignore=None):
        """
        Recursively upload a directory tree.
        Although similar to shutil.copytree we don't follow symlinks.
        """
        logger.debug(f'Uploading folders tree. src: {src}. dst: {dst}')
        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        try:
            dst = dst.replace('\\', '/')
            self.conn.mkd(dst)
        except error_perm:
            pass

        errors = []
        for name in names:
            if name in ignored_names:
                continue
            src_name = os.path.join(src, name)
            dst_name = os.path.join(dst, name)
            try:
                if os.path.islink(src_name):
                    pass  # noqa
                elif os.path.isdir(src_name):
                    self.upload_tree(src_name, dst_name, ignore)
                else:
                    # Will raise a SpecialFileError for unsupported file types
                    self.put(src_name, dst_name)
            except Exception as ex:
                errors.append((src_name, dst_name, str(ex)))

        logger.debug(f'Folders tree uploaded: {dst}')
        return dst

    def put_tree(self, *args, **kwargs):
        """
        Alias for upload_tree.
        """
        logger.debug('Put upload tree')
        return self.upload_tree(*args, **kwargs)

    def get_tree(self, remote, local):
        """
        Recursively download a directory tree.
        """
        logger.debug(f'Downloading directory tree: {remote} to {local}')
        remote = remote.replace('\\', '/')
        for entry in self.list(remote, extra=True):
            name = entry['name']
            remote_path = os.path.join(remote, name)
            local_path = os.path.join(local, name)
            if entry.flags == 'd':
                if not os.path.exists(local_path):
                    os.mkdir(local_path)
                self.get_tree(remote_path, local_path)
            elif entry.flags == '-':
                self.get(remote_path, local_path)

    def list(self, remote='.', extra=False, remove_relative_paths=False):
        """
        Return directory list.
        """
        if extra:
            self.tmp_output = []
            self.conn.dir(remote, self._collector)
            directory_list = split_file_info(self.tmp_output)
        else:
            directory_list = self.conn.nlst(remote)

        if remove_relative_paths:
            return list(filter(self.is_not_relative_path, directory_list))

        logger.debug(f'Directory listed: {directory_list}')
        return directory_list

    def is_not_relative_path(self, path):
        """
        Check if path is not relative path.
        :param path:
        :return:
        """
        if isinstance(path, dict):
            return path.get('name') not in self.relative_paths
        else:
            return path not in self.relative_paths

    def descend(self, remote, force=False):
        """
        Descend, possibly creating directories as needed.
        """
        remote_dirs = remote.split('/')
        for directory in remote_dirs:
            try:
                self.conn.cwd(directory)
            except (Exception,):
                if force:
                    self.conn.mkd(directory)
                    self.conn.cwd(directory)
        return self.conn.pwd()

    def delete(self, remote):
        """
        Delete a file from server.
        :param remote:
        """
        logger.debug(f'Deleting remote file: {remote}')
        try:
            self.conn.delete(remote)
        except (Exception,):
            try:
                self.conn.rmd(remote)
            except (Exception,):
                return False
        else:
            return True

    def cd(self, remote):
        """
        Change working directory on server.
        """
        logger.debug(f'Move to a remote path: {remote}')
        try:
            self.conn.cwd(remote)
        except (Exception,):
            return False
        else:
            return self.pwd()

    def pwd(self):
        """
        Return the current working directory.
        """
        current_dir = self.conn.pwd()
        logger.debug(f'Current FTP server directory: {current_dir}')
        return current_dir

    def rename(self, remote_from, remote_to):
        """
        Rename a file on the server.
        """
        logger.debug(f"Renaming file from {remote_from} to {remote_to}")
        return self.conn.rename(remote_from, remote_to)

    def mkdir(self, new_dir):
        """
        Create directory on the server.
        """
        logger.debug(f"Creating directory: {new_dir}")
        return self.conn.mkd(new_dir)

    def close(self):
        """
        End the session.
        """
        logger.debug('Closing FTP server connection')
        try:
            self.conn.quit()
        except (Exception,):
            self.conn.close()

    def _collector(self, line):
        """
        Helper for collecting output from dir().
        """
        self.tmp_output.append(line)


def _get_year(date):
    """
    Get year value from date.
    :param date:
    :return:
    """
    from dateutil.relativedelta import relativedelta

    current_date = datetime.datetime.now()
    parsed_date = parser.parse("%s" % date)
    if current_date > parsed_date:
        current = current_date
    else:
        current = current_date - relativedelta(years=1)
    return current.strftime('%Y')


def split_file_info(file_info):
    """
    Parse sane directory output usually ls -l
    """
    files = []

    unix_format = re.compile(
        r'^([\-dbclps])' +  # Directory flag [1]
        r'((?:[r-][w-][-xsStT]){3})\s+' +  # Permissions [2]
        r'(\d+)\s+' +  # Number of items [3]
        r'([a-zA-Z0-9_-]+)\s+' +  # File owner [4]
        r'([a-zA-Z0-9_-]+)\s+' +  # File group [5]
        r'(\d+)\s+' +  # File size in bytes [6]
        r'(\w{3}\s+\d{1,2})\s+' +  # 3-char month and 1/2-char day of the month [7]
        r'(\d{1,2}:\d{1,2}|\d{4})\s+' +  # Time or year (need to check conditions) [+= 7]
        r'(.+)$'  # File/directory name [8]
    )

    windows_format = re.compile(
        r'(\d{2})-(\d{2})-(\d{2})\s+' +  # month/day/2-digit year (assuming after 2000)
        r'(\d{2}):(\d{2})([AP])M\s+' +  # time
        r'(\d+)\s+' +  # file size
        r'(.+)$'  # filename
    )

    for line in file_info:
        if unix_format.match(line):
            parts = unix_format.split(line)

            date = parts[7]
            time = parts[8] if ':' in parts[8] else '00:00'
            year = parts[8] if ':' not in parts[8] else _get_year(date)
            dt_obj = parser.parse("%s %s %s" % (date, year, time))

            files.append(dotdict({
                'directory': parts[1],
                'flags': parts[1],
                'perms': parts[2],
                'items': parts[3],
                'owner': parts[4],
                'group': parts[5],
                'size': int(parts[6]),
                'date': date,
                'time': time,
                'year': year,
                'name': parts[9],
                'datetime': dt_obj
            }))

        elif windows_format.match(line):
            parts = windows_format.split(line)

            hour = int(parts[4])
            hour += 12 if parts[6] == 'P' else 0
            hour = 0 if hour == 24 else hour
            year = int(parts[3]) + 2000
            dt_obj = datetime.datetime(year, int(parts[1]), int(parts[2]), hour, int(parts[5]), 0)

            files.append(dotdict({
                'directory': None,
                'flags': None,
                'perms': None,
                'items': None,
                'owner': None,
                'group': None,
                'size': int(parts[7]),
                'date': "{}-{}-{}".format(*parts[1:4]),
                'time': "{}:{}{}".format(*parts[4:7]),
                'year': year,
                'name': parts[8],
                'datetime': dt_obj
            }))

    return files


class FtpObject:
    """
    A wrapper for FTP connections.
    """
    ftp_session = None

    def __init__(self, context):
        self.context = context

    def connect(self, host, user, password, secure=False, passive=True, ftp_conn=None):
        """
        Connect with FTP server.
        :param host:
        :param user:
        :param password:
        :param secure:
        :param passive:
        :param ftp_conn:
        :return:
        """
        self.ftp_session = FTPCore(host=host, user=user, password=password, secure=secure, passive=passive,
                                   ftp_conn=ftp_conn)

        logger.info('Connecting to FTP server with:')
        logger.info(f"host: {host}")
        logger.info(f"user: {user}")
        logger.info(f"secure: {secure}")
        logger.info(f"passive: {passive}")
        logger.info(f"ftp_conn: {host}")
        return self.ftp_session.conn

    def get_file_and_save(self, remote_file_path, local_file_path):
        """
        Get file and save.
        :param remote_file_path:
        :param local_file_path:
        :return:
        """
        logger.info(f'Get file {remote_file_path} and save in: {local_file_path}')
        return self.ftp_session.get(remote_file_path, local_file_path)

    def get_file_and_write(self, local_file_path, remote_file_path):
        """
        Get file and write.
        :param local_file_path:
        :param remote_file_path:
        :return:
        """
        logger.info(f"Get file {remote_file_path} and save in: {local_file_path}")
        temp_file = open(local_file_path, 'wb')
        return self.ftp_session.get(remote_file_path, temp_file)

    def get_content_file(self, remote_file_path):
        """
        Get file content
        :param remote_file_path:
        :return:
        """
        logger.info(f"Getting file content: {remote_file_path}")
        return self.ftp_session.get(remote_file_path)

    def put_new_remote_file(self, local_file_path, remote_file_path):
        """
        Put new file en remote FTP server.
        :param local_file_path:
        :param remote_file_path:
        :return:
        """
        logger.info(f"Put the file {local_file_path} in remote ftp sever: {remote_file_path}")
        return self.ftp_session.put(local_file_path, remote_file_path)

    def put_file_in_remote_path(self, local_file_path, remote_dir_path):
        """
        Put file in remote path.
        :param local_file_path:
        :param remote_dir_path:
        :return:
        """
        logger.info(f"Put the file {local_file_path} in remote dir: {remote_dir_path}")
        return self.ftp_session.put(local_file_path, remote_dir_path)

    def put_file_with_open_descriptor(self, local_file_path, remote_file_path):
        """
        Put file with open descriptor.
        :param local_file_path:
        :param remote_file_path:
        :return:
        """
        logger.info(f"Put the local file {local_file_path} in remote server: {remote_file_path}")
        temp_file = open(local_file_path, 'r')
        return self.ftp_session.put(temp_file, remote_file_path)

    def put_using_string_data(self, remote_file_path, content):
        """
        Put using string data.
        :param remote_file_path:
        :param content:
        :return:
        """
        logger.info(f"Putting remote file {remote_file_path} the content: {content}")
        return self.ftp_session.put(None, remote_file_path, contents=str.encode(content))

    def put_tree_on_remote_directory(self, local_path, tree):
        """
        Put tree on remote directory.
        :param local_path:
        :param tree:
        :return:
        """
        logger.info(f'Putting the local tree path {local_path} in remote server tree: {tree}')
        return self.ftp_session.upload_tree(local_path, tree)

    def get_file_list_in_directory(self, remote_path):
        """
        Get file list in directory.
        :param remote_path:
        :return:
        """
        logger.info(f"Getting file list in remote directory: {remote_path}")
        return self.ftp_session.list(remote_path)

    def get_complete_file_list_in_directory(self, remote_path):
        """
        Get complete file list in directory.
        :param remote_path:
        :return:
        """
        logger.info(f"Getting complete file list in remote path: {remote_path}")
        file_list = self.ftp_session.list(remote_path, extra=True)
        for i in range(0, len(file_list)):
            if file_list[i]["datetime"]:
                file_list[i]["datetime"] = str(file_list[i]["datetime"])
        return file_list

    def change_directory(self, remote_path):
        """
        Change FTP server directory.
        :param remote_path:
        :return:
        """
        logger.info(f'Change FTP directory: {remote_path}')
        return self.ftp_session.cd(remote_path)

    def create_directory(self, new_folder):
        """
        Create new folder in FTP server.
        :param new_folder:
        :return:
        """
        logger.info(f"Creating new remote folder {new_folder}")
        return self.ftp_session.mkdir(new_folder)

    def delete_file(self, remote_file_path):
        """
        Delete remote file
        :param remote_file_path:
        :return:
        """
        logger.info(f"Deleting remote file: {remote_file_path}")
        return self.ftp_session.delete(remote_file_path)

    def close_connection(self):
        """
        Close FTP server connection
        :return:
        """
        logger.info('Closing remote FTP server connection')
        self.ftp_session.close()

    def current_dir(self):
        """
        Retunr current dir in FTP server.
        :return:
        """
        return self.ftp_session.pwd()

    def rename_remote_file(self, remote_from, remote_to):
        """
        Rename a remote file.
        :param remote_from:
        :param remote_to:
        :return:
        """
        return self.ftp_session.rename(remote_from, remote_to)

    def get_ftp_session(self):
        return self.ftp_session
