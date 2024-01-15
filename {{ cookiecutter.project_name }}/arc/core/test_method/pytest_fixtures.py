# -*- coding: utf-8 -*-
"""
pytest implementation and overwrite functions.
These functions are useful for running the framework without the behave context, to run test cases using Pytest.
"""
# TODO: This mode of implementation is deprecated because it is obsolete. Update or delete.
import logging
import os
import pytest

from arc.core.driver.driver_manager import DriverManager

logger = logging.getLogger(__name__)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_run_test_make_report(item):
    """
    This function implement pytest hook for pytest report generator.
    :param item:
    :return:
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.yield_fixture(scope='session', autouse=True)
def session_driver_fixture(request):
    """
    This function fix session driver with pytest.
    :param request:
    :return:
    """
    yield None
    DriverManager.close_drivers(
        scope='session',
        test_name=request.node.name,
        test_passed=request.session.testsfailed == 0
    )


@pytest.yield_fixture(scope='module', autouse=True)
def module_driver_fixture(request):
    """
    This function configure module driver fixture for pytest.
    :param request:
    :return:
    """
    previous_fails = request.session.testsfailed
    yield None
    DriverManager.close_drivers(
        scope='module',
        test_name=os.path.splitext(os.path.basename(request.node.name))[0],
        test_passed=request.session.testsfailed == previous_fails
    )


@pytest.yield_fixture(scope='function', autouse=True)
def driver_wrapper(request):
    """
    This functions run and configure driver wrapper for pytest.
    :param request:
    :return:
    """
    default_driver_wrapper = DriverManager.connect_default_driver_wrapper()
    yield default_driver_wrapper
    DriverManager.close_drivers(
        scope='function',
        test_name=request.node.name,
        test_passed=not request.node.rep_call.failed
    )
