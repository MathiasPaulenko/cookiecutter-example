import configparser
import logging
from datetime import datetime
import time
import sys


class Logger(configparser.ConfigParser):

    def __init__(self):
        super().__init__()

    @staticmethod
    def config_log():
        log_path = 'output/logs/'
        log_name = 'talos_virtual_%Y-%m-%d.log'
        log_file = log_path + datetime.now().strftime(log_name)

        log_format = '%(levelname).4s %(asctime)s [%(filename)s:%(lineno)d] %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)])
        logging.Formatter.converter = time.gmtime
