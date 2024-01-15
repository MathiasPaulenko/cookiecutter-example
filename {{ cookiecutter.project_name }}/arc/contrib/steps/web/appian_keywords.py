# -*- coding: utf-8 -*-
"""
Appian Generic Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the evidence files.

List of steps:
######################################################################################################################
## Actions Steps:
login with the username 'username' and password 'password' in appian
logout in appian
search for 'field' field with 'value'
select the dropdown 'dropdown' with value 'value'
click on record related action 'record'
fill record type user filter 'field' with 'value'
select 'value' value of the 'header' dropdown with default value 'd_value'
go to appian module 'module'
click on appian menu 'menu'

## Generic Steps:
click on the first record of 'name' grid
click on the first record of 'name' table
click on the last record of 'name' grid
click on the last record of 'name' table
click on the first row of column 'column' of 'name' grid
click on the first row of column 'column' of 'name' table
sort record column 'column' from grid 'section'
sort record column 'column' from table 'section'
sort record column index 'index' from grid 'name'
sort record column index 'index' from table 'name'
click on first record of 'name' section
click on record type 'name' and the row 'number'
click on record grid navigation 'page'
sort record grid by column 'column'
click on 'btn' button which is left to button 'reference'
click on 'btn' button which is right to button 'reference'
click on card which contains text as 'text'
click on paragraph which contains text as 'text'
clear record type user filter 'field'
fill 'field' field with 'value'
fill field 'name' in section 'section' with 'value'
click a section 'section' to (expand|collapse)
click on link 'name' from table 'section'
click on link 'name' from section 'section'
click on radio option 'value' for field 'field'
click on radio option 'value'
select the 'heading' checkbox 'label'
click on the first record of 'table' grid which has value 'value'
click on the first record of 'table' table which has value 'value'
fill textarea from section 'section' for the field 'field' with the value 'value'
click on icon of column 'cell' from 'table' table on row 'row'
(|native |js )type in the text field containing 'label' the value 'value'
(|native |js )type in the text area containing 'label' the value 'value'
(|native |js )type in the date field containing 'label' the value 'value'
(|native |js )type on the appian field with placeholder contains 'ph' the value 'value'
(|native |js )type on the appian element with placeholder contains 'ph' the value 'value'
(|native |js )clean the element with label 'text' in the section 'section'
(|native |js )type in the text field 'label' in section 'section' the value 'value'
(|native |js )type in the text area 'label' in section 'section' the value 'value'
(|native |js )click on the 'btn' button of the popup with the text 'text'
(|native |js )click on the first link in the section 'section'
(|native |js )click on the first button in the section 'section'
(|native |js )click on the link with index 'index' in the section 'section'
(|native |js )click on the button with index 'index' in the section 'section'
(|native |js )click on the 'link' link in the horizontal list
(|native |js )click on the link containing 'text' in the section 'section'
(|native |js )click on the button containing 'text' in the section 'section'
(|native |js )click on the link with text 'text' in the section 'section'
(|native |js )click on the button with text 'text' in the section 'section'
(|native |js )click on the radio button option 'value'
(|native |js )click on the first record of the column with index 'index' of the table
(|native |js )click on the record with row index 'row' and column index 'column' of the table
click the icon with preceding text 'text'
click the icon with following text 'text'
fill the textarea with role textbox with the text 'text'

## Verifications Steps:
verify that 'records' records appear in the 'name' table
verify that 'records' records appear in the 'name' grid
verify record related action 'related' is present
verify record related action 'related' is not present
verify field 'label' in section 'section' contains 'value'
verify field 'field' contains validation error message as 'msg'
verify field 'field' from grid 'name' which contains validation message 'msg'
verify field 'field' from section 'name' which contains validation message 'msg'
verify link 'link' is present in section 'section'
verify grid 'section' column 'column' row 'row' contains 'value'
verify grid 'grid' row 'row' is selected
verify button 'btn' is disabled
verify button 'btn' is enabled
verify 'field' field is not present under 'section' section
verify 'section_child' section present below 'section' section
verify that any paragraph contains the text 'text' and is presented
"""
import logging

from behave import use_step_matcher, step
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from arc.contrib.web.utils import click_button_by_xpath, send_keys_by_options, clear_and_send_keys_by_options
from arc.page_elements import Link, Links, Button, InputText, Text

use_step_matcher("re")
logger = logging.getLogger(__name__)


#######################################################################################################################
#                                            Actions Steps                                                            #
#######################################################################################################################
@step(u"login with the username '(?P<username>.+)' and password '(?P<password>.+)' in appian")
def appian_login_with_username_and_password_in_appian(context, username, password):
    """
    This steps performs a login of a standard appian application with the
    username and password that is passed by parameter.
    :example
        Given login with the username 'back_office' and password '1234' in appian
    :
    :tag Appian Actions Steps:
    :param context:
    :param username:
    :param password:
    :return:
    """
    inp__username = InputText(By.ID, 'un')
    inp__password = InputText(By.ID, 'pw')
    btn__login = Button(By.XPATH, "//*[@id='loginForm']//input[@type='submit']")

    inp__username.wait_until_visible()
    inp__username.text = username
    inp__password.text = password
    btn__login.wait_until_clickable()
    btn__login.click()


@step(u"logout in appian")
def appian_logout_in_appian(context):
    """
    This step logs off a user from a standard appian.
    :example
        Given logout in appian
    :
    :tag Appian Actions Steps:
    :param context:
    :return:
    """
    div__userprofile = Button(By.XPATH, "//div[contains(@class, 'UserProfileLayout---current_user_menu_wrapper')]/a")
    div__userprofile.wait_until_visible()
    div__userprofile.click()

    btn__close = Button(
        By.XPATH,
        "//div[contains(@class, 'UserProfileLayout---current_user_actions')]/div/div[3]/button"
    )
    btn__close.wait_until_visible()
    btn__close.click()


