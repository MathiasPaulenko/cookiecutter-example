"""
Web Generic Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the evidence files.

List of steps:
######################################################################################################################
## Generic Steps:
    access to the web application 'web'
    click on the 'element_type' element by 'by' and locator 'loc'
    type on the 'element_type' element by 'by' and locator 'loc' the text 'text'
    check on the 'element_type' element by 'by' and locator 'loc'
    uncheck on the 'element_type' element by 'by' and locator 'loc'
    clear 'element_type' element by 'by' and locator 'loc'
    choose the 'value' option from the select element by 'by' and locator 'loc'
    choose the option 'value' from the select element by 'by' and locator 'loc'
    choose option with index 'index' from the select element by 'by' and locator 'loc'
    choose the option by text 'text' from the select element by 'by' and locator 'loc'
    deselect all options of a select element by 'by' and locator 'loc'
    deselect the 'value' option from the select element by 'by' and locator 'loc'
    deselect the option with index 'i' from the select element by 'by' and locator 'loc'
    deselect the option by text 'text' from the select element by 'by' and locator 'loc'
    click on the button containing 'name'
    click on the button with text 'text'
    click on the link containing 'name'
    click on the link with text 'text'
    click on the 'btn1' button to the left of the 'btn2' button
    click on the 'btn1' button to the right of the 'btn2' button
    type on the field with placeholder contains 'placeholder' the value 'value'
    type on the element with placeholder contains 'placeholder' the value 'value'
    (|native |js )clean the element with label contains 'text'
    (|native |js )clean the field with label contains 'text'
    switch to tab with index 'index'
    close parent tab

## Data Steps:
    save in the context 'name' the element text 'e' by 'by' and locator 'loc'
    save in the context 'name' the select element current value by 'by' and locator 'loc'
    save in the context 'name' all options of a select element by 'by' and locator 'loc'
    save in the context 'name' options selected of a select element by 'by' and locator 'loc'
    scroll to the 'element_type' element by 'by' with locator 'loc'
    save in context 'name' the attribute 'att' of element 'text' by 'by' and locator 'loc'

## Verification Steps
    verify element 'element_type' by 'by' and locate 'loc' text is 'value'
    verify element 'element_type' by 'by' and locate 'loc' text contains 'value'
    verify element 'element_type' by 'by' and locate 'loc' is present'
    verify element 'element_type' by 'by' and locate 'loc' is visible'
    verify the current url is 'url'
    verify element containing 'text' is present'
    verify field containing 'text' is present'
    verify element containing 'text' is not present'
    verify field containing 'text' is not present'
    verify link containing 'text' is present'
    verify link containing 'text' is not present'
    verify button containing 'text' is present'
    verify button containing 'text' is not present'

## Wait Steps
    wait until the element 'element_type' by 'by' with locator 'loc' is visible
    wait until the element 'element_type' by 'by' with locator 'loc' is not visible
    wait until the element 'element_type' by 'by' with locator 'loc' is clickable
    do an implicit wait of 'seconds' seconds
    wait until the element 'element_type' by 'by' with locator 'loc' is present
    wait until the element 'element_type' by 'by' with locator 'loc' stops
    wait until the element 'text' by 'by' with locator 'loc' contain text 'text'
    wait until the element 'text' by 'by' with locator 'loc' not contain text 'text'
    wait until element 'text' by 'b' with locator 'loc' attribute 'att' is 'value'
    wait presence of the element by 'by' with locator 'loc'
    wait until frame element by 'by' with locator 'loc' is available and switch to it
    wait until the title is 'title'
    wait until the title contains 'title'
    wait until alert is present

######################################################################################################################
"""
from behave import use_step_matcher, step
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from arc.contrib.web.utils import get_element
from arc.page_elements import Button, Group, Link, InputText
from arc.settings.settings_manager import Settings

use_step_matcher("re")

if Settings.PYTALOS_RUN.get('default_steps_options', default=False):
    IS_HIGHLIGHT = Settings.PYTALOS_RUN.get('default_steps_options').get('element_highlight_web', False)
    WAIT = Settings.PYTALOS_RUN.get('default_steps_options').get('wait', 15)
else:
    IS_HIGHLIGHT = False
    WAIT = 15


#######################################################################################################################
#                                            Generic Steps                                                            #
#######################################################################################################################

