@san_web
Feature: demo
  demo of santander.com home

  Background:
    Given access the web application '${{datas:web}}'
    And accept all cookies

  @san_web1
  Scenario:  Closing Markets
    And go to the 'Closing Markets' page
    When filter for the year '2019' in Closing Markets
    And filter for the month 'October' in Closing Markets
    Then the current page should be audited for accessibility
    And open the first PDF

  @san_web2
  Scenario:  Navigation
    Given go to the 'Price' page
    Then check if the title is 'Price'
    When choose the link from the top menu 'Press Room'
    And filter press by date
    And go to Home
    Given go to the 'Dividends' page
    Then the current page should be audited for accessibility
    And filter for the year '2018' in Dividens

