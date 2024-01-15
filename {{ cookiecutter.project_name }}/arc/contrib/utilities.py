# -*- coding: utf-8 -*-
"""
Generic utilities module for all types of automations and functionalities.
"""
import errno

import pkg_resources
import gettext
import logging
import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse

import requests
from behave.runner_util import exec_file
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from arc.core import constants
from arc.core.test_method.exceptions import TalosTestError
from arc.page_elements import Button, Checkbox, Group, InputRadio, InputText, Link, Select, Text
from arc.page_elements.layer_page_element import Layer
from arc.page_elements.page_elements import (
    Layers, Buttons, Checkboxes,
    Groups, InputRadios, InputTexts,
    Links, Selects, Texts
)
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


def load_modules(file_path):
    """
    Load modules from file path.
    """
    file_split = file_path.split(os.sep)
    file_path = os.sep.join(file_split[:-1])
    file_name = file_split[-1]
    exec_file(os.path.join(file_path, file_name))


def load_translation(domain, lang=Settings.PYTALOS_REPORTS.get('reports_language')):
    """
    Load Babel translation.
    :param domain:
    :param lang:
    :return:
    """
    logger.info(f"Loading translation file for domain {domain} and lang {lang}")
    gnu_translations = gettext.translation(
        domain=domain,
        localedir=Settings.LOCALE_PATH.get(force=True),
        languages=[lang]
    )

    gnu_translations.install()
    return gnu_translations


