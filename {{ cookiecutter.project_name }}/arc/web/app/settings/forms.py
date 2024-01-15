from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, IntegerField, FloatField, SelectField, HiddenField
from wtforms.validators import InputRequired

from arc.settings.settings_manager import Settings
from arc.web.app.utils import get_available_profiles
from arc.web.models.models import DataType


class ConfigurationForm(FlaskForm):
    """
    This class allows to create a form for a CFG file.
    """
    custom_sections_inputs = HiddenField(default="{}")
    remove_sections_inputs = HiddenField(default="{}")
    choice_inputs_name_values = {
        'Driver_type': ['chrome', 'firefox', 'iexplorer', 'edge', 'safari', 'opera', 'edgeie', 'ios', 'android', 'api', 'backend', 'host'],
        'Server_type': ['', 'appium', 'perfecto', 'saucelabs'],
        'AppiumCapabilities_platformName': ['uiautomator2', 'XCUITest'],
        'AppiumCapabilities_automationName': ['android', 'iOS']
    }

    @staticmethod
    def prepare_configuration_inputs(section: str, option: str, value):
        """
        This method add dynamic inputs to the form.
        :param section:
        :param option:
        :param value:
        :return:
        """
        input_type = StringField
        data = {
            'label': option.title().replace('_', ' '),
            'name': f"{section}_{option}",
            'default': value
        }
        section_key = f"{section}_{option}"
        if isinstance(value, bool):
            input_type = BooleanField
        elif isinstance(value, int):
            input_type = IntegerField
        elif isinstance(value, float):
            input_type = FloatField
        if section_key in ConfigurationForm.choice_inputs_name_values:
            input_type = SelectField
            data['choices'] = ConfigurationForm.choice_inputs_name_values[section_key]

        return input_type, data