@step(u"access to the web application '(?P<web>.+)'")
def web_access_to_the_web_application(context, web):
    """
    With this step you access a web application by passing the url as a parameter.
    :example
        Given access to the web application 'https://web.com'
    :
    :tag Web Generic Steps:
    :param context:
    :param web:
    :return:
    """
    context.driver.get(web)

    WebDriverWait(context.driver, WAIT).until(
        ec.presence_of_element_located((By.TAG_NAME, "body"))
    )

    context.runtime.web = web


@step(u"click on the '(?P<element_type>.+)' element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_click_on_element_by_and_loc(context, element_type, by, loc):
    """
    This step clicks a Web element, passing the item type, locator type, and locator through the parameter.
    Allowed elements to check: All except Text and Group
    :example
        When click on the 'button' element by 'xpath' and locator '//*[text()='Click Me']'

    :
    :tag Web Generic Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_clickable()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)

    element.click()


@step(u"type on the '(?P<element_type>.+)' element by '(?P<by>.+)' and locator '(?P<loc>.+)' the text '(?P<text>.+)'")
def web_type_on_element_by_locator_text(context, element_type, by, loc, text):
    """
    This step type a Web element, passing the item type, locator type, and locator through the parameter.
    Allowed elements to check: Input Text
    :example
        When type on the 'input text' element by 'xpath' and locator '//*[@id="input-example"]/input' the text 'hello'

    :
    :tag Web Generic Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :param text:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_clickable()
    element.text = text

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"check on the '(?P<element_type>.+)' element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_check_element_by_locator(context, element_type, by, loc):
    """
    This step check a Web element, passing the item type, locator type, and locator through the parameter.
    Allowed elements to check: checkbox and radius
    :example
        When check on the 'checkbox' element by 'id' and locator 'checkbox-1'

    :
    :tag Web Generic Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.check()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"uncheck on the '(?P<element_type>.+)' element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_uncheck_on_element_by_locator(context, element_type, by, loc):
    """
    This step uncheck a Web element, passing the item type, locator type, and locator through the parameter.
    Allowed elements to check: checkbox
    :example
        When uncheck on the 'checkbox' element by 'id' and locator 'checkbox-1'

    :
    :tag Web Generic Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.uncheck()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"clear '(?P<element_type>.+)' element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_clear_element_by_locator(context, element_type, by, loc):
    """
    This step clear a Web element, passing the item type, locator type, and locator through the parameter.
    Allowed elements to check: Input Text, Special Group, Specials Select
    :example
        When clear 'input text' element by 'xpath' and locator '//*[@id="firstName"]'

    :
    :tag Web Generic Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.clear()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"choose the '(?P<value>.+)' option from the select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_choose_value_from_select_by_locator(context, value, by, loc):
    """
    This step chooses between the available values of a selection combobox by passing the value to be selected,
    the type of locator and the locator.
    Allowed elements to check: Select
    :example
        When choose the 'value' option from the select element by 'xpath' and locator '//*[@id="select"]'

    :
    :tag Web Generic Steps:
    :param context:
    :param value:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.option(value)

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"choose the option '(?P<v>.+)' from the select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_choose_option_selenium_by_value_by_locator(context, v, by, loc):
    """
    This step chooses between the available values of a selection combobox using selenium
    by passing the value to be selected, the type of locator and the locator.
    Allowed elements to check: Select
    :example
        When choose the option 'value' from the select element by 'xpath' and locator '//*[@id="select"]'

    :
    :tag Web Generic Steps:
    :param context:
    :param v:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.selenium_select().select_by_value(v)

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"choose option with index '(?P<index>.+)' from the select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_choose_option_selenium_by_index_by_locator(context, index, by, loc):
    """
    This step chooses a value from an index of the selection combobox using selenium
    by passing the index to be selected, the type of locator and the locator.
    Allowed elements to check: Select
    :example
        When choose option with index '1' from the select element by 'id' and locator 'select-id'

    :
    :tag Web Generic Steps:
    :param context:
    :param index:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.selenium_select().select_by_index(index)

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"choose the option by text '(?P<text>.+)' from the select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_choose_option_selenium_by_text_by_locator(context, text, by, loc):
    """
    This step chooses a value from a text of the selection combobox using selenium
    by passing the index to be selected, the type of locator and the locator.
    Allowed elements to check: Select
    :example
        When choose the option by text 'option-1' from the select element by 'id' and locator 'select-id'

    :
    :tag Web Generic Steps:
    :param context:
    :param text:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.selenium_select().select_by_visible_text(text)

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"deselect all options of a select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_deselect_all_select_options_by_locator(context, by, loc):
    """
    This step chooses between the available values of a selection combobox using selenium
    by passing the value to be selected, the type of locator and the locator.
    Allowed elements to check: Select
    :example
        When choose the 'value' option by selenium from the select element by 'xpath' and locator '//*[@id="select"]'
        When deselect all options of a select element by 'xpath' and locator '//*[@id="select"]'

    :
    :tag Web Generic Steps:
    :param context:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.selenium_select().deselect_all()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"deselect the '(?P<value>.+)' option from the select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_deselect_by_value_select_by_locator(context, value, by, loc):
    """
    This step deselect between the available values of a selection combobox using selenium
    by passing the value to be selected, the type of locator and the locator.
    Allowed elements to check: Select
    :example
        When deselect the 'value' option from the select element by 'xpath' and locator '//*[@id="select"]'

    :
    :tag Web Generic Steps:
    :param context:
    :param value:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.selenium_select().deselect_by_value(value)

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"deselect the option with index '(?P<i>.+)' from the select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_deselect_option_selenium_by_index_by_locator(context, i, by, loc):
    """
    This step deselect a value from an index of the selection combobox using selenium
    by passing the index to be selected, the type of locator and the locator.
    Allowed elements to check: Select
    :example
        When deselect the option with index '1' from the select element by 'id' and locator 'select-id'

    :
    :tag Web Generic Steps:
    :param context:
    :param i:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.selenium_select().deselect_by_index(i)

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"deselect the option by text '(?P<text>.+)' from the select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_deselect_option_selenium_by_text_by_locator(context, text, by, loc):
    """
    This step deselect a value from a text of the selection combobox using selenium
    by passing the index to be selected, the type of locator and the locator.
    Allowed elements to check: Select
    :example
        When deselect the option by text 'option-1' from the select element by 'id' and locator 'select-id'
    :
    :tag Web Generic Steps:
    :param context:
    :param text:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    element.wait_until_clickable()
    element.selenium_select().deselect_by_visible_text(text)

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"click on the button containing '(?P<name>.+)'")
def web_click_on_the_button_containing(context, name):
    """
    This step clicks on the button-type element containing the text passed by parameter.
    :example
        When click on the button containing 'submit'
    :
    :tag Web Generic Steps:
    :param context:
    :param name:
    :return:
    """
    element = Button(By.XPATH, f"//button[contains(text(),'{name}')]")
    element.wait_until_clickable()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)

    element.click()


@step(u"click on the button with text '(?P<text>.+)'")
def web_click_on_the_button_with_text(context, text):
    """
    This step clicks on the button-type element with the text exactly as it is passed by parameter.
    :example
        When click on the button with text 'submit'
    :
    :tag Web Generic Steps:
    :param context:
    :param text:
    :return:
    """
    element = Button(By.XPATH, f"//button[text()='{text}']")
    element.wait_until_clickable()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)

    element.click()


@step(u"click on the link containing '(?P<name>.+)'")
def web_click_on_the_link_containing(context, name):
    """
    This step clicks on the link-type element containing the text passed by parameter.
    :example
        When click on the link containing 'subscribe'
    :
    :tag Web Generic Steps:
    :param context:
    :param name:
    :return:
    """
    element = Link(By.XPATH, f"//a[contains(text(),'{name}')]")
    element.wait_until_clickable()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)

    element.click()


@step(u"click on the link with text '(?P<text>.+)'")
def web_click_on_the_link_with_text(context, text):
    """
    This step clicks on the link-type element with the text exactly as it is passed by parameter.
    :example
        When click on the link with text 'created'
    :
    :tag Web Generic Steps:
    :param context:
    :param text:
    :return:
    """
    element = Link(By.XPATH, f"//a[text()='{text}']")
    element.wait_until_clickable()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)

    element.click()


@step(u"click on the '(?P<btn1>.+)' button to the left of the '(?P<btn2>.+)' button")
def web_click_on_the_button_to_the_left_of_the_button(context, btn1, btn2):
    """
    This step clicks on the button to the left of a reference button.
    Both the button by reference and the button to interact are passed to the text they contain.
    :example
        When click on the 'submit' button to the left of the 'reset' button
    :
    :tag Web Generic Steps:
    :param context:
    :param btn1:
    :param btn2:
    :return:
    """
    element = Button(By.XPATH, f"//button[contains(text(),'{btn2}')][1]/preceding::*[contains(text(),'{btn1}')][1]")
    element.wait_until_clickable()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)

    element.click()


@step(u"click on the '(?P<btn1>.+)' button to the right of the '(?P<btn2>.+)' button")
def click_on_the_button_to_the_right_of_the_button(context, btn1, btn2):
    """
    This step clicks on the button to the right of a reference button.
    Both the button by reference and the button to interact are passed to the text they contain.
    :example
        When click on the 'submit' button to the right of the 'reset' button
    :
    :tag Web Generic Steps:
    :param context:
    :param btn1:
    :param btn2:
    :return:
    """
    element = Button(By.XPATH, f"//button[contains(text(),'{btn2}')][1]/following::*[contains(text(),'{btn2}')][1]")
    element.wait_until_clickable()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)

    element.click()


@step(u"type on the field with placeholder contains '(?P<placeholder>.+)' the value '(?P<value>.+)'")
@step(u"type on the element with placeholder contains '(?P<placeholder>.+)' the value '(?P<value>.+)'")
def web_type_on_the_field_element_with_placeholder_contains_the_value(context, placeholder, value):
    """
    This step writes the value passed by parameter in the element or field that has the placeholder attribute equal
    to the text passed by parameter.
    :example
        When type on the element with placeholder contains 'user' the value 'user_value'

        When type on the field with placeholder contains 'user' the value 'user_value'
    :
    :tag Web Generic Steps:
    :param context:
    :param placeholder:
    :param value:
    :return:
    """
    element = InputText(By.XPATH, f"//*[@placeholder='{placeholder}']")
    element.wait_until_visible()
    element.text = value

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"(|native |js )clean the element with label contains '(?P<text>.+)'")
@step(u"(|native |js )clean the field with label contains '(?P<text>.+)'")
def web_clean_the_element_field_with_label_contains(context, option, text):
    """
    This steps cleans the information of an element or field that is located immediately and to the right of its label.
    :example
        When clean the element with label contains 'username'
        When clean the field with label contains 'username'
        When native clean the field with label contains 'username'
        When js clean the element with label contains 'username'

    :
    :tag Web Generic Steps:
    :param context:
    :param option:
    :param text:
    :return:
    """
    element = InputText(
        By.XPATH,
        f"//*[contains(text(),'{text}')]//following::*[self::input or self::textarea][1]"
    )

    element.wait_until_visible()
    element.scroll_element_into_view()
    context.utilities.move_to_element(element)

    if option.strip() == 'native':
        element = context.utilities.convert_to_selenium_element(element)
        element.clear()

    elif option.strip() == 'js':
        element = context.utilities.convert_to_selenium_element(element)
        context.utilities.js_clear(element)

    else:
        element.clear()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"switch to tab with index '(?P<index>.+)'")
def web_switch_to_tab_with_index(context, index):
    """
    This step changes to the browser tab according to the index that is passed by parameter. The index must be a number
    and be consistent with the number of current open tabs.
    :example
        Then switch to tab with index '2'
    :
    :tag Web Generic Steps:
    :param context:
    :param index:
    :return:
    """
    context.driver.switch_to.window(context.driver.window_handles[int(index)])


@step(u"close parent tab")
def web_close_parent_tab(context):
    """
    This step closes the parent tab and puts the focus on the next browser tab.
    :example
        Then close parent tab
    :
    :tag Web Generic Steps:
    :param context:
    :return:
    """
    current_window = context.driver.current_window_handle
    new_window = [window for window in context.driver.window_handles if window != current_window][0]
    context.driver.switch_to.window(current_window)
    context.driver.close()
    context.driver.switch_to.window(new_window)


@step(u"scroll to the '(?P<element_type>.+)' element by '(?P<by>.+)' with locator '(?P<loc>.+)'")
def web_scroll_to_the_element_by_with_locator(context, element_type, by, loc):
    """
    With this step you can scroll to an element by passing the type of element, the type of locator and the locator
    :example
        Then scroll to the 'button' element by 'id' with locator 'button-1'

    :
    :tag Web Control Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


#######################################################################################################################
#                                               Data Steps                                                            #
#######################################################################################################################

@step(u"save in the context '(?P<name>.+)' the element text '(?P<e>.+)' by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_save_context_text_element_by_loc(context, name, e, by, loc):
    """
    With this step, you can save the text of an element to a parameter of the context.test object with the name of that
    parameter as an argument. Text is obtained from an element by passing the element type, locator type, and locator.
    :example
        Given save in the context 'test' the element text 'button' by 'id' and locator 'login'

    :
    :tag Web Control Steps:
    :param context:
    :param name:
    :param e:
    :param by:
    :param loc:
    :return:
    """

    element = get_element(context, e, by, loc)
    element.wait_until_visible()
    setattr(context.test, name, element.text)


@step(u"save in the context '(?P<name>.+)' the select element current value by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_save_current_value_select_by_locator(context, name, by, loc):
    """
    With this step, you can save the current value of a select element to a parameter of the context.test object with
    the name of that parameter as an argument. Text is obtained from an element by passing the element type,
    locator type, and locator.
    :example
        Given save in the context 'test' the element text 'button' by 'id' and locator 'username'

    :
    :tag Web Control Steps:
    :param context:
    :param name:
    :param by:
    :param loc:
    :return:
    """

    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    setattr(context.test, name, element.text)


@step(u"save in the context '(?P<name>.+)' all options of a select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def web_save_all_option_select_by_locator(context, name, by, loc):
    """
    With this step, you can save all options of a select element to a parameter of the context.test object with
    the name of that parameter as an argument. Text is obtained from an element by passing the element type,
    locator type, and locator.
    :example
        Given save in the context 'options' all options of a select element by 'id' and locator 'select-element'

    :
    :tag Web Control Steps:
    :param context:
    :param name:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    setattr(context.test, name, element.selenium_select().options())


@step(u"save in the context '(?P<n>.+)' options selected of a select element by '(?P<by>.+)' and locator '(?P<loc>.+)'")
def save_selected_option_select_by_locator(context, n, by, loc):
    """
    With this step, you can save all selected options of a select element to a parameter of the context.test object with
    the name of that parameter as an argument. Text is obtained from an element by passing the element type,
    locator type, and locator.
    :example
        Given save in the context 'options' all options of a select element by 'id' and locator 'select-element'

    :
    :tag Web Control Steps:
    :param context:
    :param n:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, 'select', by, loc)
    element.wait_until_visible()
    setattr(context.test, n, element.selenium_select().all_selected_options())


@step(
    u"save in context '(?P<n>.+)' the attribute '(?P<a>.+)' of element '(?P<t>.+)' by '(?P<by>.+)' "
    u"and locator '(?P<loc>.+)'"
)
def web_save_context_text_element_by_loc(context, n, a, t, by, loc):
    """
    With this step, you can save an attribute value by its name of an element to a parameter of the context.test object
    with the name of that parameter as an argument. Text is obtained from an element by passing the element type,
    locator type, and locator.
    :example
        Given save in context 'att' the attribute 'href' of element 'link' by 'id' and locator 'link-1'

    :
    :tag Web Control Steps:
    :param context:
    :param n:
    :param a:
    :param t:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, t, by, loc)
    element.wait_until_visible()
    setattr(context.test, n, element.get_attribute(a))


#######################################################################################################################
#                                            Verification Steps                                                       #
#######################################################################################################################
@step(u"verify element '(?P<element_type>.+)' by '(?P<by>.+)' and locate '(?P<loc>.+)' text is '(?P<value>.+)'")
def web_verify_element_by_locator_text_is_value(context, element_type, by, loc, value):
    """
    This step verifies that an element passed by parameter has the text also passed by parameter.
    :example
        When verify element 'button' by 'id' and locate 'button-id' text is 'login'

    :
    :tag Web Verification Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :param value:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_visible()
    current = element.text == value
    expected = True

    error_msg = f'The text of the current item is not the same as the expected text.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify element text',
        f"Element text",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)

    assert result, error_msg


@step(u"verify element '(?P<element_type>.+)' by '(?P<by>.+)' and locate '(?P<loc>.+)' text contains '(?P<value>.+)'")
def web_verify_element_by_locator_text_contains_value(context, element_type, by, loc, value):
    """
    This step verifies that an element passed by parameter contains the text also passed by parameter.
    :example
        When verify element 'button' by 'id' and locate 'button-id' text contains 'login'

    :
    :tag Web Verification Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :param value:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_visible()

    current = value in element.text
    expected = True

    error_msg = f'The expected value is not in the current value of the item.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify element text contains',
        f"Element text contains",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)

    assert result, error_msg


@step(u"verify element '(?P<element_type>.+)' by '(?P<by>.+)' and locate '(?P<loc>.+)' is present")
def web_verify_element_by_locator_is_present(context, element_type, by, loc):
    """
    This step verifies that an element passed by parameter is present.
    :example
        When verify element 'button' by 'id' and locate 'button-id' is present

    :
    :tag Web Verification Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_visible()

    error_msg = f'The item is not present on the current page.'

    assert element.is_present() is True, error_msg

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"verify element '(?P<element_type>.+)' by '(?P<by>.+)' and locate '(?P<loc>.+)' is visible")
def web_verify_element_by_locator_is_visible(context, element_type, by, loc):
    """
    This step verifies that an element passed by parameter is visible.
    :example
        When verify element 'button' by 'id' and locate 'button-id' is visible

    :
    :tag Web Verification Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_visible()

    error_msg = f'The item is not visible on the current page.'
    assert element.is_visible() is True, error_msg

    if IS_HIGHLIGHT:
        context.utilities.highlight_element(element)


@step(u"verify the current url is '(?P<url>.+)'")
def web_verify_the_current_url_is(context, url):
    """
    This step checks if the current url is the one passed by parameter.
    :example
        When verify the current url is 'www.santander.com'

    :
    :tag Web Verification Steps:
    :param context:
    :param url:
    :return:
    """
    current_url = context.driver.current_url
    error_msg = 'The current URL is not the expected URL.'
    context.func.evidences.add_unit_table(
        'URL Verification',
        'Expected URL in current URL',
        current_url,
        url,
        url in current_url,
        error_msg=error_msg
    )

    assert url in current_url, error_msg


@step(u"verify element containing '(?P<text>.+)' is present")
@step(u"verify field containing '(?P<text>.+)' is present")
def web_verify_element_field_containing_is_present(context, text):
    """
    This step verifies that an element or field containing text passed by parameter is currently present on the page.
    :example
        When verify field containing 'username' is present
        When verify element containing 'login' is present

    :
    :tag Web Verification Steps:
    :param context:
    :param text:
    :return:
    """
    loc = f"//*[contains(text(),'{text}')]"
    element = Group(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'The element is not present.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify element is present',
        f"Element",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify element containing '(?P<text>.+)' is not present")
@step(u"verify field containing '(?P<text>.+)' is not present")
def web_verify_element_field_containing_is_not_present(context, text):
    """
    This step verifies that an element or field containing text passed by parameter is NOT currently
    present on the page.
    :example
        When verify field containing 'username' is not present
        When verify element containing 'login' is not present

    :
    :tag Web Verification Steps:
    :param context:
    :param text:
    :return:
    """
    loc = f"//*[contains(text(),'{text}')]"
    element = Button(By.XPATH, loc)

    try:
        element.wait_until_visible()
        element.scroll_element_into_view()
        current = element.is_present()

    except (Exception,):
        current = True

    expected = True
    error_msg = f'The element is not enabled.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify element is present',
        f"Element",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify link containing '(?P<text>.+)' is present")
def web_verify_link_containing_is_present(context, text):
    """
    This step checks if a link containing the text passed by parameter is present on the current page.
    :example
        When verify link containing 'see more' is present

    :
    :tag Web Verification Steps:
    :param context:
    :param text:
    :return:
    """
    loc = f"//a[contains(text(),'{text}')]"
    element = Link(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'The link is not present.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify link is present',
        f"Link",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify link containing '(?P<text>.+)' is not present")
def web_verify_link_containing_is_not_present(context, text):
    """
    This step checks if a link containing the text passed by parameter is NOT present on the current page.
    :example
       When verify link containing 'see more' is not present

    :
    :tag Web Verification Steps:
    :param context:
    :param text:
    :return:
    """
    loc = f"//a[contains(text(),'{text}')]"
    element = Link(By.XPATH, loc)

    try:
        element.wait_until_visible()
        element.scroll_element_into_view()
        current = element.is_present()

    except (Exception,):
        current = True

    expected = True
    error_msg = f'The link is not present.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify link is present',
        f"Link",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify button containing '(?P<text>.+)' is present")
def web_verify_button_containing_is_present(context, text):
    """
    This step checks if a button containing the text passed by parameter is present on the current page.
    :example
        When verify link containing 'see more' is present

    :
    :tag Web Verification Steps:
    :param context:
    :param text:
    :return:
    """
    loc = f"//button[contains(text(),'{text}')]"
    element = Button(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'The button is not present.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify button is present',
        f"Button",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify button containing '(?P<text>.+)' is not present")
def web_verify_button_containing_is_not_present(context, text):
    """
    This step checks if a button containing the text passed by parameter is NOT present on the current page.
    :example
        When verify link containing 'see more' is present

    :
    :tag Web Verification Steps:
    :param context:
    :param text:
    :return:
    """
    loc = f"//button[contains(text(),'{text}')]"
    element = Button(By.XPATH, loc)

    try:
        element.wait_until_visible()
        element.scroll_element_into_view()
        current = element.is_present()

    except (Exception,):
        current = True

    expected = True
    error_msg = f'The button is not present.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify button is present',
        f"Button",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


#######################################################################################################################
#                                            Wait Steps                                                             #
#######################################################################################################################
@step(u"wait until the element '(?P<element_type>.+)' by '(?P<by>.+)' with locator '(?P<loc>.+)' is visible")
def web_wait_until_element_by_locator_is_visible(context, element_type, by, loc):
    """
    With this step, you wait until an element specified by parameter is visible.
    :example
        Then wait until the element 'button' by 'id' with locator 'button-1' is visible
    :
    :tag Web Wait Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_visible()


@step(u"wait until the element '(?P<element_type>.+)' by '(?P<by>.+)' with locator '(?P<loc>.+)' is not visible")
def web_wait_until_element_by_locator_is_not_visible(context, element_type, by, loc):
    """
    With this step, you wait until an element specified by parameter is not visible.
    :example
        Then wait until the element 'button' by 'id' with locator 'button-1' is not visible
    :
    :tag Web Wait Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_not_visible()


@step(u"wait until the element '(?P<element_type>.+)' by '(?P<by>.+)' with locator '(?P<loc>.+)' is clickable")
def web_wait_until_element_by_locator_is_clickable(context, element_type, by, loc):
    """
    With this step, you wait until an element specified by parameter is clickable.
    :example
        Then wait until the element 'button' by 'id' with locator 'button-1' is clickable
    :
    :tag Web Wait Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    element.wait_until_clickable()


@step(u"do an implicit wait of '(?P<seconds>.+)' seconds")
def web_wait_until_element_by_locator_is_clickable(context, seconds):
    """
    This steps performs an implicit wait for the seconds that are passed to it by parameters.
    :example
        Then do an implicit wait of '10' seconds
    :

    :tag Web Wait Steps:
    :param context:
    :param seconds
    :return:
    """
    context.driver.implicitly_wait(int(seconds))


@step(u"wait until the element '(?P<element_type>.+)' by '(?P<by>.+)' with locator '(?P<loc>.+)' is present")
def web_wait_until_element_by_locator_is_present(context, element_type, by, loc):
    """
    With this step, you wait until an element specified by parameter is present.
    :example
        Then wait until the element 'button' by 'id' with locator 'button-1' is present
    :
    :tag Web Wait Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    context.utilities.wait_until_element_present(element=element, timeout=WAIT)


@step(u"wait until the element '(?P<element_type>.+)' by '(?P<by>.+)' with locator '(?P<loc>.+)' stops")
def web_wait_until_element_by_locator_stops(context, element_type, by, loc):
    """
    With this step, you wait until an element specified by parameter stops.
    :example
        Then wait until the element 'button' by 'id' with locator 'button-1' stops
    :
    :tag Web Wait Steps:
    :param context:
    :param element_type:
    :param by:
    :param loc:
    :return:
    """
    element = get_element(context, element_type, by, loc)
    context.utilities.wait_until_element_stops(element=element, timeout=WAIT)


@step(u"wait until the element '(?P<t>.+)' by '(?P<by>.+)' with locator '(?P<loc>.+)' contain text '(?P<text>.+)'")
def web_wait_until_element_by_locator_contain_text(context, t, by, loc, text):
    """
    With this step, you wait until an element specified by parameter contain text.
    :example
        Then wait until the element 'button' by 'id' with locator 'button-1' contain text 'login'
    :
    :tag Web Wait Steps:
    :param context:
    :param t:
    :param by:
    :param loc:
    :param text:
    :return:
    """
    element = get_element(context, t, by, loc)
    context.utilities.wait_until_element_contains_text(element=element, text=text, timeout=WAIT)


@step(u"wait until the element '(?P<t>.+)' by '(?P<by>.+)' with locator '(?P<loc>.+)' not contain text '(?P<text>.+)'")
def web_wait_until_element_by_locator_not_contain_text(context, t, by, loc, text):
    """
    With this step, you wait until an element specified by parameter not contain text.
    :example
        Then wait until the element 'button' by 'id' with locator 'button-1' contain text 'login'
    :
    :tag Web Wait Steps:
    :param context:
    :param t:
    :param by:
    :param loc:
    :param text:
    :return:
    """
    element = get_element(context, t, by, loc)
    context.utilities.wait_until_element_not_contain_text(element=element, text=text, timeout=WAIT)


@step(u"wait until element '(?P<t>.+)' by '(?P<b>.+)' with locator '(?P<loc>.+)' attribute '(?P<a>.+)' is '(?P<v>.+)'")
def web_wait_until_element_by_locator_att_value(context, t, b, loc, a, v):
    """
    With this step, you wait until an element specified by parameter attribute is a specific value.
    :example
        Then wait until element 'button' by 'id' with locator 'button-1' attribute 'href' is '#anchor-1'
    :
    :tag Web Wait Steps:
    :param context:
    :param t:
    :param b:
    :param loc:
    :param a:
    :param v:
    :return:
    """
    element = get_element(context, t, b, loc)
    context.utilities.wait_until_element_attribute_is(
        element=element, timeout=WAIT,
        attribute=a, value=v
    )


@step(u"wait presence of the element by '(?P<by>.+)' with locator '(?P<loc>.+)'")
def web_wait_presence_element_by_locator(context, by, loc):
    """
    With this step, you wait the presence of an element specified by parameter.
    :example
        Then wait presence of the element by 'id' with locator 'button-1'
    :
    :tag Web Wait Steps:
    :param context:
    :param by:
    :param loc:
    :return:
    """
    context.utilities.wait_presence_of_element_located(
        driver=context.driver, by=by, locator=loc, delay=WAIT
    )


@step(u"wait until frame element by '(?P<by>.+)' with locator '(?P<loc>.+)' is available and switch to it")
def web_wait_until_frame_by_locator_is_available_switch_it(context, by, loc):
    """
    With this step, you wait until frame element specified by parameter is available and then, switch to it.
    :example
        Then wait until frame element by 'id' with locator 'frame-id' is available and switch to it
    :
    :tag Web Wait Steps:
    :param context:
    :param by:
    :param loc:
    :return:
    """
    context.utilities.wait_frame_to_be_available_and_switch_to_it(
        driver=context.driver, by=by, locator=loc, delay=WAIT
    )


@step(u"wait until the title is '(?P<title>.+)'")
def web_wait_until_frame_by_locator_is_available_switch_it(context, title):
    """
    With this step, you wait until the title is the passed value of the parameter.
    :example
        Then wait until the title is 'hello word'
    :
    :tag Web Wait Steps:
    :param context:
    :param title:
    :return:
    """
    context.utilities.wait_until_title_is(context.driver, title, delay=WAIT)


@step(u"wait until the title contains '(?P<title>.+)'")
def web_wait_until_frame_by_locator_is_available_switch_it(context, title):
    """
    With this step, you wait until the title contains the passed value of the parameter.
    :example
        Then wait until the title contains 'hello'
    :
    :tag Web Wait Steps:
    :param context:
    :param title:
    :return:
    """
    context.utilities.wait_until_title_is(context.driver, title, delay=WAIT)


@step(u"wait until alert is present")
def web_wait_until_frame_by_locator_is_available_switch_it(context):
    """
    With this step, you wait until any alert is present.
    :example
        Then wait until alert is present
    :
    :tag Web Wait Steps:
    :param context:
    :return:
    """
    context.utilities.wait_until_alert_is_present(context.driver, delay=WAIT)