def makedirs_safe(folder):
    """
    Create a new folder if it does not exist
    :param folder: folder path
    """
    try:
        os.makedirs(folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def get_message_exception(exception):
    """
    Get message exception parsed.
    :param exception:
    :return:
    """
    return str(exception).split('\n', 1)[0]


def get_valid_filename(s, max_length=constants.FILENAME_MAX_LENGTH):
    """
    Get valid file name string from a current file name (s) with a file name max length.
    :param s:
    :param max_length:
    :return:
    """
    s = str(s).strip().replace(' -- @', '_')
    s = re.sub(r'(?u)[^-\w]', '_', s).strip('_')
    return s[:max_length]


def get_installed_packages():
    """
        Return a list of the installed packages
    :return:
    """
    packages = {}
    for item in pkg_resources.working_set:
        packages[item.key] = item.version
    return packages


class Utils(object):
    """
    Class of web, server, selenium and page element utilities.
    """
    _window_size = None
    page_element_instances = (Button, Text, InputText, InputRadio, Link, Checkbox, Select, Group, Layer)

    def __init__(self, driver_wrapper=None):
        from arc.core.driver.driver_manager import DriverManager
        self.driver_wrapper = driver_wrapper if driver_wrapper else DriverManager.get_default_wrapper()

    def set_implicitly_wait(self):
        """
        Set an implicitly wait to driver instance.
        :return: 
        """
        implicitly_wait = self.driver_wrapper.config.get_optional('Driver', 'implicitly_wait')
        logger.debug(f'Implicitly wait configured: {implicitly_wait}')
        if implicitly_wait:
            self.driver_wrapper.driver.implicitly_wait(implicitly_wait)

    def get_explicitly_wait(self):
        """
        Get explicitly wait configured.
        :return: 
        """
        explicitly_wait = int(self.driver_wrapper.config.get_optional('Driver', 'explicitly_wait', '10'))
        logger.debug(f'Explicitly wait configured: {explicitly_wait}')
        return explicitly_wait

    def capture_screenshot(self, name):
        """
        Take a capture screenshot with a file name passed by parameter.
        :param name: 
        :return: 
        """
        from arc.core.driver.driver_manager import DriverManager
        filename = '{0:0=2d}_{1}'.format(DriverManager.screenshots_number, name)
        filename = '{}.png'.format(get_valid_filename(filename))
        filepath = os.path.join(DriverManager.screenshots_directory, filename)
        if not os.path.exists(DriverManager.screenshots_directory):
            os.makedirs(DriverManager.screenshots_directory)
        if self.driver_wrapper.driver.get_screenshot_as_file(filepath):
            logger.info('Screenshot saved in %s', filepath)
            DriverManager.screenshots_number += 1
            return filepath
        return None

    @staticmethod
    def get_path_capture_screenshot_autogui(name):
        """
        This method return the path to store the screenshot when using the pyautogui get screenshot
        :param name:
        :return:
        """
        from arc.core.driver.driver_manager import DriverManager
        filename = '{0:0=2d}_{1}'.format(DriverManager.screenshots_number, name)
        filename = '{}.png'.format(get_valid_filename(filename))
        if not os.path.exists(DriverManager.screenshots_directory):
            os.makedirs(DriverManager.screenshots_directory)
        filepath = os.path.join(DriverManager.screenshots_directory, filename)
        return filepath

    def save_webdriver_logs(self, test_name):
        """
        Save webdriver logs.
        :param test_name:
        :return:
        """
        try:
            log_types = self.driver_wrapper.driver.log_types
        except (Exception,):
            # geckodriver does not implement log_types, but it implements get_log for client and server
            log_types = ['client', 'server']

        logger.debug("Reading logs from '%s' and writing them to log files", ', '.join(log_types))
        for log_type in log_types:
            try:
                self.save_webdriver_logs_by_type(log_type, test_name)
                logger.debug(f'Saving webdriver logs type {log_type} for test name {test_name}')
            except (Exception,) as ex:
                # Capture exceptions to avoid errors in teardown method
                logger.warning(f'Unable to save webdriver logs: {ex}')

    def save_webdriver_logs_by_type(self, log_type, test_name):
        """
        Save webdriver logs by type.
        :param log_type:
        :param test_name:
        :return:
        """
        try:
            logs = self.driver_wrapper.driver.get_log(log_type)
        except (Exception,) as ex:
            logger.warning(f'Unable to save webdriver logs: {ex}')
            return

        if len(logs) > 0:
            from arc.core.driver.driver_manager import DriverManager

            log_file_name = '{}_{}.txt'.format(get_valid_filename(test_name), log_type)
            log_file_name = os.path.join(DriverManager.logs_directory, log_file_name)
            with open(log_file_name, 'a+', encoding='utf-8') as log_file:
                driver_type = self.driver_wrapper.config.get('Driver', 'type')
                log_file.write(
                    u"\n{} '{}' test logs with driver = {}\n\n".format(datetime.now(), test_name, driver_type))
                for entry in logs:
                    timestamp = datetime.fromtimestamp(float(entry['timestamp']) / 1000.).strftime(
                        '%Y-%m-%d %H:%M:%S.%f')
                    log_file.write(u'{}\t{}\t{}\n'.format(timestamp, entry['level'], entry['message'].rstrip()))

    def discard_logcat_logs(self):
        """
        Discard logcat logs.
        :return:
        """
        if self.driver_wrapper.is_android_test():
            try:
                self.driver_wrapper.driver.get_log('logcat')
            except (Exception,) as ex:
                logger.warning(f'Unable to save webdriver logs: {ex}')

    @staticmethod
    def get_locator_by(by: str):
        """
        Get str locator from by string.
        :param by:
        :return:
        """
        by = str(by).lower()
        if by == 'xpath':
            return By.XPATH
        elif by == 'id':
            return By.ID
        elif by == 'link text':
            return By.LINK_TEXT
        elif by == 'name':
            return By.NAME
        elif by == 'tag name':
            return By.TAG_NAME
        elif by == 'class name':
            return By.CLASS_NAME
        elif by == 'css selector':
            return By.CSS_SELECTOR
        elif by == 'partial link text':
            return By.PARTIAL_LINK_TEXT
        else:
            return None

    @staticmethod
    def get_page_elements():
        """
        Get page elements dictionary
        :return:
        """
        return {
            'button': Button,
            'buttons': Buttons,
            'checkbox': Checkbox,
            'checkboxes': Checkboxes,
            'group': Group,
            'groups': Groups,
            'inputradio': InputRadio,  # noqa
            'inputradios': InputRadios,  # noqa
            'inputtext': InputText,  # noqa
            'inputtexts': InputTexts,  # noqa
            'link': Link,
            'links': Links,
            'select': Select,
            'selects': Selects,
            'text': Text,
            'texts': Texts,
            'layer': Layer,
            'layers': Layers

        }

    def _expected_condition_find_element(self, element):
        """
        Expected condition find element.
        :param element:
        :return:
        """
        web_element = False
        try:
            from arc.page_elements import PageElement
            if isinstance(element, PageElement):
                # Use _find_web_element() instead of web_element to avoid logging error message
                element._web_element = None
                element._find_web_element()  # noqa
                web_element = element._web_element  # noqa
            elif isinstance(element, tuple):
                web_element = self.driver_wrapper.driver.find_element(*element)
        except NoSuchElementException:
            pass
        return web_element

    def _expected_condition_find_element_visible(self, element):
        """
        Expected condition for fin element until this is visible.
        :param element:
        :return:
        """
        try:
            web_element = self._expected_condition_find_element(element)
            return web_element if web_element and web_element.is_displayed() else False
        except NoSuchElementException as e:
            raise e
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_element_not_visible(self, element):
        web_element = self._expected_condition_find_element(element)
        try:
            return True if not web_element or not web_element.is_displayed() else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_first_element(self, elements):
        """
        Expected condition find element for find first element in an elements list.
        :param elements:
        :return:
        """
        from arc.page_elements import PageElement
        element_found = None
        for element in elements:
            try:
                if isinstance(element, PageElement):
                    element._web_element = None
                    element._find_web_element()  # noqa
                else:
                    self.driver_wrapper.driver.find_element(*element)
                element_found = element
                break
            except (NoSuchElementException, TypeError):
                pass
        return element_found

    def _expected_condition_find_element_clickable(self, element):
        """
        Expected condition for find element unit this is clickable.
        :param element:
        :return:
        """
        web_element = self._expected_condition_find_element_visible(element)
        try:
            return web_element if web_element and web_element.is_enabled() else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_element_stopped(self, element_times):
        """
        Expected condition for find element is stepped.
        :param element_times:
        :return:
        """
        element, times = element_times
        web_element = self._expected_condition_find_element(element)
        try:
            locations_list = [tuple(web_element.location.values()) for _ in range(int(times)) if not time.sleep(0.001)]
            return web_element if set(locations_list) == set(locations_list[-1:]) else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_element_containing_text(self, element_text_pair):
        """
        Expected condition for find element containing text.
        :param element_text_pair:
        :return:
        """
        element, text = element_text_pair
        web_element = self._expected_condition_find_element(element)
        try:
            return web_element if web_element and text in web_element.text else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_element_not_containing_text(self, element_text_pair):
        """
        Expected condition for find element not containing text.
        :param element_text_pair:
        :return:
        """
        element, text = element_text_pair
        web_element = self._expected_condition_find_element(element)
        try:
            return web_element if web_element and text not in web_element.text else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_value_in_element_attribute(self, element_attribute_value):
        """
        Expected condition value in element attribute.
        :param element_attribute_value:
        :return:
        """
        element, attribute, value = element_attribute_value
        web_element = self._expected_condition_find_element(element)
        try:
            return web_element if web_element and web_element.get_attribute(attribute) == value else False
        except StaleElementReferenceException:
            return False

    def _wait_until(self, condition_method, condition_input, timeout=None):
        """
        Generic wait until for a condition method and a condition input.
        :param condition_method:
        :param condition_input:
        :param timeout:
        :return:
        """
        # Remove implicitly wait timeout
        self.driver_wrapper.driver.implicitly_wait(0)
        # Get explicitly wait timeout
        timeout = timeout if timeout else self.get_explicitly_wait()
        condition_response = WebDriverWait(self.driver_wrapper.driver, timeout).until(
            lambda s: condition_method(condition_input))
        # Restore implicitly wait timeout from properties
        self.set_implicitly_wait()
        return condition_response

    def wait_until_element_present(self, element, timeout=None):
        """
        Wait until element is present in the DOM.
        :param element:
        :param timeout:
        :return:
        """
        logger.info(f'Waiting until element is present: {element}')
        return self._wait_until(self._expected_condition_find_element, element, timeout)

    def wait_until_element_visible(self, element, timeout=None):
        """
        Wait until element is visible in DOM and page.
        :param element:
        :param timeout:
        :return:
        """
        logger.info(f"Waiting until element is visible: {element}")
        return self._wait_until(self._expected_condition_find_element_visible, element, timeout)

    def wait_until_element_not_visible(self, element, timeout=None):
        """
        Wait until element is not visible in DOM and page.
        :param element:
        :param timeout:
        :return:
        """
        logger.info(f"Waiting until element is not visible: {element}")
        return self._wait_until(self._expected_condition_find_element_not_visible, element, timeout)

    def wait_until_first_element_is_found(self, elements, timeout=None):
        """
        Wait until first element of a elements list is found.
        :param elements:
        :param timeout:
        :return:
        """
        try:
            logger.info(f"Waiting until first element is found: {elements}")
            return self._wait_until(self._expected_condition_find_first_element, elements, timeout)
        except TimeoutException as ex:
            msg = 'None of the page elements has been found after %s seconds'
            timeout = timeout if timeout else self.get_explicitly_wait()
            logger.error(msg, timeout)
            ex.msg += "\n  {}".format(msg % timeout)
            raise TalosTestError(ex)

    def wait_until_element_clickable(self, element, timeout=None):
        """
        Wait until element is clickable.
        :param element:
        :param timeout:
        :return:
        """
        logger.info(f"Waiting until element is clickable : {element}")
        return self._wait_until(self._expected_condition_find_element_clickable, element, timeout)

    def wait_until_element_stops(self, element, times=1000, timeout=None):
        """
        Wait until element is stopped.
        :param element:
        :param times:
        :param timeout:
        :return:
        """
        logger.info(f"Waiting until element is stopped : {element}")
        return self._wait_until(self._expected_condition_find_element_stopped, (element, times), timeout)

    def wait_until_element_contains_text(self, element, text, timeout=None):
        """
        Wait until element contains text passed by parameter.
        :param element:
        :param text:
        :param timeout:
        :return:
        """
        logger.info(f"Waiting until element contains text {text} : {element}")
        return self._wait_until(self._expected_condition_find_element_containing_text, (element, text), timeout)

    def wait_until_element_not_contain_text(self, element, text, timeout=None):
        """
        Wait until element is not contain text passed by parameter.
        :param element:
        :param text:
        :param timeout:
        :return:
        """
        logger.info(f"Waiting until element do not contain text {text} : {element}")
        return self._wait_until(self._expected_condition_find_element_not_containing_text, (element, text), timeout)

    def wait_until_element_attribute_is(self, element, attribute, value, timeout=None):
        """
        Wait until element attribute is one of passed by parameter.
        :param element:
        :param attribute:
        :param value:
        :param timeout:
        :return:
        """
        logger.info(f"Waiting until element is {attribute} wit value {value} : {element}")
        return self._wait_until(self._expected_condition_value_in_element_attribute, (element, attribute, value),
                                timeout)

    def wait_presence_of_element_located(self, driver, by, locator, delay=30):
        """
        Wait presence of an element located.
        :param driver:
        :param by:
        :param locator:
        :param delay:
        :return:
        """
        loc_by = self.get_locator_by(by)
        logger.info(f"Waiting presence of element located by {loc_by} and locator {locator}")
        element = WebDriverWait(driver, delay).until(ec.presence_of_element_located((loc_by, locator)))
        return element

    def wait_frame_to_be_available_and_switch_to_it(self, driver, by, locator, delay=30):
        """
        Wait frame to be an available and switch to it.
        :param driver:
        :param by:
        :param locator:
        :param delay:
        :return:
        """
        loc_by = self.get_locator_by(by)
        logger.info(f"Waiting for frame is available and switch to it with by {by} and locator {locator}")
        element = WebDriverWait(driver, delay).until(ec.frame_to_be_available_and_switch_to_it((loc_by, locator)))
        return element

    @staticmethod
    def wait_until_title_is(driver, title, delay=30):
        """
        Wait until title is the title passed by parameter.
        :param driver:
        :param title:
        :param delay:
        :return:
        """
        logger.info(f"Waiting until page title is {title}")
        element = WebDriverWait(driver, delay).until(ec.title_is(title))
        return element

    @staticmethod
    def wait_until_title_contains(driver, title, delay=30):
        """
        Wait until title contains a substring passed by parameter.
        :param driver:
        :param title:
        :param delay:
        :return:
        """
        logger.info(f"Waiting until page title contains {title}")
        element = WebDriverWait(driver, delay).until(ec.title_contains(title))
        return element

    @staticmethod
    def wait_until_alert_is_present(driver, delay=30):
        """
        Wait until alert is present.
        :param driver:
        :param delay:
        :return:
        """
        logger.info(f"Waiting until alert is present")
        element = WebDriverWait(driver, delay).until(ec.alert_is_present())
        return element

    def get_remote_node(self):
        """
        Get remote node server.
        :return:
        """
        logging.getLogger("requests").setLevel(logging.WARNING)
        remote_node = None
        server_type = 'local'
        if self.driver_wrapper.config.getboolean_optional('Server', 'enabled'):
            # Request session info from grid hub
            session_id = self.driver_wrapper.driver.session_id
            logger.debug("Trying to identify remote node")
            try:
                # Request session info from grid hub and extract remote node
                url = '{}/grid/api/testsession?session={}'.format(  # noqa
                    self.get_server_url(),
                    session_id
                )
                proxy_id = requests.get(url, verify=False).json()['proxyId']  # noqa
                remote_node = urlparse(proxy_id).hostname if urlparse(proxy_id).hostname else proxy_id
                server_type = 'grid'
                logger.debug("Test running in remote node %s", remote_node)
            except (ValueError, KeyError):
                try:
                    # Request session info from GGR and extract remote node
                    from arc.integrations.selenoid import Selenoid
                    remote_node = Selenoid(self.driver_wrapper).get_selenoid_info()['Name']
                    server_type = 'ggr'
                    logger.debug("Test running in a GGR remote node %s", remote_node)
                except (Exception,):
                    try:
                        # The remote node is a Selenoid node
                        url = '{}/status'.format(self.get_server_url())
                        total = requests.get(url).json()['total']
                        remote_node = self.driver_wrapper.config.get('Server', 'host')
                        server_type = 'selenoid'
                        logger.debug(f"Test running in a Selenoid node {remote_node}")
                        logger.debug(f"Test running total in Selenoid node {total}")
                    except (Exception,):
                        # The remote node is not a grid node or the session has been closed
                        remote_node = self.driver_wrapper.config.get('Server', 'host')
                        server_type = 'selenium'
                        logger.debug("Test running in a Selenium node %s", remote_node)

        return server_type, remote_node

    def get_server_url(self):
        """
        Get server url.
        :return:
        """
        server_auth = None
        server_host = self.driver_wrapper.config.get('Server', 'host')
        server_url = server_host
        server_port = self.driver_wrapper.config.get('Server', 'port')
        server_username = self.driver_wrapper.config.get_optional('Server', 'username')
        server_password = self.driver_wrapper.config.get_optional('Server', 'password')
        if server_username != '' and server_password != '':
            server_auth = '{}:{}@'.format(
                server_username,
                server_password
            ) if server_username and server_password else ''

        if server_auth:
            split_server_url = str(server_host).split('//')
            server_url = '{}//{}{}'.format(split_server_url[0], server_auth, split_server_url[1])
        if server_port != '':
            server_url = server_url + ':{}'.format(server_port)

        logger.debug(f'Server url obtained: {server_url}')
        return server_url

    def download_remote_video(self, remote_node, session_id, video_name):
        """
        Download remote video recorded.
        :param remote_node:
        :param session_id:
        :param video_name:
        :return:
        """
        try:
            video_url = self._get_remote_video_url(remote_node, session_id)
        except requests.exceptions.ConnectionError:
            logger.warning("Remote server seems not to have video capabilities")
            return

        if not video_url:
            logger.warning("Test video not found in node '%s'", remote_node)
            return

        self._download_video(video_url, video_name)

    @staticmethod
    def _get_remote_node_url(remote_node, protocol='http'):
        """
        Get remote node url.
        :param remote_node:
        :return:
        """
        grid_extras_port = 3000
        return '{}://{}:{}'.format(protocol, remote_node, grid_extras_port)

    def _get_remote_video_url(self, remote_node, session_id):
        """
        Get remote video url.
        :param remote_node:
        :param session_id:
        :return:
        """
        url = '{}/video'.format(self._get_remote_node_url(remote_node))
        timeout = time.time() + 5  # 5 seconds from now

        # Requests videos list until timeout or the video url is found
        video_url = None
        while time.time() < timeout:
            response = requests.get(url).json()
            try:
                video_url = response['available_videos'][session_id]['download_url']
                break
            except KeyError:
                time.sleep(1)
        logger.debug(f"Remote video url obtained: {video_url}")
        return video_url

    @staticmethod
    def _download_video(video_url, video_name):
        """
        Download video from url.
        :param video_url:
        :param video_name:
        :return:
        """
        logger.debug(f"Downloading video with name {video_name} and url {video_url}")
        from arc.core.driver.driver_manager import DriverManager
        filename = '{0:0=2d}_{1}'.format(DriverManager.videos_number, video_name)
        filename = '{}.mp4'.format(get_valid_filename(filename))
        filepath = os.path.join(DriverManager.videos_directory, filename)
        if not os.path.exists(DriverManager.videos_directory):
            os.makedirs(DriverManager.videos_directory)
        response = requests.get(video_url)
        open(filepath, 'wb').write(response.content)
        logger.info("Video saved in '%s'", filepath)
        DriverManager.videos_number += 1

    def is_remote_video_enabled(self, remote_node):
        """
        Check is remote vide enabled.
        :param remote_node:
        :return:
        """
        enabled = False
        if remote_node:
            url = '{}/config'.format(self._get_remote_node_url(remote_node))
            try:
                response = requests.get(url, timeout=5).json()
                record_videos = response['config_runtime']['theConfigMap']['video_recording_options'][
                    'record_test_videos']
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, KeyError):
                record_videos = 'false'
            if record_videos == 'true':
                # Wait to the video recorder start
                time.sleep(1)
                enabled = True
        return enabled

    def get_center(self, element):
        """
        Get center of a element.
        :param element:
        :return:
        """
        web_element = self.get_web_element(element)
        location = web_element.location
        size = web_element.size
        return {'x': location['x'] + (size['width'] / 2), 'y': location['y'] + (size['height'] / 2)}

    def get_safari_navigation_bar_height(self):
        """
        Get safari browser navigation bar height.
        :return:
        """
        status_bar_height = 0
        if self.driver_wrapper.is_ios_test() and self.driver_wrapper.is_web_test():
            # ios 7.1, 8.3
            status_bar_height = 64
        return status_bar_height

    def get_window_size(self):
        """
        Get window size.
        :return:
        """
        if not self._window_size:
            if self.driver_wrapper.is_android_web_test() and self.driver_wrapper.driver.current_context != 'NATIVE_APP':
                window_width = self.driver_wrapper.driver.execute_script("return window.innerWidth")
                window_height = self.driver_wrapper.driver.execute_script("return window.innerHeight")
                self._window_size = {'width': window_width, 'height': window_height}
            else:
                self._window_size = self.driver_wrapper.driver.get_window_size()

        logger.debug(f"Window size obtained: {self._window_size}")
        return self._window_size

    def get_native_coords(self, coords):
        """
        Get native coords.
        :param coords:
        :return:
        """
        web_window_size = self.get_window_size()
        self.driver_wrapper.driver.switch_to.context('NATIVE_APP')
        native_window_size = self.driver_wrapper.driver.get_window_size()
        scale = native_window_size['width'] / web_window_size['width']
        offset_y = self.get_safari_navigation_bar_height()
        native_coords = {'x': coords['x'] * scale, 'y': coords['y'] * scale + offset_y}
        logger.debug('Converted web coords %s into native coords %s', coords, native_coords)
        return native_coords

    def swipe(self, element, x, y, duration=None):
        """
        Swipe on element by coords.
        :param element:
        :param x:
        :param y:
        :param duration:
        :return:
        """
        logger.debug(f"Performing a swipe action in element {element} wit cords x:{x} y:{y}")
        if not self.driver_wrapper.is_mobile_test():
            msg = 'Swipe method is not implemented in Selenium'
            logger.error(msg)
            raise TalosTestError(msg)

        # Get center coordinates of element
        center = self.get_center(element)
        initial_context = self.driver_wrapper.driver.current_context
        if self.driver_wrapper.is_web_test() or initial_context != 'NATIVE_APP':
            center = self.get_native_coords(center)

        # Android needs absolute end coordinates and ios needs movement
        end_x = x if self.driver_wrapper.is_ios_test() else center['x'] + x
        end_y = y if self.driver_wrapper.is_ios_test() else center['y'] + y
        self.driver_wrapper.driver.swipe(center['x'], center['y'], end_x, end_y, duration)

        if self.driver_wrapper.is_web_test() or initial_context != 'NATIVE_APP':
            self.driver_wrapper.driver.switch_to.context(initial_context)

    def get_web_element(self, element):
        """
        Get web element from element.
        :param element:
        :return:
        """
        from arc.page_elements import PageElement
        if isinstance(element, WebElement):
            web_element = element
        elif isinstance(element, PageElement):
            web_element = element.web_element
        elif isinstance(element, tuple):
            web_element = self.driver_wrapper.driver.find_element(*element)
        else:
            web_element = None
        return web_element

    def get_first_webview_context(self):
        """
        Get first webview context.
        :return:
        """
        for context in self.driver_wrapper.driver.contexts:
            if context.startswith('WEBVIEW'):
                return context

        msg = 'No WEBVIEW context has been found'
        logger.error(msg)
        raise TalosTestError(msg)

    def switch_to_first_webview_context(self):
        """
        Switch to first webview context.
        :return:
        """
        self.driver_wrapper.driver.switch_to.context(self.get_first_webview_context())

    def highlight_element(self, element, color='red', border='4', other=None):
        """
        Highlight element with a color and border.
        :param other:
        :param element:
        :param color:
        :param border:
        :return:
        """
        is_page_element = self.is_page_element_instance(element)
        if is_page_element is True:
            element = self.convert_to_selenium_element(element)

        original_style = element.get_attribute('style')
        if other:
            style = other
        else:
            style = "border: {0}px solid {1};".format(border, color)
        self.driver_wrapper.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, style)
        return original_style

    def unhighlight_element(self, element, original_style):
        """
        Unhighlight element with the original style.
        :param element:
        :param original_style:
        :return:
        """
        is_page_element = self.is_page_element_instance(element)
        if is_page_element is True:
            element = self.convert_to_selenium_element(element)
        self.driver_wrapper.driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            element,
            original_style
        )

    def is_page_element_instance(self, element):
        """
        Check if element is a pge element instance.
        :param element:
        :return:
        """
        is_page_element = False
        if isinstance(element, self.page_element_instances):
            is_page_element = True

        return is_page_element

    def convert_to_selenium_element(self, page_element):
        """
        Convert page element instance to selenium element web element instance.
        :param page_element:
        :return:
        """
        by, loc = page_element.locator

        if ".shadowRoot." in loc:
            locators = loc.split('.shadowRoot.')
            return self.get_element_inside_shadowroot(locators=locators)
        else:
            if by == 'xpath':
                page_element = self.driver_wrapper.driver.find_element(By.XPATH, loc)
            elif by == 'id':
                page_element = self.driver_wrapper.driver.find_element(By.ID, loc)
            elif by == 'link text':
                page_element = self.driver_wrapper.driver.find_element(By.LINK_TEXT, loc)
            elif by == 'name':
                page_element = self.driver_wrapper.driver.find_element(By.NAME, loc)
            elif by == 'tag name':
                page_element = self.driver_wrapper.driver.find_element(By.TAG_NAME, loc)
            elif by == 'class name':
                page_element = self.driver_wrapper.driver.find_element(By.CLASS_NAME, loc)
            elif by == 'css selector':
                page_element = self.driver_wrapper.driver.find_element(By.CSS_SELECTOR, loc)
            elif by == 'partial link text':
                page_element = self.driver_wrapper.driver.find_element(By.PARTIAL_LINK_TEXT, loc)
        return page_element

    def move_to_element(self, element):
        """
        Performing a move action to element.
        :param element:
        :return:
        """
        logger.info(f"Performing a move action to element: {element}")
        if self.is_page_element_instance(element):
            element = self.convert_to_selenium_element(element)
        action = ActionChains(self.driver_wrapper.driver)
        action.move_to_element(element).perform()

    def double_click(self, element):
        """
        Performing a double click action on element.
        :param element:
        :return:
        """
        logger.info(f"Performing a double click action to element: {element}")
        if self.is_page_element_instance(element):
            element = self.convert_to_selenium_element(element)
        action = ActionChains(self.driver_wrapper.driver)
        double_click = action.double_click(element)
        double_click.perform()

    def js_click(self, element):
        """
        Performing a javascript click on element.
        :param element:
        :return:
        """
        logger.info(f"Performing a javascript click on element: {element}")
        if self.is_page_element_instance(element):
            element = self.convert_to_selenium_element(element)

        self.driver_wrapper.driver.execute_script("arguments[0].click();", element)

    def js_send_keys(self, element, value):
        """
        Performing a javascript send keys on element.
        :param element:
        :param value:
        :return:
        """
        logger.info(f"Performing a javascript send key on element: {element} and value {value}")
        if self.is_page_element_instance(element):
            element = self.convert_to_selenium_element(element)

        self.driver_wrapper.driver.execute_script(f"arguments[0].setAttribute('value', '{value}')", element)

    def js_clear(self, element):
        """
        Performing a javascript clear action on element.
        :param element:
        :return:
        """
        logger.info(f"Performing a javascript clear on element: {element}")
        if self.is_page_element_instance(element):
            element = self.convert_to_selenium_element(element)

        self.driver_wrapper.driver.execute_script(f"arguments[0].setAttribute('value', '')", element)

    def change_style_attribute(self, element, attribute, value):
        """
        Change style attribute.
        :param element:
        :param attribute:
        :param value:
        :return:
        """
        logger.info(f"Changing style attribute of element: {element}, att: {attribute} and value {value}")
        if self.is_page_element_instance(element):
            element = self.convert_to_selenium_element(element)
        self.driver_wrapper.driver.execute_script(f"arguments[0].{attribute} = '{value}';", element)

    def switch_to_active_element(self):
        """
        Switch focus to active element.
        :return:
        """
        logger.info(f"Switching to active element")
        return self.driver_wrapper.driver.switch_to.active_element

    def get_element_inside_shadowroot(self, locators, element=None):  # noqa
        """
        Get element inside a shadow root.
        :param locators:
        :param element:
        :return:
        """
        for idx, locator in enumerate(locators):
            if element is None:
                shadow_host = self.driver_wrapper.driver.find_element(By.CSS_SELECTOR, locator)
                shadow_r = shadow_host.shadow_root
                element = shadow_r.find_element(By.CSS_SELECTOR, locators[idx + 1])
            else:
                if idx < len(locators) - 1:
                    element = element.shadow_root.find_element(By.CSS_SELECTOR, locators[idx + 1])
        return element