@step(u"search for '(?P<field>.+)' field with '(?P<value>.+)'")
def appian_search_for_field_with(context, field, value):
    """
    This step enters a value passed by parameter to perform a search in an appian search field.
    :example
        Given search for 'Username' field with 'user1'
    :
    :tag Appian Actions Steps:
    :param context:
    :param field:
    :param value:
    :return:
    """
    element = InputText(By.XPATH, f"//label[contains(text(),'{field}')]/following::input[1]")
    element.wait_until_visible()
    element.scroll_element_into_view()
    element.text = value

    element = context.utilities.switch_to_active_element()
    element.send_keys(Keys.TAB)


@step(u"select the dropdown '(?P<dropdown>.+)' with value '(?P<value>.+)'")
def appian_select_the_dropdown_with_value(context, dropdown, value):
    """
    This step selects an appian dropdown with a value passed by parameter.
    It does not support all types of dropdown that appian has by default.
    :example
        Given select the dropdown 'Username' with value 'user1'
    :
    :tag Appian Actions Steps:
    :param context:
    :param dropdown:
    :param value:
    :return:
    """
    locator = f"//*[text()='{dropdown}']/following::*[@role='listbox'][1]"

    element = Link(By.XPATH, locator)
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    element = InputText(By.XPATH, locator)
    element.wait_until_visible()
    element.text = value
    element.text = Keys.ENTER


@step(u"click on record related action '(?P<record>.+)'")
def appian_click_on_record_related_action(context, record):
    """
    This step clicks on the related action record indicated by parameter.
    :example
        Given click on record related action 'User 1'
    :
    :tag Appian Actions Steps:
    :param context:
    :param record:
    :return:
    """
    element = Link(By.XPATH, f"//li[@role='presentation']/following::*[contains(text(),'Related Actions')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    element = Link(By.XPATH, f"//*[contains(text(),'{record}')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"fill record type user filter '(?P<field>.+)' with '(?P<value>.+)'")
def appian_fill_record_type_user_filter_with(context, field, value):
    """
    This step populates a user filter type field.
    The name of the field and the value to be filled in are passed to it.
    :example
        Given fill record type user filter 'User' with 'user1'
    :
    :tag Appian Actions Steps:
    :param context:
    :param field:
    :param value:
    :return:
    """
    element = InputText(By.XPATH, f"//*[contains(text(),'{field}')]/following::input[1]")
    element.wait_until_visible()
    element.scroll_element_into_view()
    element.text = value

    element = context.utilities.switch_to_active_element()
    element.send_keys(Keys.TAB)


@step(u"select '(?P<value>.+)' value of the '(?P<header>.+)' dropdown with default value '(?P<d_value>.+)'")
def appian_select_value_of_the_dropdown_with_default_value(context, value, header, d_value):
    """
    This step selects the value of an appian dropdown by passing it the header of the field and the value to select.
    :example
        Given select 'user1' value of the 'Users' dropdown with default value 'user2'
    :
    :tag Appian Actions Steps:
    :param context:
    :param value:
    :param header:
    :param d_value:
    :return:
    """
    locator = f"//*[contains(text(),'{header}')]/following::*[.='{d_value}'][1]/.."
    element = Link(By.XPATH, locator)
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    element = context.utilities.switch_to_active_element()
    element.send_keys(Keys.DOWN)

    match = context.utilities.switch_to_active_element().text

    if value in context.utilities.switch_to_active_element().text:
        context.utilities.switch_to_active_element().send_keys(Keys.ENTER)
    else:
        context.utilities.switch_to_active_element().send_keys(Keys.DOWN)

    while match != context.utilities.switch_to_active_element().text:
        if value in context.utilities.switch_to_active_element().text:
            context.utilities.switch_to_active_element().send_keys(Keys.ENTER)
            break
        context.utilities.switch_to_active_element().send_keys(Keys.DOWN)


@step(u"go to appian module '(?P<module>.+)'")
def appian_go_to_appian_module(context, module):
    """
    This step clicks or opens a module passed by parameter.
    These default modules of appian usually act as a menu being at the top of the screen at the
    same level as the user options button.
    :example
        Given go to appian module 'Tracking'
    :
    :tag Appian Actions Steps:
    :param context:
    :param module:
    :return:
    """
    element = Link(By.XPATH, f"//a/div[contains(text(),'{module}')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on appian menu '(?P<menu>.+)'")
def appian_click_on_appian_menu(context, menu):
    """
    This step clicks on the menu option that is passed by parameter.
    :example
        Given click on appian menu 'payments'
    :
    :tag Appian Actions Steps:
    :param context:
    :param menu:
    :return:
    """
    element = Link(By.XPATH, f"//*[@role='tablist']/li[@title='{menu}']/a")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


#######################################################################################################################
#                                            Generic Steps                                                            #
#######################################################################################################################


@step(u"click on the first record of '(?P<name>.+)' grid")
@step(u"click on the first record of '(?P<name>.+)' table")
def appian_click_on_the_first_record_of_grid_table(context, name):
    """
    This step clicks on the first record in a table or grid.
    :example
        Given click on the first record of 'Users' grid
        Given click on the first record of 'Users' table
    :
    :tag Appian Generic Steps:
    :param context:
    :param name:
    :return:
    """
    element = Link(By.XPATH, f"//*[contains(text(),'{name}')]/following::table[1]/tbody[1]/tr[1]/td[1]/*[last()]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on the last record of '(?P<name>.+)' grid")
@step(u"click on the last record of '(?P<name>.+)' table")
def appian_click_on_the_last_record_of_grid_table(context, name):
    """
    This step clicks on the last record in a table or grid.
    :example
        Given click on the last record of 'User' grid
        Given click on the last record of 'User' table
    :
    :tag Appian Generic Steps:
    :param context:
    :param name:
    :return:
    """
    element = Link(By.XPATH, f"//*[contains(text(),'{name}')]/following::table[1]/tbody[1]/tr[last()]/td[1]/*[last()]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on the first row of column '(?P<column>.+)' of '(?P<name>.+)' grid")
@step(u"click on the first row of column '(?P<column>.+)' of '(?P<name>.+)' table")
def appian_click_on_the_first_row_of_column_of_name_table_grid(context, column, name):
    """
    This step clicks on the first row of the column whose name is passed by parameter of a table or grid whose name
    is passed to parameter.
    :example
        Given click on the first row of column 'Name' of 'Users' grid
        Given click on the first row of column 'Name' of 'Users' table
    :
    :tag Appian Generic Steps:
    :param context:
    :param column:
    :param name:
    :return:
    """
    element = Link(
        By.XPATH,
        f"//*[contains(text(),'{name}')]/following::table[1]/tbody[1]/tr[1]/td[{column}]/*[last()]/p/a"
    )
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"sort record by column '(?P<column>.+)' from grid '(?P<section>.+)'")
@step(u"sort record by column '(?P<column>.+)' from table '(?P<section>.+)'")
def appian_sort_record_grid_by_column_from_table_grid(context, column, section):
    """
    This steps sorts by column whose name is passed by parameter in the section indicated by
    parameter a table or grid.
    :example
        Given sort record by column 'creation date' from grid 'Users'
        Given sort record by column 'creation date' from table 'Users'
    :
    :tag Appian Generic Steps:
    :param context:
    :param column:
    :param section:
    :return:
    """
    element = Link(
        By.XPATH,
        f"//*[contains(text(),'{section}')]/following::table[1]/thead[1]/tr[1]/th/*[contains(text(),'{column}')]"
    )
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"sort record column index '(?P<index>.+)' from grid '(?P<name>.+)'")
@step(u"sort record column index '(?P<index>.+)' from table '(?P<name>.+)'")
def appian_sort_record_grid_by_column_index_from_table_grid(context, index, name):
    """
    This step sorts the records of a table or grid according to the index of the column that is passed to it by
    parameter and the name of the table or grid to be sorted.
    :example
        Given sort record column index '2' from grid 'Users'
        Given sort record column index '2' from table 'Users'
    :
    :tag Appian Generic Steps:
    :param context:
    :param index:
    :param name:
    :return:
    """
    element = Link(
        By.XPATH,
        f"//*[contains(text(),'{name}')]/following::table[1]/thead[1]/tr[1]/th[{index}]/div"
    )
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on first record of '(?P<name>.+)' section")
def appian_click_on_first_record_of_section(context, name):
    """
    This step clicks on the first record of a section by passing the name of the section by parameter.
    :example
        Given click on first record of 'Payments' section
    :
    :tag Appian Generic Steps:
    :param context:
    :param name:
    :return:
    """
    element = Link(By.XPATH, f"//*[contains(text(),'{name}')]/following::table[1]/tbody[1]/tr[1]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on record type '(?P<name>.+)' and the row '(?P<number>.+)'")
