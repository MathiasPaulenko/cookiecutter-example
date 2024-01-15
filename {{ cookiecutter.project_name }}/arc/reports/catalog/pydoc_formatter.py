# -*- coding: utf-8 -*-
"""
Module with functions to obtain comment, description and other information from gherkin files in order to format
that information.
"""
import inspect
import os
from inspect import getmembers, isfunction


def get_decorators(function):
    """
    Get decorators from function.
    :param function:
    :return:
    """
    source = inspect.getsource(function)
    list_source = source.split("\n")
    verb = list_source[0].split("(")[0]
    return verb.replace("@", "")


def get_decorate_text(function):
    """
    Get decorate text from function.
    :param function:
    :return:
    """
    source = inspect.getsource(function)
    verb = get_decorators(function)
    behave_step = source.split("\n")[0].split(verb)[1].replace('(u"', "").replace('")', "")
    behave_step = behave_step.replace("'(?P<", "{").replace(">.+)'", "}")
    return behave_step


def get_params_doc(doc):
    """
    Get params information from document.
    :param doc:
    :return:
    """
    doc_split = str(doc).split(":")
    params = []
    for param in doc_split:
        if str(param).strip().startswith("param"):
            params.append(param)
    return params


def get_formatter_doc(doc):
    """
    Get formatter document.
    :param doc:
    :return:
    """
    doc = str(doc).replace(":", "@@")
    doc_split = str(doc).split("@@")
    py_doc = str(doc_split[0]).split("\n")
    values = []
    for d in py_doc:
        if d.strip() != "":
            values.append(d.strip())
    return values


def get_example_doc(doc):
    """
    Get example from docstring from function.
    :param doc:
    :return:
    """
    doc_split = str(doc).split(":")
    example = None
    for value in doc_split:
        if str(value).startswith("example") or str(value).startswith("examples"):
            example = value.replace("example", "").replace("examples", "")

    return example


def get_types_doc(doc):
    """
    Get type from docstring from function.
    :param doc:
    :return:
    """
    doc_split = str(doc).split(":")
    tag = None
    for value in doc_split:
        if str(value).startswith("tag") or str(value).startswith("type"):
            tag = value.replace("tag", "").replace("type", "")
    return tag


def get_pydoc_info(function):
    """
    Get information of docstring from function.
    :param function:
    :return:
    """
    _list = getmembers(function, isfunction)
    function_name = str(function.__file__).split("\\")[-1].replace("_", " ").replace(".py", "").title()
    project_name = \
        str(os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir) + '/../../../')).split(os.sep)[-1]
    function_path = str(function.__file__).split(os.sep + project_name + os.sep)[-1].replace(os.sep, ".")
    list_excel_data = []
    for a in _list:
        excel_data = {}
        if a[0] == 'use_step_matcher':
            continue
        elif a[0] == 'given' or a[0] == 'step' or a[0] == 'and' or a[0] == 'when' or a[0] == 'then':
            continue
        else:
            excel_data["Function Name"] = function_name
            excel_data["Function Path"] = function_path
            excel_data["Verb Step"] = get_decorators(a[1]).upper()
            excel_data["Step"] = get_decorate_text(a[1])
            excel_data["Py Doc"] = get_formatter_doc(a[1].__doc__)
            excel_data["Example"] = get_example_doc(a[1].__doc__)
            excel_data["Params"] = get_params_doc(a[1].__doc__)
            excel_data["Tags"] = get_types_doc(a[1].__doc__)

            list_excel_data.append(excel_data)

    return list_excel_data