def set_test_default_data():
    """
    This function call the different functions to add custom attributes to the Feature, Scenario and Step classes.
    """
    set_feature_default_data()
    set_scenario_default_data()
    set_step_default_data()
    logger.debug('Setup custom attributes for Feature, Scenario and Step classes')


def set_step_default_data():
    """
    This function set custom attributes to the Step classes.
    """
    from behave.model import Step
    Step.response_content = None
    Step.response_headers = None
    Step.request = None
    Step.screenshots = []
    Step.jsons = []
    Step.api_info = []
    Step.unit_tables = []
    Step.additional_text = []
    Step.additional_html = []
    Step.start_time = None
    Step.end_time = None
    Step.sub_steps = []

    logger.debug('Setup custom step attributes')


def set_scenario_default_data():
    """
    This function set custom attributes to the Scenario and ScenarioOutline classes.
    """
    from behave.model import Scenario
    Scenario.total_steps = 0
    Scenario.steps_passed = 0
    Scenario.steps_failed = 0
    Scenario.steps_skipped = 0
    Scenario.steps_passed_percent = "0"
    Scenario.steps_failed_percent = "0"
    Scenario.steps_skipped_percent = "0"
    Scenario.sub_steps = []

    logger.debug('Setup custom scenario attributes')


def set_feature_default_data():
    """
    This function set custom attributes to the Feature class.
    :return:
    """
    from behave.model import Feature
    Feature.passed_scenarios = 0
    Feature.failed_scenarios = 0
    Feature.total_scenarios = 0

    Feature.total_steps = 0
    Feature.steps_passed = 0
    Feature.steps_failed = 0
    Feature.steps_skipped = 0

    Feature.passed_scenarios = 0
    Feature.failed_scenarios = 0
    Feature.total_scenarios = 0

    Feature.scenarios_passed_percent = "0"
    Feature.scenarios_failed_percent = "0"
    Feature.steps_passed_percent = "0"
    Feature.steps_failed_percent = "0"
    Feature.steps_skipped_percent = "0"

    Feature.start_time = None
    Feature.end_time = None

    logger.debug('Setup custom feature attributes')

