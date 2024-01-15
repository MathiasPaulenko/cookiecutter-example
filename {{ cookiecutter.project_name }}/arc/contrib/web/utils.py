# -*- coding: utf-8 -*-
"""
Functionalities utilities oriented to functional web automation with TalosBDD.
"""
import logging

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from arc.page_elements import Button
from arc.settings.settings_manager import Settings

logger = logging.getLogger(__name__)


def get_element(context, element_type, by, loc):
    """
    returns a Page Element object by passing the element type of the following list, the locator type
    (xpath, id...) and the corresponding locator parameter.

    Elements type:
    =================
    button -> Button,
    buttons -> Buttons,
    checkbox -> Checkbox,
    checkboxes -> Checkboxes,
    group -> Group,
    groups -> Groups,
    inputradio -> InputRadio,
    inputradios -> InputRadios,
    inputtext -> InputText,
    inputtexts -> InputTexts,
    link -> Link,
    links -> Links,
    select -> Select,
    selects -> Selects,
    text -> Text,
    texts -> Texts,
    layer -> Layer,
    layers -> Layers

    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return PageElement:
    """
    if Settings.PYTALOS_RUN.get('default_steps_options', default=False):
        wait = Settings.PYTALOS_RUN.get('default_steps_options').get('wait', 15)
    else:
        wait = 15

    page_elements = context.utilities.get_page_elements()
    element_type = element_type.lower().replace(' ', '')
    page_element = page_elements[element_type]
    by = context.utilities.get_locator_by(by.lower())
    return page_element(by, loc, wait=wait)


def click_button_by_xpath(context, xpath, option=''):
    """
    Function to click on a button passing the xpath.
    With the option parameter you can indicate which is the engine of interaction with the element, being the options:
    empty -> PageElement, default option.
    js -> Javascript.
    native -> Selenium.
    :param context:
    :param xpath:
    :param option:
    :return:
    """
    element = Button(
        By.XPATH,
        xpath
    )

    element.wait_until_clickable()
    element.scroll_element_into_view()
    context.utilities.move_to_element(element)

    if option.strip() == 'native':
        element = context.utilities.convert_to_selenium_element(element)
        element.click()

    elif option.strip() == 'js':
        element = context.utilities.convert_to_selenium_element(element)
        context.utilities.js_click(element)

    else:
        element.click()


def send_keys_by_options(context, element, value, option=''):
    """
    Function to send keys or fill element passing the xpath.
    With the option parameter you can indicate which is the engine of interaction with the element, being the options:
    empty -> PageElement, default option.
    js -> Javascript.
    native -> Selenium.
    :param context:
    :param element:
    :param value:
    :param option:
    :return:
    """
    if option.strip() == 'native':
        element = context.utilities.convert_to_selenium_element(element)
        element.send_keys(value)
        element.send_keys(Keys.TAB)

    elif option.strip() == 'js':
        element = context.utilities.convert_to_selenium_element(element)
        context.utilities.js_send_keys(element, value)
        element.send_keys(Keys.TAB)

    else:
        element.text = value
        element.text = Keys.TAB


def clear_and_send_keys_by_options(context, element, value, option=''):
    """
    Function to clear and then, send keys or fill element passing the xpath.
    With the option parameter you can indicate which is the engine of interaction with the element, being the options:
    empty -> PageElement, default option.
    js -> Javascript.
    native -> Selenium.
    :param context:
    :param element:
    :param value:
    :param option:
    :return:
    """
    if option.strip() == 'native':
        element = context.utilities.convert_to_selenium_element(element)
        element.clear()
        element.send_keys(value)
        element.send_keys(Keys.TAB)

    elif option.strip() == 'js':
        element = context.utilities.convert_to_selenium_element(element)
        context.utilities.js_clear(element)
        context.utilities.js_send_keys(element, value)
        element.send_keys(Keys.TAB)

    else:
        element.clear()
        element.text = value
        element.text = Keys.TAB
