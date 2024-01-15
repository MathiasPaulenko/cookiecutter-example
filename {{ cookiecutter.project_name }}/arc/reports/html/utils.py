# -*- coding: utf-8 -*-
"""
Utility module for the generation of HTML reports.
"""
import base64
import datetime
import logging
import os
import jinja2.runtime
from PIL import Image
import xml.dom.minidom
import json

from arc.contrib.tools.formatters import replace_chars
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

BASE_DIR = Settings.BASE_PATH.get(force=True)

jinja_env = None

STATUS_ICONS = {
    'passed': '<i class="status-success-icon"></i>',
    'failed': '<i class="status-failed-icon"></i>',
    'skipped': '<i class="status-skipped-icon"></i>'
}


def format_decimal(value):
    """
    This function format a float value to 2 decimal.
    :param value:
    :type value:
    :return:
    :rtype:
    """
    return f"{value:.2f}"


def get_duration(value):
    """
    Given the seconds its return the datetime.
    :param value:
    :type value:
    :return:
    :rtype:
    """
    if isinstance(value, jinja2.runtime.Undefined) or isinstance(value, str):
        value = 0.0
    return datetime.timedelta(seconds=value)


def get_datetime_from_timestamp(timestamp):
    """
    Given a timestamp return a datetime
    :param timestamp:
    :type timestamp:
    :return:
    :rtype:
    """
    return datetime.datetime.fromtimestamp(timestamp).replace(microsecond=0) if isinstance(timestamp, float) else "-"


def get_date_or_time_from_timestamp(args):
    """
    Given a timestamp return a date or a time depending on the option selected
    :param args:
    :return:
    :rtype:
    """
    timestamp = args[0]
    option = args[1]
    datetime_format = ''
    if option == 'Date':
        datetime_format = '%Y-%m-%d'
    elif option == 'Time':
        datetime_format = '%H:%M:%S'
    return datetime.datetime.fromtimestamp(timestamp).strftime(datetime_format) if isinstance(timestamp, float) else "-"


def get_duration_from_timestamps(args):
    """
    Given a list of an ending timestamp and a starting timestamp return duration
    :param args:
    :type args:
    :return:
    :rtype:
    """
    end_time = datetime.datetime.fromtimestamp(args[0]).replace(microsecond=0)
    start_time = datetime.datetime.fromtimestamp(args[1]).replace(microsecond=0)
    duration = end_time-start_time
    return duration if isinstance(args, list) else "-"


def get_base64_image_by_path(image_path):
    """
    Return a base64 string given an image_path.
    :param image_path:
    :type image_path:
    :return:
    :rtype:
    """
    with open(image_path, 'rb') as image:
        return base64.b64encode(image.read()).decode()


def transform_image_to_webp(image_path):
    """
    Transform any image to webp, saves it in the html/assets/img folder and return the path to the image.
    :param image_path:
    """
    img = Image.open(image_path)
    img_name = img.filename.split(os.sep)[-1].replace('.png', '')
    logger.debug(f"Converting image to webp: {img_name}")
    if Settings.PYTALOS_REPORTS.get('compress_screenshot'):
        img.save(f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/assets/imgs/{img_name}.webp", quality=50)
        return f"./assets/imgs/{img_name}.webp"
    else:
        images_folder = img.filename.split(os.sep)[-2]
        if images_folder == 'screenshots':
            return f"../../screenshots/{img_name}.png"
        else:
            return f"../../screenshots/{images_folder}/{img_name}.png"


def transform_accessibility_image_to_webp(image_path):
    """
    Transform any image to webp, saves it in the html/assets/img folder and return the path to the image.
    :param image_path:
    """
    img = Image.open(image_path)
    img_name = img.filename.split(os.sep)[-1].replace('.png', '')
    logger.debug(f"Converting image to webp: {img_name}")
    if Settings.PYTALOS_REPORTS.get('compress_screenshot'):
        img.save(f"{Settings.BASE_PATH.get(force=True)}/output/reports/html/assets/imgs/{img_name}.webp", quality=50)
        return f"../../html/assets/imgs/{img_name}.webp"
    else:
        images_folder = img.filename.split(os.sep)[-2]
        return f"../../../screenshots/{images_folder}/{img_name}.png"


def parse_url_params(url, params):
    """
    Parse url params.
    """
    for idx, param in enumerate(params):
        if idx == 0:
            url += f"?{param}={params[param]}"
        else:
            url += f"&{param}={params[param]}"
    return url


def json_pretty(json_data):
    """
    Format json indent.
    """
    return json.dumps(json_data, indent=4)


def parse_content_type(content):
    """
    Return content type parsed.
    """
    if content is not None:
        if isinstance(content, (list, dict)):
            return json.dumps(content, indent=4)
        if content.startswith('<?xml'):
            dom = xml.dom.minidom.parseString(content)
            return dom.toprettyxml()
    else:
        content = '-'
    return content


def get_short_name(text):
    """
    Return short name from text and replace spanish letter into char compatible with html.
    """
    name = '%.100s' % text
    short_name = replace_chars(name).replace('Ñ', '&Ntilde;').replace('ñ', '&#241;')
    return short_name


def get_doc_pdf_scenario_name(scenario_name, driver, file_type='docx'):

    if file_type == 'docx':
        _docx_path = os.path.join(Settings.REPORTS_PATH.get(force=True), 'doc') + os.sep
        scenario_name = replace_chars('%.100s' % scenario_name)
        docx_path = str(_docx_path) + str(driver).upper() + "-" + scenario_name + ".docx"
        return docx_path
    elif file_type == 'pdf':
        _pdf_path = os.path.join(Settings.REPORTS_PATH.get(force=True), 'pdf') + os.sep
        scenario_name = replace_chars('%.100s' % scenario_name)
        pdf_path = str(_pdf_path) + str(driver).upper() + "-" + replace_chars(
            scenario_name.__str__()) + ".pdf"
        return pdf_path


def attach_html_files():
    if (Settings.PYTALOS_REPORTS.get('generate_html') or
            (
                    Settings.PYTALOS_ALM.get('post_to_alm') and
                    Settings.PYTALOS_ALM.get('attachments').get('html', False)
            )):
        return True
    return False


def attach_docx_files():
    if (Settings.PYTALOS_REPORTS.get('generate_docx') or
            (
                    Settings.PYTALOS_ALM.get('post_to_alm') and
                    Settings.PYTALOS_ALM.get('attachments').get('docx', False)
            )):
        return True
    return False


def attach_pdf_files():
    if (Settings.PYTALOS_REPORTS.get('generate_pdf') or
            (
                    Settings.PYTALOS_ALM.get('post_to_alm') and
                    Settings.PYTALOS_ALM.get('attachments').get('pdf', False)
            )):
        return True
    return False


def format_path_to_attach_html(path_to_format):
    """
    Return path formatted to attach in html.
    """
    return '/'.join([path for path in path_to_format.replace('\\', '/').split('/') if path != ''])
