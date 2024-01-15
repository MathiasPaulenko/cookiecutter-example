# -*- coding: utf-8 -*-
"""
File containing the CommonObject class used in the PageElement as parent.
"""
import logging

logger = logging.getLogger(__name__)


class CommonObject(object):
    """
    CommonObject class instance.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver_wrapper = None

    def reset_object(self):
        """
        Reset object
        :return:
        """
        pass

    @property
    def driver(self):
        """
        Return driver configured.
        :return:
        """
        return self.driver_wrapper.driver

    @property
    def config(self):
        """
        Return configuration instance.
        :return:
        """
        return self.driver_wrapper.config

    @property
    def utils(self):
        """
        Return utilities instance
        :return:
        """
        return self.driver_wrapper.utils
