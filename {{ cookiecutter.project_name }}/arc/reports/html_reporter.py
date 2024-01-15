# -*- coding: utf-8 -*-
"""
Module for generating HTML from XML file.
"""
import logging
import os

from junit2htmlreport import runner as junit2html_runner

from arc.reports.html.utils import get_short_name
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)

REPORTS_HOME = os.path.join(Settings.OUTPUT_PATH.get(), 'reports/html') + os.sep


def make_html_reports(path=REPORTS_HOME):
    """
    It converts junit reports into html report and return output paths
    :param path:
    :return:
    """
    if os.path.isdir(path):
        xml_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-4:] == '.xml']
        output = []
        for xml_file_name in xml_list:
            xml_file_renamed = get_short_name(xml_file_name[:-4])
            os.rename(f"{path}{xml_file_name}", f"{path}{xml_file_renamed}.xml")
            _file = f"{path}{xml_file_renamed}.xml"
            new_file = f"{path}{xml_file_renamed}.html"
            junit2html_runner.run([_file, new_file])
            output.append(new_file)

        logger.debug(f'Simple HTML generated in: {output}')
        return output

    else:
        os.stat(path)
        new_path = f"{get_short_name(path[:-4])}.html"
        junit2html_runner.run([path, new_path])
        logger.debug(f'Simple HTML generated in: {new_path}')
        return new_path
