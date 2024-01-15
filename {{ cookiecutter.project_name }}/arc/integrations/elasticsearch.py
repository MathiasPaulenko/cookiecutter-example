# -*- coding: utf-8 -*-
"""
Elastic Search integration class file.
"""
import json
import logging

import requests

from arc.reports.html.utils import BASE_DIR
from arc.core.constants import ELASTICSEARCH
from arc.core.env_settings import disabled_environment_proxy, activate_environment_proxy

logger = logging.getLogger(__name__)


class Elasticsearch:
    """
    Integration class with Elastic Search for sending execution data to the CoE's Elastic.
    """
    _host = ELASTICSEARCH['host']
    _port = ELASTICSEARCH['port']
    _key = ELASTICSEARCH['ApiKey']
    _index = ELASTICSEARCH['index']
    _header = {
        "Authorization": f"ApiKey {_key}"
    }
    _url = f'{_host}:{_port}'
    _json_path = f'{BASE_DIR}/output/reports/talos_report.json'

    def run(self):
        """
        Run Elastic Search conección and send json execution data.
        :return:
        """
        logger.debug('Running Elastic Search connector')
        disabled_environment_proxy()
        if self._start_connection():
            logger.debug('The connection to Elastic Search was successful')
            self._send_json()
        activate_environment_proxy()

    def _start_connection(self):
        """
        Connect with Elastic Search server through api rest
        :return:
        """
        logger.debug(f"Starting connection to: {self._url}")
        response = requests.get(headers=self._header, url=self._url, verify=False)
        if response.status_code not in (200, 201, 202):
            logger.warning(f"Warning: Impossible to start connection with elastic, {response.text}")
        return response.status_code in (200, 201, 202)

    def _send_json(self):
        """
        Send execution json data through api rest.
        :return:
        """
        file_url = f'{self._url}/{self._index}/_doc/'
        logger.debug(f"Sending execution data to: {file_url}")
        with open(self._json_path) as json_file:
            json_data = json.load(json_file)
        if self._index_exist():
            del json_data['features']
            json_data['global_data']['features'] = json_data['global_data'].pop('results')
            response = requests.post(headers=self._header, url=file_url, json=json_data, verify=False)
            logger.debug("The execution data has been sent to Elastic Search")
            if response.status_code not in (200, 201, 202):
                logger.warning(f"Warning: Impossible to send json data to elastic, {response.text}")
            else:
                logger.debug("Execution data sent to Elastic Search successfully")

    def _index_exist(self):
        """
        Verify if index exists in Elastic Search server.
        :return:
        """
        index_url = f'{self._url}/{self._index}'
        logger.debug(f"Check if index exists: {index_url}")
        response = requests.get(headers=self._header, url=index_url, verify=False)
        if response.status_code not in (200, 201, 202):
            logger.warning(f"Warning: Impossible find index {self._index}")
        return response.status_code in (200, 201, 202)
