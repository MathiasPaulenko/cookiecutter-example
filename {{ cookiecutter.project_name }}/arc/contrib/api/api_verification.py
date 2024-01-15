# -*- coding: utf-8 -*-
"""
Module of verifications and evidences of the api wrapper class for testing api rest services.
"""
import json
import logging
import os
from copy import deepcopy

import jsonschema

from arc.contrib.tools import files
from arc.core.test_method.exceptions import VerificationException

logger = logging.getLogger(__name__)


def _get_func_name_parsed(func_name):
    """
    Return function name parsed.
    :param func_name:
    :return:
    """
    return func_name.replace('_', ' ').capitalize()


def _get_not_equal_msg(expected_value, current_value):
    """
    Check if a expected message is not equal to current message value.
    :param expected_value:
    :param current_value:
    :return:
    """
    return f"The expected value: '{expected_value}' is not equal to the current value: '{current_value}'"


def _response_to_json(response):
    """
    Return json response converted to dict.
    :param response:
    :return:
    """
    return response.json()


class ApiVerification:
    """
    Class of api wrapper module checks
    """

    def __init__(self, context):
        self.context = context

    def evidence_or_raise(self, verification, func_name, key, expected_value, current_value, error_msg):
        """
        This function evidences in the reports a check of a verification function of a key, passing it the expected
        value and the actual value and an error message in case there is a verification error.
        :param verification:
        :param func_name:
        :param key:
        :param expected_value:
        :param current_value:
        :param error_msg:
        :return:
        """
        if verification:
            self.context.func.evidences.add_unit_table(
                title=_get_func_name_parsed(func_name),
                key=key,
                current_value=current_value,
                expected_value=expected_value,
                result=True,
            )

        else:
            logger.error(f"{_get_func_name_parsed(func_name)}: {error_msg}")
            raise VerificationException(
                context=self.context,
                title=_get_func_name_parsed(func_name),
                key=key,
                current_value=current_value,
                expected_value=expected_value,
                result=False,
                error_msg=error_msg
            )

    def verify_simple_value_in_json_response(self, key, expected_value, json_response):
        """
        Verify first level value from json response with expected value.
        :param key:
        :param expected_value:
        :param json_response:
        :return:
        """
        verification = (str(key) in json_response)
        current_value = json_response.get(key)
        verification = (expected_value == current_value) and verification
        logger.debug(f'Checking simple value in response: {current_value} = {expected_value} -> {verification}')
        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_simple_value_in_json_response.__name__,
            key=key,
            expected_value=expected_value,
            current_value=current_value,
            error_msg=_get_not_equal_msg(expected_value, current_value)
        )

    def verify_simple_value_in_xml_response(self, key, expected_value, xml_response):
        """
        Verify first level value from xml response with expected value.
        :param key:
        :param expected_value:
        :param xml_response:
        :return:
        """
        elements = xml_response.find(key)
        current_value = elements.text
        verification = (elements is not None) and (expected_value == current_value)
        logger.debug(f'Checking simple value in xml response: {current_value} = {expected_value} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_simple_value_in_xml_response.__name__,
            key=key,
            expected_value=expected_value,
            current_value=current_value,
            error_msg=_get_not_equal_msg(expected_value, current_value)
        )

    def verify_value_in_response_with_path(self, key_path, expected_value, response):
        """
        Verify value in response with key path value expected.
        :param key_path:
        :param expected_value:
        :param response:
        :return:
        """
        params_list = key_path.split('.')
        aux_json = deepcopy(_response_to_json(response))
        for param in params_list:
            if type(aux_json) is list:
                aux_json = aux_json[int(param)]
            else:
                aux_json = aux_json[param]

        current_value = os.path.expandvars(aux_json) if \
            aux_json and type(aux_json) not in [int, bool, float] else aux_json

        verification = current_value == expected_value
        logger.debug(f'Checking value in response: {current_value} = {expected_value} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_value_in_response_with_path.__name__,
            key=key_path,
            expected_value=expected_value,
            current_value=current_value,
            error_msg=_get_not_equal_msg(expected_value, current_value)
        )

    def validate_json_schema(self, expected_schema, json_response, input_type):
        """
        Validate json schema with json response.
        :param expected_schema:
        :param json_response:
        :param input_type:
        :return:
        """
        verification = True
        try:

            if input_type.lower() == "json" and json_response:
                jsonschema.validate(instance=json_response, schema=expected_schema)
            elif (input_type.lower() == "str" or input_type.lower() == "dict") and json_response:
                json_schema = json.loads(expected_schema)
                json_response_v = json.loads(json_response)
                jsonschema.validate(instance=json_response_v, schema=json_schema)
            elif input_type.lower() == "json_file" and json_response:
                json_schema = files.json_to_dict(expected_schema)
                json_response_v = files.json_to_dict(json_response)
                jsonschema.validate(instance=json_response_v, schema=json_schema)
            else:
                verification = False

        except (Exception,):
            verification = False

        logger.debug(f'Checking response schema: {verification}')

        self.context.func.evidences.add_json('Json Response', json_response)
        self.context.func.evidences.add_json('Expected Schema', expected_schema)

        self.evidence_or_raise(
            verification=verification,
            func_name=self.validate_json_schema.__name__,
            key='Json Schema',
            expected_value=expected_schema,
            current_value=json_response,
            error_msg='The given scheme does not correspond to response.'
        )

    def verify_response_headers_contains_value(self, expected_value, response):
        """
        Verify if response headers contains the expected value.
        :param expected_value:
        :param response:
        :return:
        """
        current_value = None

        for key in response.headers.keys():
            if expected_value in response.headers[key]:
                current_value = response.headers[key]
                break
            else:
                current_value = None

        verification = current_value == expected_value
        logger.debug(f'Checking response header contains: {current_value} = {expected_value} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_response_headers_contains_value.__name__,
            key='Headers',
            expected_value=expected_value,
            current_value=current_value,
            error_msg=_get_not_equal_msg(expected_value, current_value)
        )

    def verify_response_contains_value(self, expected_value, response):
        """
        Verify json response contains expected value.
        :param expected_value:
        :param response:
        :return:
        """
        verification = expected_value in response
        logger.debug(f'Checking response contains: {expected_value} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_response_contains_value.__name__,
            key='Response',
            expected_value=expected_value,
            current_value='See Request Response table',
            error_msg=f'''The value {expected_value}, is not in response'''
        )

    def verify_response_not_contains_value(self, expected_value, response):
        """
        Verify json response not contains expected value
        :param expected_value:
        :param response:
        :return:
        """
        verification = expected_value not in response
        logger.debug(f'Checking response not contains: {expected_value} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_response_not_contains_value.__name__,
            key='Response',
            expected_value=expected_value,
            current_value='See Request Response table',
            error_msg=f'''The value {expected_value}, is in response'''
        )

    def verify_response_reason(self, expected_reason, current_reason):
        """
        Verify response reason.
        :param expected_reason:
        :param current_reason:
        :return:
        """
        verification = current_reason == expected_reason
        logger.debug(f'Checking response reason: {current_reason} = {expected_reason} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_response_reason.__name__,
            key='Reason',
            expected_value=expected_reason,
            current_value=current_reason,
            error_msg=_get_not_equal_msg(expected_reason, current_reason)
        )

    def verify_response_value_type(self, key, expected_type, json_response):
        """
        Verify json response type with a expected data type.
        :param key:
        :param expected_type:
        :param json_response:
        :return:
        """
        current_type = type(json_response[key])
        verification = current_type is expected_type
        logger.debug(f'Checking response value type: {current_type} = {expected_type} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_response_value_type.__name__,
            key=key,
            expected_value=str(expected_type),
            current_value=str(current_type),
            error_msg=_get_not_equal_msg(expected_type, current_type)
        )

    def xml_verify_response_value_type(self, key, expected_type, response):
        """
        Verify xml response type with a expected data type.
        :param key:
        :param expected_type:
        :param response:
        :return:
        """
        current_value = type(response.find(key).text)
        verification = current_value is expected_type
        logger.debug(f'Checking xml response value type: {current_value} = {expected_type} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.xml_verify_response_value_type.__name__,
            key=key,
            expected_value=str(expected_type),
            current_value=str(current_value),
            error_msg=_get_not_equal_msg(expected_type, current_value)
        )

    def verify_status_code(self, expected_status, current_status):
        """
        Verify status code.
        :param expected_status:
        :param current_status:
        :return:
        """
        verification = current_status == expected_status
        logger.debug(f'Checking response status code: {current_status} = {expected_status} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_status_code.__name__,
            key='Status Code',
            expected_value=expected_status,
            current_value=current_status,
            error_msg=_get_not_equal_msg(expected_status, current_status)
        )

    def verify_value_type_in_response_with_path(self, param_path_key, expected_value, response):
        """
        Verify the type with a dot-separated value is equal to expected data type.
        :param param_path_key:
        :param expected_value:
        :param response:
        :return:
        """
        params_list = param_path_key.split('.')
        aux_json = deepcopy(_response_to_json(response))
        current_value = 'unknown'

        try:
            for param in params_list:
                if type(aux_json) is list:
                    aux_json = aux_json[int(param)]
                else:
                    aux_json = aux_json[param]
            current_value = os.path.expandvars(aux_json) \
                if aux_json and type(aux_json) not in [int, bool, float] else aux_json

            verification = type(current_value) is expected_value
            error_msg = _get_not_equal_msg(expected_value, type(current_value))
        except Exception as ex:
            verification = False
            error_msg = repr(ex)

        logger.debug(f'Checking response value type {param_path_key}: '
                     f'{current_value} = {expected_value} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_value_type_in_response_with_path.__name__,
            key=param_path_key,
            expected_value=expected_value,
            current_value=type(current_value),
            error_msg=error_msg
        )

    def xml_verify_value_type_in_response_with_path(self, param_path_key, expected_value, response):
        """
        Verify xml type from dot-separated value is equal to expected data type.
        :param param_path_key:
        :param expected_value:
        :param response:
        :return:
        """
        element = response.find(param_path_key)
        current_value = element.text
        verification = type(current_value) is expected_value
        logger.debug(f'Checking xml response value type {param_path_key}: '
                     f'{current_value} = {expected_value} -> {verification}')
        self.evidence_or_raise(
            verification=verification,
            func_name=self.xml_verify_value_type_in_response_with_path.__name__,
            key=param_path_key,
            expected_value=expected_value,
            current_value=type(current_value),
            error_msg=_get_not_equal_msg(expected_value, current_value)
        )

    def verify_response_contains_key(self, key, response):
        """
        Verify if json response contains expected key.
        :param key:
        :param response:
        :return:
        """
        keys = []
        json_dict = {}

        try:
            for key_d in response.json().keys():
                if key_d not in keys:
                    keys.append(key_d)
                    json_dict.setdefault("response_keys", []).append(key_d)

        except (Exception,):
            response_json = response.json()
            for json_values in response_json:
                for key_l in json_values.keys():
                    if key_l not in keys:
                        keys.append(key_l)
                        json_dict.setdefault("response_keys", []).append(key_l)

        verification = key in keys
        logger.debug(f'Checking response contain key: {key} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.verify_response_contains_key.__name__,
            key=key,
            expected_value=key,
            current_value=keys,
            error_msg=f"The key '{key}' is not found in the response keys: {keys}."
        )

    def xml_verify_response_contains_key(self, key, response):
        """
        Verify if xml response contains a key or tag.
        :param key:
        :param response:
        :return:
        """
        json_dict = {}

        for response_key in response.findall('*'):
            json_dict[response_key.tag] = response_key.text

        verification = len(response.findall(f'*/{key}')) > 0
        logger.debug(f'Checking xml response contain key: {key} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.xml_verify_response_contains_key.__name__,
            key=key,
            expected_value=key,
            current_value=str(json_dict),
            error_msg=f"The key '{key}' is not found in the xml response."
        )

    def status_code_is_one_of(self, expected_values, current_value):
        """
        Verify if status code is one of a list of status code.
        :param expected_values:
        :param current_value:
        :return:
        """
        verification = current_value in expected_values
        logger.debug(f'Checking response status code is one of: {current_value} in {expected_values} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.status_code_is_one_of.__name__,
            key='Status Code',
            expected_value=expected_values,
            current_value=current_value,
            error_msg=_get_not_equal_msg(str(expected_values), current_value)
        )

    def response_time_is_between(self, less_expected, greater_expected, response):
        """
        Verify if response time is between a less expected time value and greater expected time value.
        :param less_expected:
        :param greater_expected:
        :param response:
        :return:
        """
        current_value = response.elapsed.total_seconds()
        verification = (less_expected < current_value) and (current_value < greater_expected)
        expected_value = f"{less_expected} - {greater_expected}"
        logger.debug(f'Checking response time is between: '
                     f'{current_value} in {less_expected} - {greater_expected} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.response_time_is_between.__name__,
            key='Response Between Time',
            expected_value=expected_value,
            current_value=current_value,
            error_msg=f"The response time '{current_value}', is not among the values indicated: '{expected_value}'"
        )

    def response_time_is_less_than(self, seconds_expected, response):
        """
        Verify if response time is less than a expected time value.
        :param seconds_expected:
        :param response:
        :return:
        """
        current_value = response.elapsed.total_seconds()
        verification = current_value < seconds_expected
        logger.debug(f'Checking response time is less than: {current_value} < {seconds_expected} -> {verification}')
        self.evidence_or_raise(
            verification=verification,
            func_name=self.response_time_is_less_than.__name__,
            key='Response Less Time',
            expected_value=seconds_expected,
            current_value=current_value,
            error_msg=f"The response time '{current_value}', is not less than the time indicated: '{seconds_expected}'"
        )

    def response_time_is_greater_than(self, seconds_expected, response):
        """
        Verify if response time is greater than a expected time value.
        :param seconds_expected:
        :param response:
        :return:
        """
        current_value = response.elapsed.total_seconds()
        verification = current_value > seconds_expected
        logger.debug(f'Checking response time is greater than: {current_value} < {seconds_expected} -> {verification}')

        self.evidence_or_raise(
            verification=verification,
            func_name=self.response_time_is_greater_than.__name__,
            key='Response Greater Time',
            expected_value=seconds_expected,
            current_value=current_value,
            error_msg=f"The response time '{current_value}', "
                      f"is not greater than the time indicated: '{seconds_expected}'"
        )
