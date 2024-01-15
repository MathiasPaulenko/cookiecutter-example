# -*- coding: utf-8 -*-
import argparse

from talos_virtual.core.environment import before_execution, after_execution
from talos_virtual.core import environment
from talos_virtual.helpers import hook
from talos_virtual.core.context import Context
from talos_virtual.core.logger.logger import Logger


class ModelRunner:
    hooks = {}

    def __init__(self, context):
        self.register_hook()
        self.context = context

    def register_hook(self):
        for func in dir(environment):
            if func in dir(hook):
                if callable(getattr(environment, func)) and not func.startswith("__"):
                    self.hooks[func] = getattr(environment, func)

    def run_hook(self, name, *args):
        if name in self.hooks:
            try:
                self.hooks[name](self.context, *args)
            except Exception as e:
                raise e

    def run_model(self):
        self.run_hook('before_all')
        self.run_hook('after_all')


def make_argv(imposter: str = None, console: bool = False):
    params = []
    if imposter:
        params.append('--imposter')
        params.append(imposter)
    if console:
        params.append('--console')
    return params


def parse_arguments(arguments):
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser('Arguments Talos Virtual')
    parser.add_argument('--imposter', action='append',
                        help='Imposter configuration. Accept JSON file and dict',
                        required=False, type=str)
    parser.add_argument('--console', help='Keeps the mountebank service opened until the user closes it manually',
                        action='store_true', required=False)
    args = parser.parse_args(args=arguments)
    return args


def main(args=None):
    logger = Logger()
    logger.config_log()
    context = Context()
    args = parse_arguments(args)
    before_execution(args, context)
    runner = ModelRunner(context)
    runner.run_model()
    after_execution(context)
