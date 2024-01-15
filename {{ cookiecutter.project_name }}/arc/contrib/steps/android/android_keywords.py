"""
Android Generic Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the evidence files.

List of steps:
######################################################################################################################
## Generic Steps:
    write 'text' to the android element with id 'id_text'
    write 'text' to the android element with resource id 'resources id'

######################################################################################################################
"""
import logging

from appium.webdriver.common.appiumby import AppiumBy
from behave import use_step_matcher, step
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

use_step_matcher("re")
logger = logging.getLogger(__name__)


#######################################################################################################################
#                                            Generic Steps                                                            #
#######################################################################################################################

@step(u"escribir '(?P<text>.+)' en el elemento android de id '(?P<id_text>.+)'")
@step(u"write '(?P<text>.+)' to the android element with id '(?P<id_text>.+)'")
def write_to_the_android_element_with_id(context, text, id_text):
    """
    This Step is used to write in an element with specific id
    :example
        write 'user8' to the android element with id 'sanMe8'
    :
    :tag Android Generic Steps:
    :param context:
    :param text:
    :param id_text:
    :return:
    """
    wait = WebDriverWait(context.driver, 10)
    element = wait.until(ec.presence_of_element_located((AppiumBy.ID, id_text)))
    assert element.is_displayed()
    element.send_keys(text)


@step(u"escribir '(?P<text>.+)' en el elemento android de resource id '(?P<resource_id>.+)'")
@step(u"write '(?P<text>.+)' to the android element with resource id '(?P<resource_id>.+)'")
def write_to_the_android_element_with_resource_id(context, text, resource_id):
    """
    This Step is used to write in an element with specific resource id
    :example
        write 'user8' to the android element with resource id 'sanMe8'
    :
    :tag Android Generic Steps:
    :param context:
    :param text:
    :param resource_id:
    :return:
    """
    wait = WebDriverWait(context.driver, 10)
    element = wait.until(ec.presence_of_element_located((
        AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().resourceId("{resource_id}")')
    ))
    assert element.is_displayed()
    element.send_keys(text)