def appian_click_on_record_type_and_the_row(context, name, number):
    """
    This step clicks on the record by passing the name of the record and indicating the number of the row where it is.
    :example
        Given click on record type 'Users' and the row '2'
    :
    :tag Appian Generic Steps:
    :param context:
    :param name:
    :param number:
    :return:
    """
    element = Link(By.XPATH, f"//*[contains(text(),'{name}')]//following::table[1]/tbody[1]/tr[{number}]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on record grid navigation '(?P<page>.+)'")
def appian_click_on_record_grid_navigation(context, page):
    """
    This steps clicks on the appian navigation grid log.
    :example
        Given click on record grid navigation 'Modules'
    :
    :tag Appian Generic Steps:
    :param context:
    :param page:
    :return:
    """
    element = Link(By.XPATH, f"//*[(@aria-label='{page}') or (@title='{page}')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"sort record grid by column '(?P<column>.+)'")
def appian_sort_record_grid_by_column(context, column):
    """
    This step sorts by the name of a column passed by parameter the register of a grid.
    :example
        Given sort record grid by column 'creation date'
    :
    :tag Appian Generic Steps:
    :param context:
    :param column:
    :return:
    """
    element = Link(By.XPATH, f"//*[*]/following::table[1]/thead[1]/tr[1]/th/*[contains(text(),'{column}')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on '(?P<btn>.+)' button which is left to button '(?P<reference>.+)'")
def appian_click_on_button_which_is_left_to_button(context, btn, reference):
    """
    This step clicks on the button to the left of a reference button. You must pass the name of the button you
    want to click and the name of the reference button.
    :example
        Given click on 'search' button which is left to button 'reset'
    :
    :tag Appian Generic Steps:
    :param context:
    :param btn:
    :param reference:
    :return:
    """
    element = Button(By.XPATH, f"//button[contains(text(),'{reference}')][1]/preceding::*[contains(text(),'{btn}'")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on '(?P<btn>.+)' button which is right to button '(?P<reference>.+)'")
def appian_click_on_button_which_is_right_to_button(context, btn, reference):
    """
    This step clicks on the button to the right of a reference button. You must pass the name of the button you
    want to click and the name of the reference button.
    :example
        Given click on 'reset' button which is right to button 'search'
    :
    :tag Appian Generic Steps:
    :param context:
    :param btn:
    :param reference:
    :return:
    """
    element = Button(By.XPATH, f"//button[contains(text(),'{reference}')][1]/following::*[contains(text(),'{btn}'")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on card which contains text as '(?P<text>.+)'")
@step(u"click on paragraph which contains text as '(?P<text>.+)'")
def appian_click_on_card_paragraph_which_contains_text_as(context, text):
    """
    This step clicks on the letter or paragraph containing the text passed by parameter.
    :example
        Given click on card which contains text as 'Page of'
        Given click on paragraph which contains text as 'Page of'
    :
    :tag Appian Generic Steps:
    :param context:
    :param text:
    :return:
    """
    element = Link(By.XPATH, f"//strong[contains(text(),'{text}')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"clear record type user filter '(?P<field>.+)'")
def appian_clear_record_type_user_filter(context, field):
    """
    This step cleans the record of a filter from the field whose name is passed to it by parameter.
    :example
        Given clear record type user filter 'search'
    :
    :tag Appian Generic Steps:
    :param context:
    :param field:
    :return:
    """
    element = InputText(By.XPATH, f"//*[contains(text(),'{field}')]/following::input[1]")
    element.wait_until_visible()
    element.scroll_element_into_view()
    element.clear()


@step(u"fill '(?P<field>.+)' field with '(?P<value>.+)'")
def appian_fill_field_with(context, field, value):
    """
    This steps populates the field standard of appian with the value passed by parameter.
    :example
        Given fill 'amount' field with '100.00'
    :
    :tag Appian Generic Steps:
    :param context:
    :param field:
    :param value:
    :return:
    """
    element = InputText(By.XPATH, f"//label[contains(text(),'{field}')]/following::input[1]")
    element.wait_until_visible()
    element.scroll_element_into_view()
    element.text = value

    element = context.utilities.switch_to_active_element()
    element.send_keys(Keys.TAB)


@step(u"fill field '(?P<name>.+)' in section '(?P<section>.+)' with '(?P<value>.+)'")
def appian_fill_field_in_section_with_value(context, name, section, value):
    """
    This steps fills the field with the value passed by parameter in the section indicated by parameter.
    :example
        Given fill field 'amount' in section 'payments' with '100.00'
    :
    :tag Appian Generic Steps:
    :param context:
    :param name:
    :param section:
    :param value:
    :return:
    """
    element = InputText(
        By.XPATH,
        f"//*[contains(text(),'{section}')]/following::*[contains(text(),'{name}')]/following::input[1]"
    )
    element.wait_until_visible()
    element.scroll_element_into_view()
    element.text = value

    element = context.utilities.switch_to_active_element()
    element.send_keys(Keys.TAB)


@step(u"click a section '(?P<section>.+)' to (expand|collapse)")
def appian_click_a_section_to_expand_collapse(context, section, option):
    """
    This step clicks to extend or collapse (depending on the option chosen) a section passed by parameter.
    :example
        Given click a section 'Additional information' to expand
        Given click a section 'Additional information' to collapse
    :
    :tag Appian Generic Steps:
    :param context:
    :param section:
    :param option:
    :return:
    """
    element = Link(By.XPATH, f"//*[contains(text(),'{section}')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on link '(?P<name>.+)' from table '(?P<section>.+)'")
@step(u"click on link '(?P<name>.+)' from section '(?P<section>.+)'")
def appian_click_on_link_from_table_section(context, name, section):
    """
    This step clicks on the link with the text passed by parameter of a table or section
    indicated the name by parameter.
    :example
        Given click on link 'add' from table 'Payments'
        Given click on link 'add' from section 'Payments'
    :
    :tag Appian Generic Steps:
    :param context:
    :param name:
    :param section:
    :return:
    """
    element = Link(By.XPATH, f"//*[contains(text(),'{section}')]/following::a[contains(text(),'{name}')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on radio option '(?P<value>.+)' for field '(?P<field>.+)'")
def appian_click_on_radio_option_for_field(context, value, field):
    """
    This step clicks on the option indicated by parameter of a radius button of a field indicated by parameter.
    :example
        Given click on radio option 'euro' for field 'Currency'
    :
    :tag Appian Generic Steps:
    :param context:
    :param value:
    :param field:
    :return:
    """
    element = Link(
        By.XPATH, f"(//strong[contains(text(),'{field}')]/following::input[@value='{value}'])[1]/following::label[1]"
    )
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on radio option '(?P<value>.+)'")
def appian_click_on_radio_option(context, value):
    """
    This step clicks on a radio button option that is indicated by parameter.
    :example
        Given click on radio option 'euro'
    :
    :tag Appian Generic Steps:
    :param context:
    :param value:
    :return:
    """
    element = Link(
        By.XPATH, f"//*[@role='radiogroup']/*/input[@type='radio']/following::label[contains(text(),'{value}')]"
    )
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"select the '(?P<heading>.+)' checkbox '(?P<label>.+)'")
def appian_select_the_checkbox_label(context, heading, label):
    """
    This step selects the checkbox after a header or title and passing the label of the option you want to select.
    :example
        Given select the 'Currency' checkbox 'euro'
    :
    :tag Appian Generic Steps:
    :param context:
    :param heading:
    :param label:
    :return:
    """
    element = Link(
        By.XPATH, f"//*[contains(text(), '{heading}')]/following::*[@type='checkbox']/following::*[text()=''{label}'']"
    )
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"click on the first record of '(?P<table>.+)' grid which has value '(?P<value>.+)'")
@step(u"click on the first record of '(?P<table>.+)' table which has value '(?P<value>.+)'")
def appian_click_on_the_first_record_of_grid_table_which_has_value(context, table, value):
    """
    This step clicks on the first record of the table or grid that has le value passed by parameter.
    You must also pass the name of the table or grid.
    :example
        Given click on the first record of 'Users' grid which has value 'user1'
        Given click on the first record of 'Users' table which has value 'user1'
    :
    :tag Appian Generic Steps:
    :param context:
    :param table:
    :param value:
    :return:
    """
    element = Link(
        By.XPATH,
        f"//*[contains(text(),'{table}')]/following::table[1]/tbody[1]/tr[1]/td[1]/div/p/a[contains(text(),'{value}')]"
    )
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"fill textarea from section '(?P<section>.+)' for the field '(?P<field>.+)' with the value '(?P<value>.+)'")
def appian_fill_textarea_from_section_for_the_field_with_the_value(context, section, field, value):
    """
    This step fills the textarea of the section passed by parameter also passing the name of the field of the textarea
    and the value to fill.
    :example
        Given fill textarea from section 'Payments' for the field 'amount' with the value '10.00'
    :
    :tag Appian Generic Steps:
    :param context:
    :param section:
    :param field:
    :param value:
    :return:
    """
    element = InputText(
        By.XPATH,
        f"//*[contains(text(),'{section}')]/following::*[contains(text(),'{field}')]/following::textarea[1]"
    )
    element.wait_until_visible()
    element.scroll_element_into_view()
    element.text = value


