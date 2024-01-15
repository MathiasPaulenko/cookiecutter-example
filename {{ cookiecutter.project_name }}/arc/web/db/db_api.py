import os
import logging

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from arc.core.paths.directories import get_default_steps_path
from arc.core.test_method.exceptions import TalosDatabaseError
from arc.settings.settings_manager import Settings
from arc.web.app.utils import set_setting_value, print_portal_console
from arc.web.main import create_app
from arc.web.models.models import TalosSettings, DataType

logger = logging.getLogger(__name__)


def get_db():
    """
        This function return the engine created for the sqlite database.
        If the database doesn't exist, then create it if the create_database setting is set to true.
    :return:
    """
    from arc.web.config import Config
    db = Config.DATABASE_PATH
    if db_exists(db):
        logger.info(f"DB {db} exist")
        return create_engine(f"{Config.SQLALCHEMY_DATABASE_URI}")
    else:
        logger.info(f"DB {db} doesn't exist")
        if Settings.PYTALOS_WEB.get('create_database', default=False):
            logger.info(f"Creating DB {db}")
            create_app(set_environ=False)
            logger.info(f"DB {db} created. Trying to get engine again")
            return create_engine(f"{Config.SQLALCHEMY_DATABASE_URI}")
        else:
            logger.debug(f"Database with path {db} doesn't exists.")
            raise TalosDatabaseError(f"Database with path {db} doesn't exists.")


def db_exists(path):
    """
        This function only checks if the database file path exist.
    :param path:
    :return:
    """
    logger.info(f"Checking if DB with path {path} exist")
    if os.path.isfile(path):
        return True
    return False


def set_settings_config():
    """
    This function get the default settings configuration and set the values to the different sections.
    :return:
    """
    try:
        engine = get_db()
    except (Exception, ) as e:
        if os.environ.get('EXECUTION_TYPE') == 'Portal':
            print_portal_console(e + '\n')

    with Session(engine) as session:
        settings_values = select(TalosSettings).where(TalosSettings.active == 1)
        for t_setting in session.execute(settings_values):
            _settings = t_setting[0]
            setting_values = {}
            for setting in _settings.setting_values:
                value = setting.value
                if setting.data_type == DataType.BOOLEAN:
                    if setting.value == "1":
                        value = True
                    else:
                        value = False
                setting_values[setting.name] = value
            # PROJECT INFO
            set_setting_value('PROJECT_INFO', 'application', setting_values['application'])
            set_setting_value('PROJECT_INFO', 'business_area', setting_values['business_area'])
            set_setting_value('PROJECT_INFO', 'entity', setting_values['entity'])
            set_setting_value('PROJECT_INFO', 'user_code', setting_values['user_code'])

            # PROXY
            set_setting_value('PROXY', 'http_proxy', setting_values['http_proxy'])
            set_setting_value('PROXY', 'https_proxy', setting_values['https_proxy'])

            # PYTALOS_GENERAL
            set_setting_value('PYTALOS_GENERAL', 'environment_proxy.enabled', setting_values['environment_proxy'])
            set_setting_value('PYTALOS_GENERAL', 'update_driver.enabled_update', setting_values['update_driver'])
            set_setting_value('PYTALOS_GENERAL', 'update_driver.enable_proxy',
                              setting_values['update_driver_use_proxy'])
            set_setting_value('PYTALOS_GENERAL', 'logger.file_level', setting_values['log_level'])

            # PYTALOS_RUN
            set_setting_value('PYTALOS_RUN', 'execution_proxy.enabled', setting_values['execution_proxy'])
            set_setting_value('PYTALOS_RUN', 'continue_after_failed_step', setting_values['continue_after_failed_step'])
            set_setting_value('PYTALOS_RUN', 'autoretry.enabled', setting_values['autoretry'])
            set_setting_value('PYTALOS_RUN', 'autoretry.attempts', setting_values['autoretry_attempts'])
            set_setting_value('PYTALOS_RUN', 'autoretry.attempts_wait_seconds',
                              setting_values['autoretry_attempts_wait_seconds'])

            # PYTALOS_PROFILES
            if Settings.PYTALOS_PROFILES.get('environment') == setting_values['environment']:
                set_setting_value('PYTALOS_PROFILES', 'environment', setting_values['environment'])
            set_setting_value('PYTALOS_PROFILES', 'language', setting_values['language'])
            set_setting_value('PYTALOS_PROFILES', 'repositories', setting_values['repositories'])

            # PYTALOS_ALM
            set_setting_value('PYTALOS_ALM', 'post_to_alm', setting_values['post_to_alm'])
            set_setting_value('PYTALOS_ALM', 'match_alm_execution', setting_values['match_alm_execution'])
            set_setting_value('PYTALOS_ALM', 'alm3_properties', setting_values['alm3_properties'])
            set_setting_value('PYTALOS_ALM', 'replicate_folder_structure', setting_values['replicate_folder_structure'])
            set_setting_value('PYTALOS_ALM', 'scenario_name_as_run_name', setting_values['scenario_name_as_run_name'])
            set_setting_value('PYTALOS_ALM', 'attachments.pdf', setting_values['attachments_pdf'])
            set_setting_value('PYTALOS_ALM', 'attachments.docx', setting_values['attachments_docx'])
            set_setting_value('PYTALOS_ALM', 'attachments.pdf', setting_values['attachments_html'])

            # PYTALOS_JIRA
            set_setting_value('PYTALOS_JIRA', 'post_to_jira', setting_values['post_to_jira'])
            set_setting_value('PYTALOS_JIRA', 'base_url', setting_values['base_url'])
            set_setting_value('PYTALOS_JIRA', 'username', setting_values['username'])
            set_setting_value('PYTALOS_JIRA', 'password', setting_values['password'])

            # PYTALOS_OCTANE
            set_setting_value('PYTALOS_OCTANE', 'post_to_octane', setting_values['post_to_octane'])
            set_setting_value('PYTALOS_OCTANE', 'server', setting_values['server'])
            set_setting_value('PYTALOS_OCTANE', 'client_id', setting_values['client_id'])
            set_setting_value('PYTALOS_OCTANE', 'secret', setting_values['secret'])
            set_setting_value('PYTALOS_OCTANE', 'shared_space', setting_values['shared_space'])
            set_setting_value('PYTALOS_OCTANE', 'workspace', setting_values['workspace'])

            # PYTALOS_STEPS
            _steps_to_import = []
            steps_paths = get_default_steps_path()
            for key, value in steps_paths.items():
                if setting_values.get(key, False):
                    _steps_to_import.append(value)
            Settings.PYTALOS_STEPS.set(options=None, value=_steps_to_import)
