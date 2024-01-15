
class ManagerSettings(object):
    """
    This class allows to get and edit the settings values.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.get())

    def get(self, options=None, force=False, default=False):
        """
        Get the option value separated by .
        Set force to true if you need to get the arc core value
        :param options:
        :param force:
        :param default:
        :return:
        """
        return self._get_setting_value_or_default(self.name, options, force, default)

    def set(self, options, value, force=False):
        """
        This method receives the options in dot separated like environment_proxy.enabled and the value.
        Use force if you want to change the value of the arc settings.
        :param options:
        :param value:
        :param force:
        :return:
        """
        variable = self._get_setting_variable_or_default(self.name, force=force)
        self._set_setting_value(variable, options, value)

    def items(self, force=False):
        """
        Return the list of items.
        Use force to return the arc settings
        :param force:
        :return:
        """
        return self.get(force=force).items()

    @staticmethod
    def _set_setting_variable(variable, value, force=False):
        """
        Set the value of a settings if the given option was none so then the complete variable is changed.
        Example:

        Original value of PYTALOS_STEPS is ['1', '2', '3']

        Settings.PYTALOS_STEPS.set(value=['foo', 'bar'])

        Result of PYTALOS_STEPS will be ['foo', 'bar']
        :param variable:
        :param force:
        :param value:
        :return:
        """
        from arc.settings import settings as pytalos_settings
        try:
            from settings import settings as user_settings
        except (ModuleNotFoundError, ImportError):
            return getattr(pytalos_settings, variable)

        if force:
            setattr(pytalos_settings, variable, value)
        if hasattr(user_settings, variable):
            setattr(user_settings, variable, value)
        if hasattr(pytalos_settings, variable):
            setattr(pytalos_settings, variable, value)

    @staticmethod
    def _get_setting_variable_or_default(variable, force=False):
        """
        Gets the user's configuration variable, if it does not exist, gets the default configuration variable.
        :param variable:
        :param force:
        :return:
        """
        from arc.settings import settings as pytalos_settings

        if force:
            return getattr(pytalos_settings, variable)

        try:
            from settings import settings as user_settings
        except (ModuleNotFoundError, ImportError):
            return getattr(pytalos_settings, variable)

        if hasattr(user_settings, variable):
            return getattr(user_settings, variable)
        if hasattr(pytalos_settings, variable):
            return getattr(pytalos_settings, variable)
        return None

    def _get_setting_value_or_default(self, variable, option, force=False, default=False):
        """
        Get the value of a configuration by passing the variable name and the path to the option separated by dots.
        :param variable:
        :param option:
        :param force:
        :param default:
        :return:
        """
        variable = self._get_setting_variable_or_default(variable, force)
        from copy import deepcopy
        variable_axu = deepcopy(variable)
        if variable and option:
            options = option.split('.')
            for op in options:
                if op in variable_axu:
                    variable_axu = variable_axu[op]
                else:
                    # Option not in dictionary, set to none and break
                    variable_axu = None
                    break
        elif variable and not option:
            return variable_axu

        # If the value is none and Force is True, then return default
        if variable_axu is None and force is True:
            return default
        elif variable_axu is None:
            # Value is none, but we didn't try to get the core value
            return self.get(options=option, force=True)
        else:
            if isinstance(variable, dict) and len(variable) == 0:
                return self.get(options=option, force=True)
            return variable_axu

    def _set_setting_value(self, variable, option, value):
        """
        Set the value of a configuration by passing the variable name and the path to the option separated by dots.
        :param variable:
        :param option:
        :param value:
        """
        if variable and option:
            options = option.split('.')
            if len(options) > 1:
                _variable_aux = variable
                for op in options:
                    if _variable_aux.get(op, None) is not None:
                        if op == options[-1]:
                            _variable_aux[op] = value
                        else:
                            _variable_aux = variable[op]
            else:
                variable[option] = value
        else:
            self._set_setting_variable(self.name, value)


class Settings(object):
    """
    Class used to access to the settings variable values using get and set.
    """

    # Paths

    BASE_PATH = ManagerSettings("BASE_PATH")
    SETTINGS_PATH = ManagerSettings("SETTINGS_PATH")
    INTEGRATIONS_PATH = ManagerSettings("INTEGRATIONS_PATH")
    OUTPUT_PATH = ManagerSettings("OUTPUT_PATH")
    TEST_PATH = ManagerSettings("TEST_PATH")
    REPORTS_PATH = ManagerSettings("REPORTS_PATH")
    DRIVERS_HOME = ManagerSettings("DRIVERS_HOME")
    ARC_PATH = ManagerSettings("ARC_PATH")
    RESOURCES_PATH = ManagerSettings("RESOURCES_PATH")
    HELPERS_PATH = ManagerSettings("HELPERS_PATH")
    LOCALE_PATH = ManagerSettings("LOCALE_PATH")
    CONF_PATH = ManagerSettings("CONF_PATH")
    PROFILES_PATH = ManagerSettings("PROFILES_PATH")
    VS_MIDDLEWARE = ManagerSettings("VS_MIDDLEWARE")
    REPOSITORIES = ManagerSettings("REPOSITORIES")
    USER_RESOURCES_PATH = ManagerSettings("USER_RESOURCES_PATH")

    # User settings

    PROJECT_INFO = ManagerSettings("PROJECT_INFO")
    PROXY = ManagerSettings("PROXY")
    LOG_FORMAT_COMPLETE = ManagerSettings("LOG_FORMAT_COMPLETE")
    LOG_FORMAT_LARGE = ManagerSettings("LOG_FORMAT_LARGE")
    LOG_FORMAT_MEDIUM = ManagerSettings("LOG_FORMAT_MEDIUM")
    LOG_FORMAT_SHORT = ManagerSettings("LOG_FORMAT_SHORT")
    PYTALOS_GENERAL = ManagerSettings("PYTALOS_GENERAL")
    PYTALOS_RUN = ManagerSettings("PYTALOS_RUN")
    PYTALOS_STEPS = ManagerSettings("PYTALOS_STEPS")
    PYTALOS_REPORTS = ManagerSettings("PYTALOS_REPORTS")
    PYTALOS_PROFILES = ManagerSettings("PYTALOS_PROFILES")
    PYTALOS_CATALOG = ManagerSettings("PYTALOS_CATALOG")
    PYTALOS_ACCESSIBILITY = ManagerSettings("PYTALOS_ACCESSIBILITY")
    PYTALOS_ALM = ManagerSettings("PYTALOS_ALM")
    PYTALOS_JIRA = ManagerSettings("PYTALOS_JIRA")
    PYTALOS_OCTANE = ManagerSettings("PYTALOS_OCTANE")
    PYTALOS_WEB = ManagerSettings("PYTALOS_WEB")
    BEHAVE = ManagerSettings("BEHAVE")
    SQLITE = ManagerSettings("SQLITE")
    ORACLE = ManagerSettings("ORACLE")
    TALOS_VIRTUAL = ManagerSettings("TALOS_VIRTUAL")
    VISUAL_TESTING = ManagerSettings("VISUAL_TESTING")
    PYTALOS_IA = ManagerSettings("PYTALOS_IA")