class SettingsForm(FlaskForm):
    """
    This is the form for the Settings used in TalosBDD
    """
    name = StringField('Settings configuration name', validators=[InputRequired()])
    active = BooleanField('Default settings configuration', default=False)
    application = StringField('Application', validators=[InputRequired()])
    business_area = StringField('Business Area', validators=[InputRequired()])
    entity = StringField('Entity', validators=[InputRequired()])
    user_code = StringField('User Code', validators=[InputRequired()])
    http_proxy = StringField('Http Proxy')
    https_proxy = StringField('Https Proxy')
    environment_proxy = BooleanField('Environment Proxy', default=False)
    execution_proxy = BooleanField('Execution Proxy', default=False)
    update_driver = BooleanField('Update Driver', default=False)
    update_driver_use_proxy = BooleanField('Update driver use proxy')
    log_level = StringField('Log level')
    continue_after_failed_step = BooleanField('Continue after failed step')
    autoretry = BooleanField('Auto retry scenario', default=False)
    autoretry_attempts = IntegerField('Auto retry attempts', default=0)
    autoretry_attempts_wait_seconds = IntegerField('Auto retry attempts wait seconds', default=0)
    environment = SelectField('Environment', choices=get_available_profiles())
    language = StringField('Language')
    repositories = BooleanField('Repositories', default=False)
    post_to_alm = BooleanField('Post to ALM', default=False)
    attachments_pdf = BooleanField('Add PDF attachments', default=False)
    attachments_docx = BooleanField('Add DOCX attachments', default=False)
    attachments_html = BooleanField('Add HTML attachments', default=False)
    match_alm_execution = BooleanField('Match ALM execution', default=False)
    alm3_properties = BooleanField('Use ALM 3 Properties', default=False)
    replicate_folder_structure = BooleanField('Replicate folder structure', default=False)
    scenario_name_as_run_name = BooleanField('Scenario name as run name', default=False)
    post_to_jira = BooleanField('Post to Jira', default=False)
    base_url = StringField('Base URL')
    username = StringField('username')
    password = PasswordField('password')
    post_to_octane = BooleanField('Post to Octane', default=False)
    server = StringField('Server')
    client_id = StringField('Client ID')
    secret = StringField('Secret')
    shared_space = StringField('Shared Space')
    workspace = StringField('Work Space')
    web_keywords = BooleanField('Web Keywords')
    api_keywords = BooleanField('Api Keywords')
    accessibility_keywords = BooleanField('Accessibility Keywords')
    android_keywords = BooleanField('Android Keywords')
    oracle_keywords = BooleanField('Oracle Keywords')
    snowflake_keywords = BooleanField('Snowflake Keywords')
    data_keywords = BooleanField('Data Keywords')
    ftp_keywords = BooleanField('FTP Keywords')
    functional_keywords = BooleanField('Functional Keywords')
    mail_keywords = BooleanField('Mail Keywords')
    host_keywords = BooleanField('Host Keywords')
    mountebank_keywords = BooleanField('Mountebank Keywords')
    ssh_keywords = BooleanField('SSH Keywords')
    appian_keywords = BooleanField('Appian Keywords')
    autogui_keywords = BooleanField('Autogui Keywords')

    @staticmethod
    def get_settings_values(settings_values):
        """
        This method return the values of the settings given a SettingsValues query
        Do a for and get the data type, set the value and return a dict with all the data prepared
        to be used in the form.
        :param settings_values:
        :return:
        """
        data = {}
        for settings_value in settings_values:
            if settings_value.data_type == DataType.BOOLEAN:
                if settings_value.value == '0':
                    data[settings_value.name] = False
                else:
                    data[settings_value.name] = True
            else:
                data[settings_value.name] = settings_value.value
        return data

    @staticmethod
    def get_default_values():
        """
        This method return the current values of the file settings.
        :return:
        """
        return {
            'application': Settings.PROJECT_INFO.get('application'),
            'business_area': Settings.PROJECT_INFO.get('business_area'),
            'entity': Settings.PROJECT_INFO.get('entity'),
            'user_code': Settings.PROJECT_INFO.get('user_code'),
            'http_proxy': Settings.PROXY.get('http_proxy'),
            'https_proxy': Settings.PROXY.get('https_proxy'),
            'environment_proxy': Settings.PYTALOS_GENERAL.get('environment_proxy').get('enabled'),
            'execution_proxy': Settings.PYTALOS_RUN.get('execution_proxy').get('enabled'),
            'update_driver': Settings.PYTALOS_GENERAL.get('update_driver').get('enabled_update'),
            'update_driver_use_proxy': Settings.PYTALOS_GENERAL.get('update_driver').get('enable_proxy'),
            'log_level': Settings.PYTALOS_GENERAL.get('logger').get('file_level'),
            'continue_after_failed_step': Settings.PYTALOS_RUN.get('continue_after_failed_step'),
            'autoretry': Settings.PYTALOS_RUN.get('autoretry').get('enabled'),
            'autoretry_attempts': Settings.PYTALOS_RUN.get('autoretry').get('attempts'),
            'autoretry_attempts_wait_seconds': Settings.PYTALOS_RUN.get('autoretry').get('attempts_wait_seconds'),
            'accessibility_keywords': 'arc.contrib.steps.accessibility.accessibility_keywords' in Settings.PYTALOS_STEPS.get(),
            'android_keywords': 'arc.contrib.steps.android.android_keywords' in Settings.PYTALOS_STEPS.get(),
            'api_keywords': 'arc.contrib.steps.api.api_keywords' in Settings.PYTALOS_STEPS.get(),
            'oracle_keywords': 'arc.contrib.steps.db.oracle_keywords' in Settings.PYTALOS_STEPS.get(),
            'snowflake_keywords': 'arc.contrib.steps.db.snowflake_keywords' in Settings.PYTALOS_STEPS.get(),
            'data_keywords': 'arc.contrib.steps.general.data_keywords' in Settings.PYTALOS_STEPS.get(),
            'ftp_keywords': 'arc.contrib.steps.general.ftp_keywords' in Settings.PYTALOS_STEPS.get(),
            'functional_keywords': 'arc.contrib.steps.general.functional_keywords' in Settings.PYTALOS_STEPS.get(),
            'mail_keywords': 'arc.contrib.steps.general.mail_keywords' in Settings.PYTALOS_STEPS.get(),
            'host_keywords': 'arc.contrib.steps.host.host_keywords' in Settings.PYTALOS_STEPS.get(),
            'mountebank_keywords': 'arc.contrib.steps.mock.mountebank_keywords' in Settings.PYTALOS_STEPS.get(),
            'ssh_keywords': 'arc.contrib.steps.services.ssh_keywords' in Settings.PYTALOS_STEPS.get(),
            'appian_keywords': 'arc.contrib.steps.web.appian_keywords' in Settings.PYTALOS_STEPS.get(),
            'web_keywords': 'arc.contrib.steps.web.web_keywords' in Settings.PYTALOS_STEPS.get(),
            'autogui_keywords': 'arc.contrib.steps.gui.autogui_keywords' in Settings.PYTALOS_STEPS.get(),
            'environment': Settings.PYTALOS_PROFILES.get('environment'),
            'language': Settings.PYTALOS_PROFILES.get('language'),
            'repositories': Settings.PYTALOS_PROFILES.get('repositories'),
            'post_to_alm': Settings.PYTALOS_ALM.get('post_to_alm'),
            'attachments_pdf': Settings.PYTALOS_ALM.get('attachments').get('pdf'),
            'attachments_docx': Settings.PYTALOS_ALM.get('attachments').get('docx'),
            'attachments_html': Settings.PYTALOS_ALM.get('attachments').get('html'),
            'match_alm_execution': Settings.PYTALOS_ALM.get('match_alm_execution'),
            'alm3_properties': Settings.PYTALOS_ALM.get('alm3_properties'),
            'replicate_folder_structure': Settings.PYTALOS_ALM.get('replicate_folder_structure'),
            'scenario_name_as_run_name': Settings.PYTALOS_ALM.get('scenario_name_as_run_name'),
            'post_to_jira': Settings.PYTALOS_JIRA.get('post_to_jira'),
            'base_url': Settings.PYTALOS_JIRA.get('base_url'),
            'username': Settings.PYTALOS_JIRA.get('username'),
            'password': Settings.PYTALOS_JIRA.get('password'),
            'post_to_octane': Settings.PYTALOS_OCTANE.get('post_to_octane'),
            'server': Settings.PYTALOS_OCTANE.get('server'),
            'client_id': Settings.PYTALOS_OCTANE.get('client_id'),
            'secret': Settings.PYTALOS_OCTANE.get('secret'),
            'shared_space': Settings.PYTALOS_OCTANE.get('shared_space'),
            'workspace': Settings.PYTALOS_OCTANE.get('workspace'),
        }
