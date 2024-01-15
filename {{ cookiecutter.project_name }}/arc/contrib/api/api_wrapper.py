# -*- coding: utf-8 -*-
"""
Request wrapper module for automatic testing of api rest services and verification functionalities of such tests.
"""
import ast
import json
import logging
import socket
import xml.etree.ElementTree as Et
from copy import deepcopy
from io import StringIO
from urllib.parse import urlparse
import requests
from PIL import Image
from oauthlib.oauth2 import MobileApplicationClient, LegacyApplicationClient, BackendApplicationClient
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests.cookies import cookiejar_from_dict, RequestsCookieJar, create_cookie
from requests.utils import get_encodings_from_content, get_encoding_from_headers, get_unicode_from_response
from requests_oauthlib import OAuth1, OAuth2Session
from urllib3.connection import HTTPConnection

from arc.contrib.api.api_verification import ApiVerification
from arc.core.test_method.exceptions import TalosTestError
from arc.reports.evidence import get_json_formatted
from arc.settings.settings_manager import Settings
from shlex import quote

logger = logging.getLogger(__name__)

METHOD_GET = "GET"
METHOD_POST = "POST"
METHOD_PUT = "PUT"
METHOD_PATCH = "PATCH"
METHOD_DELETE = "DELETE"
METHOD_COPY = "COPY"
METHOD_HEAD = "HEAD"
METHOD_OPTIONS = "OPTIONS"
METHOD_LINK = "LINK"
METHOD_UNLINK = "UNLINK"
METHOD_PURGE = "PURGE"
METHOD_LOCK = "LOCK"
METHOD_UNLOCK = "UNLOCK"
METHOD_PROPFIND = "PROPFIND"
METHOD_VIEW = "VIEW"


