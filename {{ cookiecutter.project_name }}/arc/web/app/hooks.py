# -*- coding: utf-8 -*-
"""
TalosBDD users hooks.
In this file, the hooks are executed in sequential order according to the execution time.
The order of execution of the hooks are:
 - before execution
 - before all
 - before feature
 - before scenario
  - before_tag
 - before step
 - after step
 - after scenario
 - after feature
 - after_tag
 - after all
 - after execution
"""
import os

from arc.web.app.utils import send_request_portal


def before_execution():
    """Clean method that will be executed before execution is finished"""
    os.environ['EXECUTION_TYPE'] = 'Portal'


def after_execution():
    """Clean method that will be executed after execution is finished"""
    dict_send = {'key': 'RUNNING', 'value': 'False'}
    send_request_portal('post', 'json', dict_send, '/api/change-env')
