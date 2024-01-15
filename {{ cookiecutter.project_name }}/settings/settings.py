# -*- coding: utf-8 -*-
"""
TalosBDD configuration file.
This file contains all the possible configurations of the core functionalities of TalosBDD.

You can also use this file in order to store configurations of your own test implementations,
adding the variables you require and make use of them by importing this file wherever you need it.

Be careful not to delete or replace any of the configurations already present in this file,
doing any of these actions may cause Talos to fail or not perform its operations correctly.
"""
import os
from pathlib import Path

""" PyTalos configurations """
# Project configurations
BASE_PATH = Path(__file__).absolute().parent.parent
SETTINGS_PATH = os.path.join(BASE_PATH, 'settings')
INTEGRATIONS_PATH = os.path.join(SETTINGS_PATH, 'integrations')
OUTPUT_PATH = os.path.join(BASE_PATH, 'output')
TEST_PATH = os.path.join(BASE_PATH, 'test')
HELPERS_PATH = os.path.join(TEST_PATH, 'helpers')
LOCALE_PATH = os.path.join(BASE_PATH, 'arc/settings/locale')

# PROJECT INFO IS REQUIRED. PLEASE COMPLETE THESE FIELDS WITH THE PROJECT INFORMATION
PROJECT_INFO = {
    'application': '{{ cookiecutter.application }}',  # application being tested
    'business_area': '{{ cookiecutter.business_area }}',  # application business area
    'entity': '{{ cookiecutter.entity }}',  # your department
    'user_code': '{{ cookiecutter.user_code }}'  # your LDAP-ID
}

# Proxy configuration
PROXY = {
    'http_proxy': '',
    'https_proxy': ''
}

# Project and general configuration

LOG_FORMAT_COMPLETE = '%(levelname)-7s - [%(asctime)s] - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s'
LOG_FORMAT_LARGE = '%(levelname)-7s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s'
LOG_FORMAT_MEDIUM = '%(levelname)-7s - %(message)s'
LOG_FORMAT_SHORT = '%(message)s'

PYTALOS_GENERAL = {
    'download_path': "path",  # download path for use in the steps
    'auto_generate_output_dir': True,  # auto generation of output folder
    'auto_generate_test_dir': True,  # auto generation of test folder
    'environment_proxy': {  # activation of environment variable proxy
        'enabled': False,
        'proxy': PROXY
    },
    'update_driver': {  # automatic web driver update
        'enabled_update': False,
        'enable_proxy': False,
        'proxy': PROXY
    },
    'logger': {  # logger configuration
        'file_level': 'DEBUG',  # DEBUG, INFO, WARNING, ERROR
        'console_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
        'format_file': LOG_FORMAT_COMPLETE,
        'format_console': LOG_FORMAT_MEDIUM,
        'date_format': '%Y-%m-%d %H:%M:%S',
        'clear_log': True,
        'disable_console_log': True
    }
}

# Run configuration
PYTALOS_RUN = {
    'close_webdriver': True,  # close webdriver instance after scenario
    'webdriver_detach': True,  # detach chromedriver option
    'close_host': True,  # close host window instance after scenario
    'continue_after_failed_step': False,  # not to stop with step executions if a step fails
    'default_steps_options': {  # default step configuration and options
        "element_highlight_web": False,
        'wait': 30,
    },
    'scenario_outline_annotation_schema': u"{name} -- {row.id} {examples.name}",
    'timeout': {  # timeout for use in steps
        'short': 15,
        'medium': 30,
        'long': 60
    },
    'autoretry': {  # rerun a scenario N times if it fails. where N is the number of attempts
        'enabled': False,
        'attempts': 3,
        'attempts_wait_seconds': 0
    },
    'execution_proxy': {  # configuration of the execution modules (selenium, requests, appium, etc.)
        'enabled': False,
        'proxy': PROXY
    },

}

# Load steps
# The default steps are located in the arc/contrib/steps folder
# The steps inside the test/steps folder are loaded automatically
PYTALOS_STEPS = [
    'arc.contrib.steps.api.api_keywords',
    'arc.contrib.steps.web.web_keywords',
    'arc.contrib.steps.accessibility.accessibility_keywords'
]

# Reports configurations
PYTALOS_REPORTS = {
    'delete_old_reports': True,  # deletes the reports generated in the previous run
    'save_old_reports': {  # generates a compressed file with the contents of the output folder
        'enabled': False,
        'output_path': '',  # absolute path
        'format': 'zip'  # zip, tar, bztar or gztar
    },
    'include_sub_steps_in_results': False,
    'reports_language': 'en_US',  # language of the reports, allowed en_US and es_ES
    'generate_html': True,  # generates html report
    'generate_docx': False,  # generates docx file report
    'generate_pdf': False,  # Warning: PDF generation can be slow, including them in pipelines is not recommended
    'generate_simple_html': False,  # generates simple html report
    'generate_txt': False,  # generates txt file report
    'generate_screenshot': True,  # takes automatic screenshot at the end of each step
    'generate_screenshot_if_failed': False,  # takes automatic screenshot if the step fails
    'compress_screenshot': False,  # compresses the screenshots taken
    'generate_extra_reports': False,  # generates report and file with generic information
    'generate_error_report': {
        'enabled': True,
        'categorization': {
            'enabled': False,
            'tags': []
        }
    },
    'generate_video': {  # generates video reports
        'enabled': False,
        'fps': 5,  # number of images per second of the video
        'video_format': 'mp4'  # mp4 or avi
    }
}

# Profile datas configurations
PYTALOS_PROFILES = {
    'environment': 'cer',  # choose which folder from the profiles to use as environment
    'master_file': 'master',  # choose master file
    'locale_fake_data': 'es_ES',  # set the language of the faker wrapper
    'language': 'es',  # repository files language
    'repositories': True  # activation of data repositories
}