class ApiObject:
    """
    Instance class of api rest service request execution engine, response parsing and verification.
    """
    headers = None
    body = None
    method = None
    uri = None
    params = None
    authorization = None
    files = None
    ssl = False
    cookies = None
    cert = None
    data = None
    context = None
    response = None
    session = None
    prepare = None
    request = None
    proxies = None
    HTTPConnection.debuglevel = 0
    requests_log = None
    remote_ip = None

    def __init__(self, context):
        self.context = context
        self.verification = ApiVerification(context)

    def prepare_request(self, header=None, body=None, method=None, uri=None, params=None, authorization=None,
                        ssl=False, cookies=None, data=None, files=None, proxies=None, cert=None):
        """
        Prepare all information in order to execute the api rest request.
        :param header:
        :param body:
        :param method:
        :param uri:
        :param params:
        :param authorization:
        :param ssl:
        :param cookies:
        :param data:
        :param files:
        :param proxies:
        :param cert:
        :return:
        """
        if header is not None: self.headers = header  # noqa
        if body is not None: self.body = body  # noqa
        if method is not None: self.method = method  # noqa
        if uri is not None: self.uri = uri  # noqa
        if files is not None: self.files = files  # noqa
        if params is not None: self.params = params  # noqa
        if authorization is not None: self.authorization = authorization  # noqa
        if ssl is not None: self.ssl = ssl  # noqa
        if cookies is not None: self.cookies = cookies  # noqa
        if cert is not None: self.cert = cert

        try:
            # Sometimes there are weird symbols that ast can't parse so then, just prepare the data.
            if data is not None:
                self.data = ast.literal_eval(data)
        except (ValueError, SyntaxError):
            if data is not None:
                self.data = data

        if type(self.data) is bytes:
            self.data = json.loads(self.data.decode())

        default_proxy = {}
        try:
            if Settings.PYTALOS_RUN.get('execution_proxy').get('enabled'):
                default_proxy['http'] = Settings.PYTALOS_RUN.get('execution_proxy').get('proxy').get('http_proxy')
                default_proxy['https'] = Settings.PYTALOS_RUN.get('execution_proxy').get('proxy').get('https_proxy')
                self.proxies = default_proxy
            else:
                self.proxies = default_proxy

        except(Exception,) as ex:
            logger.warning(ex)
            self.proxies = proxies

    def send_request(self):
        """
        Send request with configuration prepared before.
        :return:
        """
        logger.info(f"Sending api rest request with:")
        logger.info(f"method: {self.method}")
        logger.info(f"url: {self.uri}")
        logger.info(f"headers: {self.headers}")
        logger.info(f"json: {self.body}")
        logger.info(f"params: {self.params}")
        logger.info(f"auth: {self.authorization}")
        logger.info(f"cookies: {self.cookies}")
        logger.info(f"data: {self.data}")
        logger.info(f"files: {self.files}")

        self.request = requests.Request(method=self.method, url=self.uri, headers=self.headers, json=self.body,
                                        params=self.params, auth=self.authorization, cookies=self.cookies,
                                        data=self.data, files=self.files)

        self.prepare = self.request.prepare()
        self.session = requests.Session()

        if self.proxies is not None: self.session.proxies.update(self.proxies)  # noqa

        self.response = self.session.send(self.prepare, verify=self.ssl, cert=self.cert)

        if self.response is None:
            msg = 'The response is None: ERROR: Check that the call was made correctly, ' \
                  'this error usually occurs when the uri is badly formed'
            logger.error(msg)
            raise TalosTestError(msg)
        else:
            self.context.api.response = self.response
            try:
                if 'application/json' in self.context.api.response.headers.get('Content-Type', '') \
                        or 'urlencoded' in self.context.api.response.headers.get('Content-Type', ''):
                    self.context.api.json_response = self.response.json() \
                        if self.context.api.response.content != b'' else ''
                elif self.context.api.response.headers.get('Content-Type', '') == 'text/xml':
                    self.context.api.xml_response = Et.fromstring(self.response.text)
                else:
                    self.context.api.json_response = self.response.text
            except TypeError:
                self.context.api.json_response = self.response.text

        data_dict = {
            "URL": self.uri,
            "Method": self.method,
            "response": self.response,
            "response_headers": self.response.headers,
            "headers": self.headers,
            "body": self.body if self.data is None else self.data,
            "params": self.params
        }
        self.set_api_info(data_dict)
        logger.info(f"The request to {self.uri} received the correct response")
        logger.info(f"Response headers: {self.response.headers}")
        return self.response

    def create_basic_authorization(self, username, password, auth_type="basic"):
        """
        Create a basic authorization instance from username and password.
        :param username:
        :param password:
        :param auth_type:
        :return:
        """
        logger.debug(f'Creating a api rest basic authorization with: username {username} and type {auth_type}')
        if auth_type.lower() == "basic":
            auth = HTTPBasicAuth(username, password)
        elif auth_type.lower() == "digest":
            auth = HTTPDigestAuth(username, password)
        else:
            msg = f"{auth_type} does not exist: try basic or digest"
            logger.error(msg)
            raise TalosTestError(msg)

        self.context.api.api_auth = auth
        return auth

    def create_oauth1(self, app_key, app_secret, user_oauth_token, user_oauth_token_secret):
        """
        Create a instance of OAuth1.
        :param app_key:
        :param app_secret:
        :param user_oauth_token:
        :param user_oauth_token_secret:
        :return:
        """
        logger.debug(f"Creating a OAuth1 authentication")
        auth = OAuth1(app_key, app_secret, user_oauth_token, user_oauth_token_secret)
        self.context.api.auth = auth
        return auth

    def create_oauth2(self, flow=None, client_id=None, client_secret=None, url=None, scope=None):
        """
        Create a instance of OAuth2 depending of flow.
        :param flow:
        :param client_id:
        :param client_secret:
        :param url:
        :param scope:
        :return:
        """
        logger.debug(f"Creating a OAuth2 authentication for {flow}")
        if flow == "web" and client_id and client_secret and url and scope:
            oauth = OAuth2Session(client_id, redirect_uri=url, scope=scope)
        elif flow == "mobile" and client_id and url and scope:
            oauth = OAuth2Session(client=MobileApplicationClient(client_id=client_id), scope=scope)
        elif flow == "legacy" and client_id:
            oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
        elif flow == "backend" and client_id:
            client = BackendApplicationClient(client_id=client_id)
            oauth = OAuth2Session(client=client)
        else:
            msg = f"the flow {flow} parameter must be filled with some of the following values: " \
                  f"web, mobile, legacy or backend"
            logger.error(msg)
            raise TalosTestError(msg)

        self.context.api.auth = oauth
        return oauth

    @staticmethod
    def formatter_table_to_dict(table, key="key", value="value"):
        """
        Return a dict parsed from list.
        :param table:
        :param key:
        :param value:
        :return:
        """
        params = {}
        if table:
            for row in table:
                params[row[key]] = row[value]
        return params

    @staticmethod
    def decompose_url(url):
        """
        Return list of url information decomposed.
        List will have url protocol, url hostname, url path and url queries.
        :param url:
        :return:
        """
        parsed = urlparse(url)
        url_protocol = parsed.scheme
        url_hostname = parsed.hostname
        url_path = []
        url_query = {}
        if parsed.path:
            path = parsed.path.split('/')
            path.pop(0)
            url_path = path
        if parsed.query:
            query = parsed.query.split('&')
            for p in query:
                d = p.split('=')  # noqa
                url_query[d[0]] = d[1]
        decompose_url = [url_protocol, url_hostname, url_path, url_query]
        logger.debug(f'Decompose url: {decompose_url}')
        return decompose_url

    @staticmethod
    def compose_url_with_params(url, dict_params: dict):
        """
        Return a valid url with param passed by parameter.
        :param url:
        :param dict_params:
        :return:
        """
        url += "?"
        len_dict = len(dict_params)
        cont = 1
        for param in dict_params:
            if cont == len_dict:
                url += param.key + "=" + param.value
            else:
                url += param.key + "=" + param.value + "&"
            cont += 1
        logger.debug(f'Compose url from url and params: {url}')
        return url

    @staticmethod
    def response_to_json(response):
        """
        Return json from response.
        :param response:
        :return:
        """
        return response.json()

    def send_simple_request(self, uri, method: str, params=None, headers: dict = None, data: dict = None,
                            allow_redirects: bool = None, timeout=None, files=None):
        """
        Send a simple request from data passed by parameter.
        :param uri:
        :param method:
        :param params:
        :param headers:
        :param data:
        :param allow_redirects:
        :param timeout:
        :param files:
        :return:
        """
        self.headers = headers
        self.body = data
        self.method = method
        self.uri = uri
        self.params = params

        if data is None:
            data = {}

        logger.info(f"Sending simple api rest request with:")
        logger.info(f"method: {method.lower()}")
        logger.info(f"url: {uri}")
        logger.info(f"headers: {headers}")
        logger.info(f"data: {data}")
        logger.info(f"allow_redirects: {allow_redirects}")
        logger.info(f"timeout: {timeout}")
        logger.info(f"files: {files}")

        if method.lower() == "post":
            response = requests.post(uri, params=params, headers=headers, data=json.dumps(data),
                                     allow_redirects=allow_redirects, timeout=timeout, files=files)
        elif method.lower() == "get":
            response = requests.get(uri, params=params, headers=headers, data=json.dumps(data),
                                    allow_redirects=allow_redirects, timeout=timeout)
        elif method.lower() == "put":
            response = requests.put(uri, params=params, headers=headers, data=json.dumps(data),
                                    allow_redirects=allow_redirects, timeout=timeout)
        elif method.lower() == "delete":
            response = requests.delete(uri, params=params, headers=headers, data=json.dumps(data),
                                       allow_redirects=allow_redirects, timeout=timeout)
        elif method.lower() == "head":
            response = requests.head(uri, params=params, headers=headers, data=json.dumps(data),
                                     allow_redirects=allow_redirects, timeout=timeout)
        elif method.lower() == "options":
            response = requests.options(uri, params=params, headers=headers, data=json.dumps(data),
                                        allow_redirects=allow_redirects, timeout=timeout)
        else:
            msg = f"Method {method} not implemented or does not exist"
            logger.error(msg)
            raise TalosTestError(msg)

        self.response = response

        data_dict = {
            "URL": self.uri,
            "Method": self.method,
            "response": self.response,
            "response_headers": self.response.headers,
            "params": self.params,
            "headers": self.headers,
            "body": self.body,
        }
        self.set_api_info(data_dict)
        logger.info(f"The request to {uri} received the correct response")
        self.session.close()
        return response

    def get_response_text(self):
        """
        Get text from response.
        :return:
        """
        logger.debug('Obtaining raw response text')
        return self.response.text

    def get_response_encoding(self):
        """
        Get response encoding
        :return:
        """
        encoding = self.response.encoding
        logger.debug(f'Obtaining response encoding {encoding}')
        return encoding

    def get_response_binary(self):
        """
        Get response binaries.
        :return:
        """
        logger.debug('Getting response binaries')
        return self.response.content

    def create_image_binary_response(self):
        """
        Create binary image from response.
        :return:
        """
        logger.debug("Creating binary image from response")
        return Image.open(str(StringIO(str(self.response.content))))

    def get_response_json(self):
        """
        Get json from response.
        :return:
        """
        return self.response.json()

    def get_response_raw(self):
        """
        Get raw response.
        :return:
        """
        return self.response.raw

    def get_remote_ip(self):
        """
        Return remote ip address if this is reachable.
        :return:
        """
        try:
            url = self.decompose_url(self.uri)
            if str(url).startswith("www."):
                self.remote_ip = socket.gethostbyname(url[1])
            else:
                self.remote_ip = socket.gethostbyname("www." + url[1])

            logger.debug(f'Remote ip address: {self.remote_ip}')
            return self.remote_ip
        except socket.error:
            logger.debug(f'Remote ip address is unknown or unreachable')
            return "Unknown or unreachable"

    def save_response_into_file(self, file_path, chuck_size=8192):
        """
        Save response into file.
        :param file_path:
        :param chuck_size:
        :return:
        """
        logger.debug(f"Saving request response in: {file_path}")
        with open(file_path, 'wb') as fd:
            for chunk in self.response.iter_content(chunk_size=chuck_size):
                fd.write(chunk)

    def get_response_history(self):
        """
        Return response history.
        :return:
        """
        history = self.response.history
        logger.debug(f'Obtaining response history: {history}')
        return self.response.history

    def get_response_headers(self):
        """
        Return headers from response.
        :return:
        """
        headers = self.response.headers
        logger.debug(f'Obtaining response headers: {headers}')
        return self.response.headers

    @staticmethod
    def get_encodings_from_content(content):
        """
        Return encodings from response content.
        :param content:
        :return:
        """
        return get_encodings_from_content(content)

    @staticmethod
    def get_encoding_from_headers(headers):
        """
        Return encoding from headers.
        :param headers:
        :return:
        """
        return get_encoding_from_headers(headers)

    def get_unicode_from_response(self):
        """
        Get unicode from response.
        :return:
        """
        return get_unicode_from_response(self.response)

    @staticmethod
    def dict_from_cookiejar(cookie_jar):
        """
        Return a dict of cookies from cookie jar.
        :param cookie_jar:
        :return:
        """
        cookie_dict = {}
        for cookie in cookie_jar:
            cookie_dict[cookie.name] = cookie.value
        logger.debug(f'Obtaining cookies from response: {cookie_dict}')
        return cookie_dict

    @staticmethod
    def add_dict_to_cookiejar(cookie_jar, cookie_dict):
        """
        Add new cookie to cookie jar.
        :param cookie_jar:
        :param cookie_dict:
        :return:
        """
        return cookiejar_from_dict(cookie_dict, cookie_jar)

    @staticmethod
    def cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True):
        """
        Return cookie jar from dict.
        :param cookie_dict:
        :param cookiejar:
        :param overwrite:
        :return:
        """
        if cookiejar is None:
            cookiejar = RequestsCookieJar()

        if cookie_dict is not None:
            names_from_jar = [cookie.name for cookie in cookiejar]
            for name in cookie_dict:
                if overwrite or (name not in names_from_jar):
                    cookiejar.set_cookie(create_cookie(name, cookie_dict[name]))

        return cookiejar

    def get_log(self):
        """
        Return requests log.
        :return:
        """
        return self.requests_log

    def _get_response_if_none(self, response):
        """
        Get response from class if response passed by parameter is none.
        :param response:
        :return:
        """
        if response is None:
            response = self.response
        return response

    # verifications methods
    def verify_simple_value_in_response(self, key, value_expected, response=None):
        """
        Verify simple value in response.
        :param key:
        :param value_expected:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        json_response = self.response_to_json(response)

        self.verification.verify_simple_value_in_json_response(key, value_expected, json_response)

    def xml_verify_simple_value_in_response(self, key, value_expected, response=None):
        """
        Verify simple value from xml response.
        :param key:
        :param value_expected:
        :param response:
        :return:
        """
        if response is None:
            response = self.context.api.xml_response

        self.verification.verify_simple_value_in_xml_response(key, value_expected, response)

    def verify_value_in_response_with_path(self, key_path: str, expected_value, response=None):
        """
        Verify value in response with key path.
        :param key_path:
        :param expected_value:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.verify_value_in_response_with_path(key_path, expected_value, response)

    def validate_json_schema(self, expected_schema, json_response=None, input_type="json"):
        """
        Validate json schema from expected schema.
        :param expected_schema:
        :param json_response:
        :param input_type:
        :return:
        """
        if json_response is None:
            json_response = self.response.json()

        self.verification.validate_json_schema(expected_schema, json_response, input_type)

    def verify_status_code(self, expected_status, response=None):
        """
        Verify status code from response.
        :param expected_status:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.verify_status_code(expected_status, response.status_code)

    # TODO: check this method.
    def verify_response_contains_value(self, value, response=None):
        """
        Verify if response contain a expected value.
        :param value:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.verify_response_contains_value(value, response.text)

    def verify_response_not_contains_value(self, value, response=None):
        """
        verify if response not contains expected value.
        :param value:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.verify_response_not_contains_value(value, response.text)

    def verify_response_headers_contains_value(self, expected_value, response=None):
        """
        Verify if response headers contains value.
        :param expected_value:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.verify_response_headers_contains_value(expected_value, response)

    def verify_response_reason(self, expected_reason, response=None):
        """
        Verify response reason.
        :param expected_reason:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.verify_response_reason(expected_reason, response.reason)

    def verify_response_value_type(self, key, expected_type, response=None):
        """
        Verify response value type.
        :param key:
        :param expected_type:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        json_response = self.response_to_json(response)
        self.verification.verify_response_value_type(key, expected_type, json_response)

    def xml_verify_response_value_type(self, key, expected_type, response=None):
        """
        Verify xml response value type.
        :param key:
        :param expected_type:
        :param response:
        :return:
        """
        if response is None:
            response = self.context.api.xml_response

        self.verification.xml_verify_response_value_type(key, expected_type, response)

    def verify_response_contains_key(self, key, response=None):
        """
        Verify response contains a expected key.
        :param key:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.verify_response_contains_key(key, response)

    def xml_verify_response_contains_key(self, key, response=None):
        """
        Verify if xml response contains a expected key.
        :param key:
        :param response:
        :return:
        """
        if response is None:
            response = self.context.api.xml_response

        self.verification.xml_verify_response_contains_key(key, response)

    def verify_value_type_in_response_with_path(self, param_path_key: str, expected_value, response):
        """
        verify response value type from with path.
        :param param_path_key:
        :param expected_value:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.verify_value_type_in_response_with_path(param_path_key, expected_value, response)

    def xml_verify_value_type_in_response_with_path(self, param_path_key: str, expected_value, response=None):
        """
        Verify xml response value type from key path.
        :param param_path_key:
        :param expected_value:
        :param response:
        :return:
        """
        if response is None:
            response = self.context.api.xml_response

        self.verification.xml_verify_value_type_in_response_with_path(param_path_key, expected_value, response)

    def response_time_is_less_than(self, seconds_expected, response=None):
        """
        Verify if response time is less than a expected time.
        :param seconds_expected:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.response_time_is_less_than(seconds_expected, response)

    def response_time_is_greater_than(self, seconds_expected, response=None):
        """
        Verify if response time is greater than a expected time.
        :param seconds_expected:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.response_time_is_greater_than(seconds_expected, response)

    def response_time_is_between(self, less_expected, greater_expected, response=None):
        """
        Verify if response is between a less expected time and a greater expected time.
        :param less_expected:
        :param greater_expected:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        self.verification.response_time_is_between(less_expected, greater_expected, response)

    def status_code_is_one_of(self, expected_values: list, response=None):
        """
        Verify if status code is on of a expected list with status code.
        :param expected_values:
        :param response:
        :return:
        """
        response = self._get_response_if_none(response)
        current_value = response.status_code
        self.verification.status_code_is_one_of(expected_values, current_value)

    def get_request_url(self):
        """
        Return requests url from response.
        :return:
        """
        return self.response.url

    def set_api_info(self, arguments):
        """
        Set api request and response information in order to include in evidences.
        :param arguments:
        :return:
        """
        self.context.runtime.api_info = {
            "url": arguments["URL"],
            "method": arguments["Method"],
            "reason": str(arguments["response"].reason),
            "status_code": str(arguments["response"].status_code),
            "remote Address": self.get_remote_ip(),
            "headers": arguments["headers"],
            "body": arguments["body"],
            "params": arguments["params"]
        }

        try:
            self.context.runtime.api_info['response_headers'] = get_json_formatted(dict(arguments['response_headers']))
            self.context.runtime.api_info['response'] = get_json_formatted(arguments["response"].json())
        except json.decoder.JSONDecodeError:
            try:
                self.context.runtime.api_info['response'] = arguments["response"].text
            except(Exception,):
                self.context.runtime.api_info['response'] = ""

    def convert_request_to_curl(self, compressed=False, verify=True):
        """
        Returns string with curl command by provided request object
        :Param request_response:
        :Param compressed:
        :Param verify:
        """
        parts = [
            ('curl', None),
            ('-X', self.response.request.method),
        ]

        for k, v in sorted(self.response.request.headers.items()):
            parts += [('-H', '{0}: {1}'.format(k, v))]

        if self.response.request.body:
            body = self.response.request.body
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            parts += [('-d', body)]

        if compressed:
            parts += [('--compressed', None)]

        if not verify:
            parts += [('--insecure', None)]

        url = deepcopy(self.request.url)
        params = []
        if self.params:
            for key, value in self.params.items():
                params.append(f'{key}={value}')
            formatted_params = '&'.join(params)
            url = f'{url}?{formatted_params}'
        parts += [(None, url)]

        flat_parts = []
        for k, v in parts:
            if k:
                flat_parts.append(quote(k))
            if v:
                flat_parts.append(quote(v))

        curl = ' '.join(flat_parts)
        logger.info(f'Curl from request was generated: {curl}')
        return curl
