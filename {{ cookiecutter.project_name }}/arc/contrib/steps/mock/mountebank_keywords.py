"""
Mountebank Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.

List of steps:
######################################################################################################################
start service mountebank {url} {imposter_protocol} {imposter_name}
stop service mountebank
create a service with a specific imposter with absolute path {imposter}
create a service with a unify imposter
delete all running imposters
delete the stub with index {index}
get imposter info
overwrite the running imposter with {imposter_dict}
overwrite the stub with index {index} with the information {stub_dict}
overwrite all the stubs with the information {stub_dict}
create a new stub with information {stub_dict}
######################################################################################################################
"""

from behave import use_step_matcher, step
from arc.talos_virtual.core.context import TalosVirtual
from arc.talos_virtual.core.contrib.mountebank.mountebank import MountebankWrapper
from arc.talos_virtual.core.env_utils import create_dict_imposter

use_step_matcher("re")


@step("start service mountebank '(?P<url>.+)' '(?P<imposter_protocol>.+)' '(?P<imposter_name>.+)'")
def start_mountebank(context, url, imposter_protocol, imposter_name):
    """
    Start a mountebank service
    :example
        When start service mountebank '127.0.0.1' 'http' 'test'
    :
    :param context:
    :param url:
    :param imposter_protocol:
    :param imposter_name:
    """
    if hasattr(context, 'talosvirtual') is False:
        context.talosvirtual = TalosVirtual(context)
        context.talosvirtual.mountebank = MountebankWrapper(url=url, imposter_protocol=imposter_protocol,
                                                            imposter_name=imposter_name)
        context.talosvirtual.mountebank.start_process()


@step("stop service mountebank")
def stop_mountebank(context):
    """
    Stop a mountebank service
    :example
        When stop service mountebank
    :
    :param context:
    """
    context.talosvirtual.mountebank.stop_process()


@step("create a service with a specific imposter with absolute path '(?P<imposter>.+)'")
def create_specific_imposter(context, imposter):
    """
    Create an imposter, given the absolute path, in mountebank service
    :example
        When create a service with a specific imposter with absolute path 'input'imposter.json'
    :
    :param context:
    :param imposter:
    """
    create_dict_imposter(context, imposter)
    context.talosvirtual.mountebank.create_imposter(dict_imposter=context.talosvirtual.mountebank.dict_imposter)


@step("create a service with a unify imposter")
def create_unify_imposter(context):
    """
    unify all the imposter stored in input path and create in mountebank service an unique imposter
    :example
        When create a service with a unify imposter
    :
    :param context:
    """
    create_dict_imposter(context)
    context.talosvirtual.mountebank.create_imposter(dict_imposter=context.talosvirtual.mountebank.dict_imposter)


@step("delete all running imposters")
def delete_all_imposters(context):
    """
    Delete all the imposters running in mountebank service
    :example
        When delete all running imposters
    :
    :param context:
    """
    context.talosvirtual.mountebank.delete_all_imposter()


@step("delete the stub with index '(?P<index>.+)'")
def delete_stub(context, index):
    """
    Delete a stub of an imposter running in mountebank service
    :example
        When delete the stub with index '1'
    :
    :param context:
    :param index:
    """
    context.talosvirtual.mountebank.delete_stub_imposter(context.talosvirtual.mountebank.imposter_port, index)


@step("get imposter info")
def get_imposter(context):
    """
    Get a dict with the imposter information running in mountebank service
    :example
        When get imposter info
    :
    :param context:
    """
    context.runtime.imposter = context.talosvirtual.mountebank.get_imposter(context.talosvirtual.mountebank.imposter_port)


@step("overwrite the running imposter with '(?P<imposter_dict>.+)'")
def overwrite_imposter(context, imposter_dict):
    """
    Overwrite a running imposter with another given by argument
    :example
        When overwrite the running imposter with '<imposter dict>'
    :
    :param context:
    :param imposter_dict:
    """
    context.talosvirtual.mountebank.overwrite_imposter(imposter_dict)


@step("overwrite the stub with index '(?P<index>.+)' with the information '(?P<stub_dict>.+)'")
def overwrite_stub(context, index, stub_dict):
    """
    Overwrite a stub of an imposter running with another given by argument
    :example
        When overwrite the stub with index '4' with the information '<stub_dict>'
    :
    :param context:
    :param index:
    :param stub_dict:
    """
    context.talosvirtual.mountebank.overwrite_stub(context.talosvirtual.mountebank.imposter_port, index, stub_dict)


@step("overwrite all the stubs with the information '(?P<stub_dict>.+)'")
def overwrite_all_stubs(context, stub_dict):
    """
    Overwrite all the stubs with  another given by argument
    :example
        When overwrite all the stubs with the information '<stub_dict>'
    :
    :param context:
    :param stub_dict:
    """
    context.talosvirtual.mountebank.overwrite_all_stubs(context.talosvirtual.mountebank.imposter_port, stub_dict)


@step("create a new stub with information '(?P<stub_dict>.+)'")
def create_stub(context, stub_dict):
    """
    Create a new stub in a imposter running in mountebank service
    :example
        When create a new stub with information '<stub_dict>'
    :
    :param context:
    :param stub_dict:
    """
    context.talosvirtual.mountebank.create_stub_imposter(context.talosvirtual.mountebank.imposter_port, stub_dict)