# Step catalog configurations
PYTALOS_CATALOG = {
    'update_step_catalog': False,  # generates excel step catalogue
    'excel_file_name': 'catalog',  # file name of the Excel generated
    'steps': {  # steps that will be in the catalogue
        'user_steps': True,
        'default_api': False,
        'default_web': False,
        'default_appian': False,
        'default_host': False,
        'default_functional': False,
        'default_data': False,
        'default_ftp': False,
        'default_mail': False,
        'default_autogui': False,
    }
}

PYTALOS_ACCESSIBILITY = {
    'automatic_analysis': False,  # Run automatic accessibility analysis by URL change.
    'take_screenshot': False,  # Take screenshot of the web elements
    'highlight_element': False,  # Highlights element when taking a screenshot
    'rules': {  # Run rules only in True
        'wcag2a': True,  # WCAG 2.0 Level A
        'wcag2aa': True,  # WCAG 2.0 Level AA
        'wcag2aaa': False,  # WCAG 2.0 Level AAA
        'wcag21a': False,  # WCAG 2.1 Level A
        'wcag21aa': False,  # WCAG 2.1 Level AA
        'wcag22aa': False,  # WCAG 2.2 Level AA
        'best-practice': False,  # Common accessibility best practices
        'ACT': False,  # W3C approved Accessibility Conformance Testing rules
        'section508': False,  # Old Section 508 rules
        'experimental': False,  # Cutting-edge rules
        'cat': {  # Category mappings which indicates what type of content it is part of
            'aria': True,
            'color': True,
            'forms': True,
            'keyboard': True,
            'name-role-value': True,
            'parsing': True,
            'semantics': True,
            'sensory-and-visual-cues': True,
            'structure': True,
            'tables': True,
            'text-alternatives': True,
            'time-and-media': True,
        },
    }
}

""" Integrations """
# MF ALM integration configurations
PYTALOS_ALM = {
    'post_to_alm': False,  # activation of the ALM connector
    'generate_json': True,  # generation of the json file needed by the connector
    'attachments': {  # chooses which reports are to be attached to the ALM upload
        'pdf': False,
        'docx': True,
        'html': True
    },
    'match_alm_execution': False,  # overwrites the TSs and TCs generated in ALM
    'alm3_properties': False,  # activate this if you are using ALM3
    'replicate_folder_structure': True,  # Deactivate this to use the folder structure indicated in tc-path and ts-path
    # If scenario_name_as_run_name is false then the Run Name in ALM will be Talos_Run_timestamp.
    # If scenario_name_as_run_name is True, then the Run Name will be the name of the executed scenario.
    'scenario_name_as_run_name': False
}

# Jira integration configuration
PYTALOS_JIRA = {
    'post_to_jira': False,  # upload evidence to Jira
    'username': 'user',  # username or mail
    'password': 'pass',  # use decode() function from arc.contrib.tools.crypto.crypto
    'base_url': 'https://jira.alm.europe.cloudcenter.corp',  # Jira url base
    'report': {  # reports to be created in Jira
        'comment_execution': True,
        'upload_doc_evidence': True,
        'upload_txt_evidence': True,
        'upload_html_evidence': True,
        'upload_pdf_evidence': False,
        'upload_log_evidence': False
    },
    'connection_proxy': {  # proxy configuration
        'enabled': False,
        'proxy': PROXY
    }
}

# Octane integration configuration

PYTALOS_OCTANE = {
    'post_to_octane': False,  # upload evidence to Octane
    'server': '',  # server name
    'client_id': '',  # client id
    'secret': '',  # secret key, use decode() function from arc.contrib.tools.crypto.crypto
    'shared_space': '',  # shared space
    'workspace': ''  # workspace name
}

"""" Talos Web Portal"""
PYTALOS_WEB = {
    'debug': False,  # true for activate portal debug
    'port': 5000,  # portal port
    "create_database": True,  # true to create the portal database.
    'save_metrics': True  # true to store run metrics in database
}

""" Behave configurations """
# BEHAVE configuration
BEHAVE = {
    'color': False,
    'junit': True,
    'default_format': 'pretty',
    'show_skipped': False,
    'show_multiline': True,
    'stdout_capture': False,
    'stderr_capture': False,
    'summary': True,
    'show_source': True,
    'show_timings': True,
    'verbose': False,
}

""" BD Configurations"""
# SQLite configuration
SQLITE = {
    'enabled': False,  # activate sqlite3 instance
    'sqlite_home': os.path.join(BASE_PATH, 'db.sqlite3')  # path of sqlite database file
}

ORACLE = {
    'client_path': ''  # Oracle client path
}

TALOS_VIRTUAL = {
    "general": {
        'url': "localhost",
        'input_path': ''
    },
    "mountebank": {
        "enabled": False,
        'imposter_protocol': "http",
        'imposter_name': "automatically",
        'imposter_port': 8080,  # If mountebank is running in a server the port by default is 8080
        'manager_port': 2525  # If mountebank is running in a server the port by default is 2525
    }
}

PYTALOS_IA = {
    'self-healing': {
        'enabled': True,
        'n_neighbors': 3,  # Number of elements similar to the element not found
        'algorithm': 'auto',  # Machine Learning algorithm used for the Nearest Neighbors approach
        'tolerance': 2.5,  # Maximum distance number form the not found element to his neighbors (0.0, ∞)
        'show_result_console': False,  # Prints the result of the self-healing in console
        'tags': [  # Tags to search when scraping the elements of the current page (add necessary tags)
            'a',
            'span',
            'button',
            'input',
            'option',
            'select',
            'textarea',
            'img',
        ]
    }
}
