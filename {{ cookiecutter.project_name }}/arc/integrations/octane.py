# -*- coding: utf-8 -*-
"""
Integration module with OCTANE.
It contains all the necessary functions for run the ALM connector.
"""
import logging
import os
from subprocess import call

from arc.integrations.alm import compress_html_report

from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


def run_octane_connect(attach_files):
    """
    Run Octane connect process.
    :return:
    """
    if hasattr(Settings, 'PYTALOS_OCTANE'):
        if Settings.PYTALOS_OCTANE.get('post_to_octane'):
            compress_html_report(attach_files)
            logger.info('Running Octane connect')
            json_path = os.path.join(os.path.abspath("output"), 'reports', 'talos_report.json')
            jar_path = 'arc/resources/talos-connect-6.0.0.jar'
            call(['java', '-jar', jar_path, '-octane', json_path])
            logger.info('Octane connect finished')