@step(u"click on icon of column '(?P<column>.+)' from '(?P<table>.+)' table on row '(?P<row>.+)'")
def appian_click_on_icon_of_column_from_table_on_row(context, column, table, row):
    """
    This step clicks on the column icon and row passed by parameter of the table with the name passed by parameter.
    :example
        Given click on icon of column '4' from 'Payments' table on row '2'
    :
    :tag Appian Generic Steps:
    :param context:
    :param column:
    :param table:
    :param row:
    :return:
    """
    element = Link(By.XPATH, f"//*[contains(text(),'{table}')]/following::tr[{row}]/td[{column}]//p/a")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step(u"(|native |js )type in the text field containing '(?P<label>.+)' the value '(?P<value>.+)'")
@step(u"(|native |js )type in the text area containing '(?P<label>.+)' the value '(?P<value>.+)'")
def appian_type_in_the_text_area_field_containing_the_value(context, option, label, value):
    """
    This step writes in the field or textarea that contains the text in the label passed by parameter the value that
    is indicated.
    :example
        Given type in the text field containing 'amount' the value '10.00'
        Given native type in the text field containing 'amount' the value '10.00'
        Given js type in the text field containing 'amount' the value '10.00'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param label:
    :param value:
    :return:
    """
    element = InputText(
        By.XPATH,
        f"//*[contains(text(),'{label}')]//following::*[self::input or self::textarea][1]"
    )

    element.wait_until_visible()
    element.scroll_element_into_view()
    context.utilities.move_to_element(element)

    send_keys_by_options(context, element, value, option=option.strip())


