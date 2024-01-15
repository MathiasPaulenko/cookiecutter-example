import json
import os.path
import subprocess
import logging
import requests
from colorama import Fore

from arc.settings.settings_manager import Settings
from arc.talos_virtual.core.exception.exceptions import VerificationException


class MountebankWrapper:
    """
    Wrapper for managing an imposter running in a mountebank service.
    """
    def __init__(self, url=None, imposter_protocol=None, imposter_name=None, input_path=None):
        """
        The MountebankWrapper object must be instantiated by passing the url, protocol, name where we are going to run
        mountebank and the input path where is stored the imposter file
        @param url:
        @param imposter_protocol:
        @param imposter_name:
        @param input_path:
        """
        self._process = None
        self._session = requests.Session()
        if url:
            self.url = url
        else:
            self.url = Settings.TALOS_VIRTUAL.get('general').get("url")
        if imposter_name:
            self.imposter_name = imposter_name
        else:
            self.imposter_name = Settings.TALOS_VIRTUAL.get('mountebank').get("imposter_name")
        if imposter_protocol:
            self.imposter_protocol = imposter_protocol
        else:
            self.imposter_protocol = Settings.TALOS_VIRTUAL.get('mountebank').get("imposter_protocol")
        if input_path:
            self.input_path = input_path
        else:
            if Settings.TALOS_VIRTUAL.get('general').get("input_path"):
                self.input_path = Settings.TALOS_VIRTUAL.get('general').get("input_path")
            else:
                self.input_path = os.path.join('test', 'helpers', 'resources')
        if self.url == 'localhost' or self.url == '127.0.0.1':
            self.manager_port = Settings.TALOS_VIRTUAL.get('mountebank').get("manager_port")
            self.imposter_port = Settings.TALOS_VIRTUAL.get('mountebank').get("imposter_port")
        else:
            self.manager_port = 2525
            self.imposter_port = 8080

        self._service_path = f'{self.imposter_protocol}://{self.url}:{self.manager_port}/imposters'

    def stop_process(self):
        """
        Stop the mountebank process in localhost
        """
        logging.info("Stopping mountebank service in localhost...")
        self._process = subprocess.Popen("mb stop", stdout=subprocess.PIPE, shell=True)
        logging.info("Mountebank service is stopped.")

    @staticmethod
    def is_service_installed(service):
        """
        Check if a service is installed in local
        :param service: The service to check if it is installed
        :return: True or False
        """
        process = subprocess.Popen(f"""{service} --version""", stdout=subprocess.PIPE, shell=True)
        output = process.communicate()
        if output[0] == b'':
            logging.error(f"""{service} is not installed in localhost.""")
            return False
        else:
            logging.info(f"""{service} is successfully installed.""")
            return True

    def start_process(self):
        """
        Start the process mountebank in localhost
        """
        if Settings.TALOS_VIRTUAL.get('general').get('url') == 'localhost' or Settings.TALOS_VIRTUAL.get('general').get('url') == '127.0.0.1':
            if self.is_service_installed('npm') is True:
                if self.is_service_installed('mb') is True:
                    logging.info("Starting mountebank service in localhost...")
                    print(Fore.BLUE + "INFO: Running a virtualized service.")
                    self._process = subprocess.Popen(f"""mb --allowInjection --port {self.manager_port}""", stdout=subprocess.PIPE, shell=True)
                    for line in iter(self._process.stdout.readline, b''):
                        line = line.decode(encoding='utf8', errors='ignore').replace("\n", "").replace("\r", "")
                        logging.info(line)
                        if 'now taking orders' in line:
                            break
                    logging.info("Mountebank service is running.")

    def delete_imposter(self, port):
        """
        Delete an imposter from a given port
        :param port: End port where imposter is running
        :return:
        """
        logging.info(f"""Deleting the imposter of the port {port}...""")
        imposters_path = f'{self._service_path}/{port}'
        response = self._session.delete(imposters_path)
        if response.status_code not in (200, 201, 202):
            logging.error(f"""It was impossible to delete the imposter.""")
            raise VerificationException(
                error_msg=f''''It was impossible to delete the imposter in port {port} with error: {str(response.content)}'''
            )
        logging.info(f"""The imposter was successfully deleted.""")

    def delete_all_imposter(self):
        """
        Delete all the imposters running on mountebank
        :return:
        """
        logging.info(f"""Deleting all the imposters...""")
        response = self._session.delete(self._service_path)
        if response.status_code not in (200, 201, 202):
            logging.error(f"""It was impossible to delete all the imposters.""")
            raise VerificationException(
                error_msg=f''''It was impossible to delete all the imposters with error: {str(response.content)}'''
            )
        logging.info(f"""All the imposters were successfully deleted.""")

    def overwrite_imposter(self, imposter_dict):
        """
        Overwrite the current imposters running on mountebank by another imposter given
        :param imposter_dict: New imposter that will overwrite the current one
        :return:
        """
        logging.info('Overwriting the imposter...')
        response = self._session.put(self._service_path, json=imposter_dict)
        if response.status_code not in (200, 201, 202):
            logging.error('It was impossible to overwrite the imposter.')
            raise VerificationException(
                error_msg=f''''It was impossible to overwrite the imposter with error: {str(response.content)}'''
            )
        logging.info('The imposter was successfully overwritten.')

    def delete_stub_imposter(self, port, index):
        """
        Delete a certain stub from an imposter running on mountebank
        :param port: port where the imposter is running
        :param index: index of the stub that you want to delete
        :return:
        """
        logging.info(f"""Deleting the stub {index} of the port {port}...""")
        imposters_path = f'{self._service_path}/{port}/stubs/{index}'
        response = self._session.delete(imposters_path)
        if response.status_code not in (200, 201, 202):
            logging.error(f"""It was impossible to delete the stub {index}.""")
            raise VerificationException(
                error_msg=f'''It was impossible to delete the stub {index} of the port {port}, with error: {str(response.content)}'''
            )
        logging.info("The stub was successfully deleted.")

    def create_stub_imposter(self, port, stub_dict):
        """
        Create a certain stub from an imposter running on mountebank
        :param port: port where the imposter is running
        :param stub_dict: stub that you want to create
        :return:
        """
        logging.info(f"""Creating new stub in port {port}...""")
        imposters_path = f'{self._service_path}/{port}/stubs'
        response = self._session.post(imposters_path, json=stub_dict)
        if response.status_code not in (200, 201, 202):
            logging.error('It was impossible to create the new stub.')
            raise VerificationException(
                error_msg=f''''It was impossible to create a new stub in port {port}, with error: {str(response.content)}'''
            )
        logging.info(f"""The stub was successfully created in port {port}.""")

    def overwrite_stub(self, port, index, stub_dict):
        """
        Overwrite a certain stub from an imposter running on mountebank
        :param port: port where the imposter is running
        :param index: index of the stub that you want to overwrite
        :param stub_dict: the new stub
        :return:
        """
        logging.info(f"""Overwriting the stub {index} in port {port}...""")
        imposters_path = f'{self._service_path}/{port}/stubs/{index}'
        response = self._session.put(imposters_path, json=stub_dict)
        if response.status_code not in (200, 201, 202):
            logging.error(f"""It was impossible to overwrite the stub {index}.""")
            raise VerificationException(
                error_msg=f''''It was impossible to overwrite the stub {index} in port {port}, with error: {str(response.content)}'''
            )
        logging.info(f"""The stub {index} was successfully overwritten.""")

    def overwrite_all_stubs(self, port, stub_dict):
        """
        Overwrite all stubs from an imposter running on mountebank
        :param port: port where the imposter is running
        :param stub_dict: the new stub
        :return:
        """
        logging.info(f"""Overwriting all stubs in port {port}...""")
        imposters_path = f'{self._service_path}/{port}/stubs'
        response = self._session.put(imposters_path, json=stub_dict)
        if response.status_code not in (200, 201, 202):
            logging.error(f"""It was impossible to overwrite all stubs.""")
            raise VerificationException(
                error_msg=f''''It was impossible to overwrite all the stubs of the port {port}, with error: {str(response.content)}'''
            )
        logging.info(f"""The stubs were successfully overwritten.""")

    def create_imposter(self, dict_imposter):
        """
        Create a new imposter on mountebank service
        :param dict_imposter: the new imposter
        :return:
        """
        logging.info("Creating new imposter...")
        response = self._session.post(self._service_path, json=dict_imposter)
        if response.status_code not in (200, 201, 202):
            logging.error("It was impossible to create the imposter.")
            raise VerificationException(
                error_msg=f''''It was impossible to create the imposter, with error: {str(response.content)}'''
            )
        logging.info("The imposter was successfully created.")

    def get_imposter(self, port):
        """
        Get the imposter information of a port running on mountebank
        :param port: port where the imposter is running
        :return: a dict with the information of the imposter
        """
        logging.info(f"""Getting the imposter in port {port}...""")
        imposters_path = f'{self._service_path}/{port}'
        response = self._session.get(imposters_path)
        if response.status_code not in (200, 201, 202):
            logging.error(f"""It was impossible to get the imposter in port {port}""")
            raise Exception(f'''It was impossible to get the imposter in port: {port}''')
        else:
            logging.info("The imposter was got")
            return json.loads(response.content)

    def get_all_imposter(self):
        """
        Get a dict with the information of all imposters running on mountebank
        :return:
        """
        logging.info(f"""Getting all the imposters...""")
        response = self._session.get(self._service_path)
        if response.status_code not in (200, 201, 202):
            logging.error("It was impossible to get a list of all imposters")
            raise Exception('It was impossible to get a list of all imposters')
        else:
            logging.info("All the imposter was got")
            return json.loads(response.content)
