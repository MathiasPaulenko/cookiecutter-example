# -*- coding: utf-8 -*-
"""
Examples of behave Step usage in TalosBDD.
"""
import logging

from behave import use_step_matcher, step
from selenium.webdriver.common.by import By

from arc.page_elements import Button, Text, Link
from test.helpers.page_objects.examples.san_web_demo.po_san import SanPageObject
from test.helpers.page_objects.examples.san_web_demo.po_menu import MenuPageObject

logger = logging.getLogger(__name__)
use_step_matcher("re")


@step("access the web application '(?P<url>.+)'")
def test(context, url):
    logger.info(f'Accessing the url: {url}')
    context.driver.get(url)


@step("accept all cookies")
def test(context):
    try:
        logger.info('Accept cookie pop up if exists')
        btn__accept_cookies = Button(By.ID, 'privacy_pref_optin')
        btn__accept_cookies.wait_until_visible()
        btn__accept_cookies.click()
    except (Exception,):
        logger.info('Cookies pop up does not exist, passing...')


@step("go to the '(?P<page>.+)' page")
def test(context, page):
    logger.info(f"Go to web page: {page}")
    po_menu = MenuPageObject()
    po_menu.go_to_page(page, context)


@step("filter for the year '(?P<option>.+)' in Closing Markets")
def test(context, option):
    logger.info(f"Filter for option {option} in Closing Markets page")
    po_closing_market = SanPageObject()
    po_closing_market.filter_by_year(option)


@step("filter for the month '(?P<option>.+)' in Closing Markets")
def test(context, option):
    logger.info(f"Filter for month {option} in closing Markets page")
    po_closing_market = SanPageObject()
    po_closing_market.filter_by_month(option)


@step("open the first PDF")
def test(context):
    logger.info(f"Opening the first PDF available")
    po_closing_market = SanPageObject()
    po_closing_market.download_first_pdf()


@step("check if the title is '(?P<value>.+)'")
def test(context, value):
    logger.info(f"Check if the title is: {value}")
    title = Text(By.XPATH, f"//h1[text()='{value}']")
    title.wait_until_visible()
    title.scroll_element_into_view()
    msg = f"The actual title and the expected title are not the same"
    assert title.text == value, msg


@step("choose the link from the top menu '(?P<value>.+)'")
def test(context, value):
    logger.info(f"Choose the link from the top menu: {value}")
    menu_link = Link(By.XPATH, f"//ul[@class='header__quicklinks-container']//child::a[contains(text(), '{value}')]")
    menu_link.wait_until_clickable()
    menu_link.scroll_element_into_view()
    menu_link.click()


@step("filter press by date")
def test(context):
    logger.info("Filter press by date")
    po_closing_market = SanPageObject()
    po_closing_market.filter_by_date_in_press_room()


@step("filter for the year '(?P<year>.+)' in Dividens")
def test(context, year):
    logger.info(f"Filter for the year {year} in Dividends page")
    po_closing_market = SanPageObject()
    po_closing_market.filter_by_year_dividends(year)


@step("go to Home")
def test(context):
    logger.info(f"Go to home page")
    Link(By.XPATH, "//a[@class='header-logo__url']").click()