@step(u"(|native |js )type in the date field containing '(?P<label>.+)' the value '(?P<value>.+)'")
def appian_type_in_the_date_field_containing_the_value(context, option, label, value):
    """
    This step writes in the date field that contains the text in the label passed by parameter the value that
    is indicated.
    :example
        Given type in the date field containing 'Creation' the value '12/02/1991'
        Given native type in the date field containing 'Creation' the value '12/02/1991'
        Given js type in the date field containing 'Creation' the value '12/02/1991'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param label:
    :param value:
    :return:
    """
    element = InputText(
        By.XPATH,
        f"//*[contains(text(),'{label}')]//following::input[1]"
    )

    element.wait_until_visible()
    element.scroll_element_into_view()
    context.utilities.move_to_element(element)

    clear_and_send_keys_by_options(context, element, value, option=option.strip())


@step(u"(|native |js )type on the appian field with placeholder contains '(?P<ph>.+)' the value '(?P<value>.+)'")
@step(u"(|native |js )type on the appian element with placeholder contains '(?P<ph>.+)' the value '(?P<value>.+)'")
def appian_type_on_the_appian_field_with_placeholder_contains_the_value(context, option, ph, value):
    """
    This step writes in the appian field that contains the text in the placeholder passing the value indicated to it
    by parameter.
    :example
        Given type on the appian field with placeholder contains 'username' the value 'user1'
        Given type on the appian element with placeholder contains 'username' the value 'user1'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param ph:
    :param value:
    :return:
    """
    element = InputText(By.XPATH, f"//*[@placeholder='{ph}']")

    element.wait_until_visible()
    element.scroll_element_into_view()
    context.utilities.move_to_element(element)

    clear_and_send_keys_by_options(context, element, value, option=option.strip())


