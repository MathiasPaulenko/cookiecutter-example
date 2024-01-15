from behave import use_step_matcher, step

from arc.contrib.tools import files

use_step_matcher("re")


# TODO: add descriptions and info for step catalog
#######################################################################################################################
#                                                  Files Steps                                                        #
#######################################################################################################################
@step(u"add to the json file with path '(?P<file_path>.+)' the key '(?P<key>.+)' with the value '(?P<value>.+)'")
def add_to_the_json_file_with_path_the_key_with_value(context, file_path, key, value):
    files.set_value_json_path(file_path, key, value)

    evidence = {
        'File Path': file_path,
        'Key': key,
        'Value': value
    }
    context.func.evidences.add_json('Data Added', evidence)


@step(u"delete to the json file with path '(?P<file_path>.+)' the value with key '(?P<key>.+)'")
def delete_to_the_json_file_with_path_the_value_with_key(context, file_path, key):
    files.delete_value_json_path(file_path, key)
    evidence = {
        'File Path': file_path,
        'Key': key,
    }
    context.func.evidences.add_json('Data Deleted', evidence)


@step(u"add to the yaml file with path '(?P<file_path>.+)' the key '(?P<key>.+)' with the value '(?P<value>.+)'")
def add_to_the_yaml_file_with_path_the_key_with_the_value(context, file_path, key, value):
    files.set_value_yaml_path(file_path, key, value)
    evidence = {
        'File Path': file_path,
        'Key': key,
        'Value': value
    }
    context.func.evidences.add_json('Data Added', evidence)


@step(u"delete to the yaml file with path '(?P<file_path>.+)' the value with key '(?P<key>.+)'")
def delete_to_the_yaml_file_with_path_the_value_with_key(context, file_path, key):
    files.delete_value_yaml_path(file_path, key)
    evidence = {
        'File Path': file_path,
        'Key': key,
    }
    context.func.evidences.add_json('Data Deleted', evidence)


#######################################################################################################################
#                                                  Context Steps                                                      #
#######################################################################################################################
@step(u"add to the context a data dictionary of the yaml file with path '(?P<file_path>.+)'")
def add_to_the_context_a_data_dictionary_of_the_yaml_file_with_path(context, file_path):
    context.runtime.dict_yaml = files.yaml_to_dict(file_path)
    evidence = {
        'File': context.runtime.dict_yaml,
    }
    context.func.evidences.add_json('Data Added', evidence)


@step(u"add to the context a data dictionary of the json file with path '(?P<file_path>.+)'")
def add_to_the_context_a_data_dictionary_of_the_json_file_with_path(context, file_path):
    context.runtime.dict_json = files.json_to_dict(file_path)
    evidence = {
        'File': context.runtime.dict_json,
    }
    context.func.evidences.add_json('Data Added', evidence)


@step(u"add to the context the value of a key path '(?P<key_path>.+)' of the json file with path '(?P<file_path>.+)'")
def add_to_the_context_the_value_of_a_key_path_of_the_json_file_with_path(context, key_path, file_path):
    context.runtime.json_key_path_value = files.get_json_value_key_path(key_path, file_path, sep_char=".")
    evidence = {
        'File': file_path,
        'Key Path': key_path,
        'Data': context.runtime.json_key_path_value
    }
    context.func.evidences.add_json('Data Added', evidence)


@step(u"add to the profiles files '(?P<file_name>.+)' the key '(?P<key>.+)' with the value '(?P<value>.+)'")
def add_to_the_profiles_files_the_key_with_the_value(context, file_name, key, value):
    files.update_data_value(context, 'profiles', file_name, key, value)
    evidence = {
        'File': file_name,
        'Key': key,
        'Data': value
    }
    context.func.evidences.add_json('Data Added', evidence)


@step(u"add to the profiles files '(?P<file_name>.+)' the key '(?P<key>.+)' with the value '(?P<value>.+)' with spread")
def add_to_the_profiles_files_the_key_with_the_value_with_spread(context, file_name, key, value):
    files.update_data_value(context, 'profiles', file_name, key, value)
    evidence = {
        'File': file_name,
        'Key': key,
        'Data': value
    }
    context.func.evidences.add_json('Data Added', evidence)


@step(u"delete to the profiles files '(?P<file_name>.+)' the value with the key '(?P<key>.+)'")
def delete_to_the_profiles_files_the_value_with_the_key(context, file_name, key):
    files.delete_profile_data_value(file_name, key, change_all_profiles=False)
    evidence = {
        'File': file_name,
        'Key': key,
    }
    context.func.evidences.add_json('Data Deleted', evidence)


@step(u"delete to the profiles files '(?P<file_name>.+)' the value with the key '(?P<key>.+)' with spread")
def delete_to_the_profiles_files_the_value_with_the_key_with_spread(context, file_name, key):
    files.delete_profile_data_value(file_name, key, change_all_profiles=True)
    evidence = {
        'File': file_name,
        'Key': key,
    }
    context.func.evidences.add_json('Data Deleted', evidence)
