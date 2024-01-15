import logging
import re
from copy import deepcopy
from colorama import Fore

logger = logging.getLogger(__name__)

# TODO: deprected functions, move to another path.

DEPRECATED_MSG = 'This function is deprecated. Use the new template var with the format ${{file:key}} available.'


class Func:
    context: None

    def __init__(self, context):
        self.context = context

    def get_profile_value_key_path(self, param_path_key, file_name, sep_char: str = "."):
        logger.warning(DEPRECATED_MSG)
        params_list = param_path_key.split(sep_char)
        profiles_datas = self.context.config.userdata['profiles']
        dict_json = profiles_datas[file_name]
        aux_json = deepcopy(dict_json)
        for param in params_list:
            if type(aux_json) is list:
                aux_json = aux_json[int(param)]
            else:
                aux_json = aux_json[param]
        return aux_json

    def get_unique_profile_re_var(self, initial_value, file_name):
        logger.warning(DEPRECATED_MSG)
        if re.match(r"{{(.*?)\}\}", initial_value):
            value = str(initial_value).replace("{{", "").replace("}}", "")
        else:
            value = initial_value

        return self.get_profile_value_key_path(value, file_name)

    @staticmethod
    def is_contains_profile_re_var(initial_value):
        logger.warning(DEPRECATED_MSG)
        if "{{" and "}}" in str(initial_value):
            return True
        else:
            return False

    def get_formatter_multiple_re_var(self, text, file_name):
        logger.warning(DEPRECATED_MSG)
        matchers = re.findall(r"{{(.*?)\}\}", text)

        for match in matchers:
            text = str(text).replace("{{" + match + "}}", str(self.get_profile_value_key_path(match, file_name)))

        return text

    def get_template_var_value(self, template_var, profile_file='master'):
        logger.warning(DEPRECATED_MSG)
        if profile_file == 'master':
            data_file = self.context.runtime.master_file
        else:
            data_file = profile_file

        if self.is_contains_profile_re_var(template_var):
            return self.get_unique_profile_re_var(template_var, data_file)
        else:
            return template_var