@step(u"(|native |js )clean the element with label '(?P<t>.+)' in the section '(?P<s>.+)'")
def appian_clean_the_element_with_label_in_the_section(context, option, t, s):
    """
    This step cleans the element with label and section passed by parameter.
    :example
        Given clean the element with label 'birthday' in the section 'Information'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param t:
    :param s:
    :return:
    """
    element = InputText(
        By.XPATH,
        f"//*[contains(text(),'{s}')]//following::*[text()='{t}']/following::*[self::input or self::textarea][1]"
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


@step(u"(|native |js )type in the text field '(?P<label>.+)' in section '(?P<s>.+)' the value '(?P<value>.+)'")
@step(u"(|native |js )type in the text area '(?P<label>.+)' in section '(?P<s>.+)' the value '(?P<value>.+)'")
def appian_type_in_the_text_field_in_section_the_value(context, option, label, s, value):
    """
    This step writes in the text area or in the field according to the label that is passed by parameter,
    in the section passed by parameter the indicated value.
    :example
        Given type in the text field 'amount' in section 'Payments' the value '100.00'
        Given type in the text area 'amount' in section 'Payments' the value '100.00'
        Given js type in the text area 'amount' in section 'Payments' the value '100.00'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param label:
    :param s:
    :param value:
    :return:
    """
    element = InputText(
        By.XPATH,
        f"//*[contains(text(),'{s}')]//following::*[text()='{label}']//following::*[self::input or self::textarea][1]"
    )

    element.wait_until_visible()
    element.scroll_element_into_view()
    context.utilities.move_to_element(element)
    send_keys_by_options(context, element, value, option=option.strip())


@step(u"(|native |js )click on the '(?P<btn>.+)' button of the popup with the text '(?P<text>.+)'")
def appian_click_on_the_button_of_the_popup_with_the_text(context, option, btn, text):
    """
    This step clicks on the button passing the name by parameter, in the popup with the indicated text.
    :example
        Given click on the 'accept' button of the popup with the text 'Information'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param btn:
    :param text:
    :return:
    """
    loc = f"//*[@role='dialog']//following::*[text()='{text}']//following::button[text()='{btn}']"
    click_button_by_xpath(context, loc, option=option.strip())


@step(u"(|native |js )click on the first link in the section '(?P<section>.+)'")
@step(u"(|native |js )click on the first button in the section '(?P<section>.+)'")
def appian_click_on_the_first_button_in_the_section(context, option, section):
    """
    This step clicks on the first link or button of the section indicated by parameter.
    :example
        Given click on the first link in the section 'Payments'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param section:
    :return:
    """
    element = Link(
        By.XPATH,
        f"//*[contains(text(),'{section}')]//following::a[1]"
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


@step(u"(|native |js )click on the link with index '(?P<index>.+)' in the section '(?P<section>.+)'")
@step(u"(|native |js )click on the button with index '(?P<index>.+)' in the section '(?P<section>.+)'")
def appian_click_on_the_link_with_index_in_the_section(context, option, index, section):
    """
    This step clicks on the button or link with the appearance index passed by parameter in the section indicating
    the text.
    :example
        Given click on the link with index '2' in the section 'Payments'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param index:
    :param section:
    :return:
    """
    loc = f"//*[contains(text(),'{section}')]//following::a[{index}]"
    click_button_by_xpath(context, loc, option=option.strip())


@step(u"(|native |js )click on the '(?P<link>.+)' link in the horizontal list")
def appian_click_on_the_link_in_the_horizontal_list(context, option, link):
    """
    This step clicks on the link with the text passed by parameter in the horizontal list or tab list component.
    :example
        Given click on the 'return' link in the horizontal list
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param link:
    :return:
    """
    element = Link(By.XPATH, f"//ul[@role='tablist']//following::a//div[text()='{link}']")
    element.wait_until_clickable()
    element.scroll_element_into_view()

    if option.strip() == 'native':
        element = context.utilities.convert_to_selenium_element(element)
        element.click()

    elif option.strip() == 'js':
        element = context.utilities.convert_to_selenium_element(element)
        context.utilities.js_click(element)

    else:
        element.click()


@step(u"(|native |js )click on the link containing '(?P<text>.+)' in the section '(?P<section>.+)'")
@step(u"(|native |js )click on the button containing '(?P<text>.+)' in the section '(?P<section>.+)'")
def appian_click_on_the_button_link_containing_in_the_section(context, option, text, section):
    """
    This step clicks on the link or button that contains a text passed by parameter in the indicated section.
    :example
        Given click on the link containing 'add' in the section 'Payments'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param text:
    :param section:
    :return:
    """

    loc = f"//*[text()='{section}']//following::button[contains(text(), '{text}')]"
    click_button_by_xpath(context, loc, option=option.strip())


@step(u"(|native |js )click on the link with text '(?P<text>.+)' in the section '(?P<section>.+)'")
@step(u"(|native |js )click on the button with text '(?P<text>.+)' in the section '(?P<section>.+)'")
def appian_click_on_the_link_button_with_text_in_the_section(context, option, text, section):
    """
    This step clicks on the link or button that has exactly the text passed by parameter in the indicated section.
    :example
        Given click on the link with text 'add' in the section 'Payments'
        Given click on the button with text 'add' in the section 'Payments'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param text:
    :param section:
    :return:
    """
    element = Link(
        By.XPATH,
        f"//*[text()='{section}']//following::button[text()='{text}']"
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


@step(u"(|native |js )click on the radio button option '(?P<value>.+)'")
def appian_click_on_the_radio_button_option(context, option, value):
    """
    This step clicks on the option of the radio button that is passed by parameter.
    :example
        Given click on the radio button option 'euro'
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param value:
    :return:
    """
    loc = f"//*[@type='radio'][@value='{value}']"
    click_button_by_xpath(context, loc, option=option.strip())


@step(u"(|native |js )click on the first record of the column with index '(?P<index>.+)' of the table")
def appian_click_on_the_first_record_of_the_column_with_index_of_the_table(context, option, index):
    """
    This step clicks on the first record in the column with index passed by parameter.
    :example
        Given click on the first record of the column with index '2' of the table
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param index:
    :return:
    """
    element = Button(
        By.XPATH,
        f"//table/tbody/tr[1]/td[{index}]//*"
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


@step(u"(|native |js )click on the record with row index '(?P<row>.+)' and column index '(?P<column>.+)' of the table")
def appian_click_on_the_record_with_row_index_and_column_index_of_the_table(context, option, row, column):
    """
    This step clicks on the table record passing the row index and column index.
    :example
        Given click on the record with row index '2' and column index '4' of the table
    :
    :tag Appian Generic Steps:
    :param context:
    :param option:
    :param row:
    :param column:
    :return:
    """
    loc = f"//table/tbody/tr[{row}]/td[{column}]//*"
    click_button_by_xpath(context, loc, option=option.strip())


@step(u"click the icon with preceding text '(?P<text>.+)'")
def click_the_icon_with_preceding_text(context, text):
    """
    This Step clicks an icon with preceding text 'text'
    :example
        When click the icon with preceding text 'text'
    :
    :tag Appian Generic Steps:
    :param context:
    :param text:
    :return:
    """
    btn_icon = WebDriverWait(context.driver, 25).until(
        ec.visibility_of_element_located((By.XPATH, f"(//*[contains(text(),'{text}')]//following::a[1])[1]"))
    )
    action = ActionChains(context.driver)
    action.move_to_element(btn_icon).perform()
    btn_icon.click()


@step(u"click the icon with following text '(?P<text>.+)'")
def click_the_icon_with_following_text(context, text):
    """
    This Step clicks an icon with following text 'text'
    :example
        When click the icon with following text 'text'
    :
    :tag Appian Generic Steps:
    :param context:
    :param text:
    :return:
    """
    btn_icon = WebDriverWait(context.driver, 25).until(
        ec.visibility_of_element_located((By.XPATH, f"(//*[contains(text(),'{text}')]//preceding::a[1])[1]"))
    )
    action = ActionChains(context.driver)
    action.move_to_element(btn_icon).perform()
    btn_icon.click()


@step("fill the textarea with role textbox with the text '(?P<text>.+)'")
def fill_the_textarea_with_role_textbox_with_the_text(context, text):
    """
    This step is used to fill in comments in a textarea with role as textbox
    :example
        When fill the textarea with role textbox with the text 'a example text'
    :
    :param context:
    :param text:
    :return:
    """
    element = InputText(By.XPATH, f"//textarea[@role='textbox']")
    element.wait_until_clickable(10)
    element.text = text


#######################################################################################################################
#                                         Verifications Steps                                                         #
#######################################################################################################################


@step(u"verify that '(?P<records>.+)' records appear in the '(?P<name>.+)' table")
@step(u"verify that '(?P<records>.+)' records appear in the '(?P<name>.+)' grid")
def appian_verify_that_records_appear_in_the_table_grid(context, records, name):
    """
    This step verifies that there are as many records as are passed by parameter in the table or grid that is
    indicated by its name.
    :example
        Then verify that '5' records appear in the 'Users' table
        Then verify that '5' records appear in the 'Users' grid
    :
    :tag Appian Verification Steps:
    :param context:
    :param records:
    :param name:
    :return:
    """
    elements = Links(By.XPATH, f"//*[contains(text(),'{name}')]/following::table[1]/tbody[1]/tr/td[1]/*[last()]")
    current = len(elements.page_elements)
    expected = int(records)

    error_msg = f'The number of expected records are not the same as the current records.\n' \
                f'Current records: {current}\n' \
                f'Expected records: {expected}'

    result = current == expected
    context.func.evidences.add_unit_table(
        'Records verification',
        'Expected Records in table',
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify record related action '(?P<related>.+)' is present")
def appian_verify_record_relate_action_is_present(context, related):
    """
    This step verifies that the related action log is present.
    :example
        Then verify record related action 'Add User' is present
    :
    :tag Appian Verification Steps:
    :param context:
    :param related:
    :return:
    """
    element = Link(By.XPATH, f"//li[@role='presentation']/following::*[contains(text(),'Related Actions')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    element = Link(By.XPATH, f"//*[contains(text(),'{related}')]")
    element.wait_until_visible()

    current = element.is_present()
    expected = True

    error_msg = f'The related action record is not present.'

    result = current is expected
    context.func.evidences.add_unit_table(
        'Related action records verification',
        'Related action records',
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify record related action '(?P<related>.+)' is not present")
def appian_verify_record_related_action_is_not_present(context, related):
    """
    This step verifies that the related action log is not present.
    :example
        Then verify record related action 'Add User' is not present
    :
    :tag Appian Verification Steps:
    :param context:
    :param related:
    :return:
    """
    element = Link(By.XPATH, f"//li[@role='presentation']/following::*[contains(text(),'Related Actions')]")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    element = Link(By.XPATH, f"//*[contains(text(),'{related}')]")
    element.wait_until_visible()

    current = element.is_present()
    expected = False

    error_msg = f'The related action record is present.'

    result = current is expected
    context.func.evidences.add_unit_table(
        'Related action records verification',
        'Related action records',
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify field '(?P<label>.+)' in section '(?P<s>.+)' contains '(?P<v>.+)'")
def appian_verify_field_in_section_contains(context, label, s, v):
    """
    This step verifies that the field with label passed by parameter in the indicated section contains the text
    indicated by parameter.
    :example
        Then verify field 'customer' in section 'Payments' contains 'customer_1'
    :
    :tag Appian Verification Steps:
    :param context:
    :param label:
    :param s:
    :param v:
    :return:
    """
    loc = f"//*[contains(text(),'{s}')]/following::*[contains(text(),'{label}')]/following::*[contains(text(),'{v}')]"
    element = Link(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'There is no field that contains the expected value.'

    result = current is expected
    context.func.evidences.add_unit_table(
        'Verify field is present',
        'Field',
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify field '(?P<field>.+)' contains validation error message as '(?P<msg>.+)'")
def appian_verify_field_contains_validation_error_message_as(context, field, msg):
    """
    This step verifies that the field indicated by parameter contains the error validation message indicated.
    :example
        Then verify field 'password' contains validation error message as 'Password is mandatory'
    :
    :tag Appian Verification Steps:
    :param context:
    :param field:
    :param msg:
    :return:
    """
    loc = f"//*[contains(text(),'{field}')]/following::*[@role='alert'][1]"
    element = Text(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.text
    expected = msg

    error_msg = f'The error message in the field is not the same as expected.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify error message in field',
        'Error Message',
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify field '(?P<field>.+)' from grid '(?P<name>.+)' which contains validation message '(?P<msg>.+)'")
@step(u"verify field '(?P<field>.+)' from section '(?P<name>.+)' which contains validation message '(?P<msg>.+)'")
def appian_verify_field_from_grid_section_which_contains_validation_message(context, field, name, msg):
    """
    This step verifies that the parameter indexed field of the section or grid with the name passed by parameter
    contains the indicated validation message.
    :example
        Then verify field 'customer' from grid 'payments' which contains validation message 'Customer does not exists'
    :
    :tag Appian Verification Steps:
    :param context:
    :param field:
    :param name:
    :param msg:
    :return:
    """
    loc = f"//*[contains(text(),'{name}')]/following::*[contains(text(),'{field}')]/following::*[@role='alert'][1]"
    element = Text(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.text
    expected = msg

    error_msg = f'The validation message in the field is not the same as expected.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify validation message in field',
        'validation Message',
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify link '(?P<link>.+)' is present in section '(?P<section>.+)'")
def appian_verify_link_is_present_in_section(context, link, section):
    """
    This step verifies that the link passed by parameter is present in the indicated section.
    :example
        Then verify link 'delete' is present in section 'Users'
    :
    :tag Appian Verification Steps:
    :param context:
    :param link:
    :param section:
    :return:
    """
    loc = f"//*[contains(text(),'{section}')]/following::a[contains(text(),'{link}')]"
    element = Text(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'The link expected is not present.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify link is present',
        'Link present',
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify grid '(?P<s>.+)' column '(?P<column>.+)' row '(?P<row>.+)' contains '(?P<v>.+)'")
def appian_verify_grid_column_row_contains(context, s, column, row, v):
    """
    This step verifies that in the indicated grid, in the column and row indicated by index, it contains the value
    indicated by parameter.
    :example
        Then verify grid 'Users' column '1' row '3' contains 'user_1'
    :
    :tag Appian Verification Steps:
    :param context:
    :param s:
    :param column:
    :param row:
    :param v:
    :return:
    """
    loc = f"//*[contains(text(),'{s}')]/following::table[1]/tbody[1]/tr[{row}]/td[{column}]/p[contains(text(),'{v}')]"
    element = Text(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'The expected value is not present.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify expected value in grid',
        f"Value in column {column} and row {row}",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify grid '(?P<grid>.+)' row '(?P<row>.+)' is selected")
def appian_verify_grid_row_is_selected(context, grid, row):
    """
    This step verifies that the row with index passed by parameter of the indicated grid is selected.
    :example
        Then verify grid 'Payments' row '1' is selected
    :
    :tag Appian Verification Steps:
    :param context:
    :param grid:
    :param row:
    :return:
    """
    loc = f"//*[contains(text(),'{grid}')][1]/following::table[1]/tbody[1]/tr[{row}][not (@aria-selected='false')]"
    element = Text(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'The expected row is not selected.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify row is selected',
        f"Row {row}",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify button '(?P<btn>.+)' is disabled")
def appian_verify_button_is_disabled(context, btn):
    """
    This step verifies that the button indicated by parameter is disabled.
    :example
        Then verify button 'next' is disabled
    :
    :tag Appian Verification Steps:
    :param context:
    :param btn:
    :return:
    """
    loc = f"//button[(contains(text(),'{btn}') and @disabled='')]"
    element = Button(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'The button is not disabled.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify button is disabled',
        f"Button",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify button '(?P<btn>.+)' is enabled")
def appian_verify_button_is_enabled(context, btn):
    """
    This step verifies that the button indicated by parameter is enabled.
    :example
        Then verify button 'next' is enabled
    :
    :tag Appian Verification Steps:
    :param context:
    :param btn:
    :return:
    """
    loc = f"//button[(contains(text(),'{btn}') and @disabled='')]"
    element = Button(By.XPATH, loc)

    try:
        element.wait_until_visible()
        element.scroll_element_into_view()
        current = element.is_present()

    except (Exception,):
        current = True

    expected = True
    error_msg = f'The button is not enabled.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify button is enabled',
        f"Button",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify '(?P<field>.+)' field is not present under '(?P<section>.+)' section")
def appian_verify_field_is_not_present_under_section(context, field, section):
    """
    This step verifies that the indicated field is not present under the indicated section.
    :example
        Then verify 'amount' field is not present under 'Payments' section
    :
    :tag Appian Verification Steps:
    :param context:
    :param field:
    :param section:
    :return:
    """
    loc = f"((//*[contains(text(),'{section}')])[1]/following::*[contains(text(),'{field}')])[1]"
    element = Text(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'The field is not present under the expected section.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify field is present',
        f"Field {field}",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step(u"verify '(?P<section_child>.+)' section present below '(?P<section>.+)' section")
def appian_verify_section_present_below_section(context, section_child, section):
    """
    This step verifies that the indicated field is not present below the indicated section.
    :example
        Then verify 'Payments' section present below 'Users' section
    :
    :tag Appian Verification Steps:
    :param context:
    :param section_child:
    :param section:
    :return:
    """
    loc = f"//*[contains(text(),'{section}')]/following::*[contains(text(),'{section_child}')][1]"
    element = Text(By.XPATH, loc)
    element.wait_until_visible()
    element.scroll_element_into_view()
    current = element.is_present()
    expected = True

    error_msg = f'The section is not present below the expected section.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify section is present',
        f"Section {section_child}",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg


@step("verify that any paragraph contains the text '(?P<text>.+)' and is presented")
def verify_that_any_paragraph_contains_the_text_and_is_presented(context, text):
    """
    This steps verify if a paragraph of the current page contains the text passed on the screen and if it is present
    on the page.
    :example
        Then verify that any paragraph contains the text 'an example text' and is presented
    :
    :tag Appian Verification Steps:
    :param context:
    :param text:
    :return:
    """
    element = InputText(By.XPATH, f"//p[contains(.,'{text}')]")
    element.wait_until_visible(10)
    current = element.is_present()
    expected = True

    error_msg = f'The text is not present in any paragraph of the page.'

    result = expected == current
    context.func.evidences.add_unit_table(
        'Verify that any paragraph contains the text and is presented',
        f"Text: {text}",
        current,
        expected,
        result,
        error_msg=error_msg
    )

    assert result, error_msg
