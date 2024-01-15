import json
import os
from os import walk

from arc.settings.settings_manager import Settings


def unify_json(context):
    """
        This function create an imposter from a several imposter files.
    :param context:
    :return:
    """
    input_path = context.talosvirtual.mountebank.input_path
    mb_path = os.path.join(Settings.BASE_PATH.get(force=True), input_path)
    json_imposter = {"port": context.talosvirtual.mountebank.imposter_port,
                     "protocol": context.talosvirtual.mountebank.imposter_protocol,
                     "name": context.talosvirtual.mountebank.imposter_name,
                     "stubs": []}
    for path, dirs, filenames in walk(mb_path):
        for current_file in filenames:
            if os.path.isfile(os.path.join(path + os.sep + current_file)) and current_file.endswith('.json'):
                f = open(path + os.sep + current_file)
                temp_json = json.load(f)
                for stub in temp_json['stubs']:
                    json_imposter['stubs'].append(stub)
    return json_imposter


def create_dict_imposter(context, imposter=None):
    """
        This function creates an impostor from a json file, if the impostor is passed as an argument that impostor
        will be created, otherwise it will unify all impostor files.
    :param context:
    :return:
    """
    if imposter:
        if '.json' in imposter:
            f = open(imposter)
            json_imposter = json.load(f)
            json_imposter['port'] = context.talosvirtual.mountebank.imposter_port
            json_imposter['protocol'] = context.talosvirtual.mountebank.imposter_protocol
            json_imposter['name'] = context.talosvirtual.mountebank.imposter_name
            context.talosvirtual.mountebank.dict_imposter = json_imposter
    else:
        context.talosvirtual.mountebank.dict_imposter = unify_json(context)



