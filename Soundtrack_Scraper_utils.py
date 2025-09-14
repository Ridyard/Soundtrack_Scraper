
# script to hold the utility functions when scraping soundtrack info
# usage: Soundtrack_Scraper_tv.py & Soundtrack_Scraper_film.py


# Soundtrack_Scraper_utils.py
"""
Utility functions for Selenium-based scraping in the Soundtrack Playlist project.
These helpers handle common page interactions like cookie banners, element finding,
expanding track lists, and detecting login modals.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Optional: if you need these in future helpers
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
# import pandas as pd
# from pathlib import Path
# import os


def handle_cookies(browser, selectors, timeout=10):
    """
    Clicks the 'Agree' button on a cookie consent popup if present.

    :param browser: Selenium WebDriver instance
    :param selectors: dict containing 'cookies_agree_button' XPath
    :param timeout: seconds to wait for the button (optional)
    """
    agree_button_xpath = selectors.get("cookies_agree_button")
    if not agree_button_xpath:
        return

    try:
        agree_button = WebDriverWait(browser, timeout).until(
            EC.element_to_be_clickable((By.XPATH, agree_button_xpath))
        )
        agree_button.click()
    except TimeoutException:
        print("No cookies popup found.")


def find_given_elements(browser, xpath_in, timeout=10):
    """
    Waits for and returns all elements matching the given XPath.

    :param browser: Selenium WebDriver instance
    :param xpath_in: XPath string to locate elements
    :param timeout: seconds to wait for presence
    :return: list of WebElement objects
    """
    WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath_in))
    )
    return browser.find_elements(By.XPATH, xpath_in)


def click_show_all(browser, selectors, parent_div_in):
    """
    Clicks the 'Show All' button inside a given parent element if present.

    :param browser: Selenium WebDriver instance
    :param selectors: dict containing 'show_all_button' XPath
    :param parent_div_in: WebElement representing the parent container
    """
    try:
        show_all_xpath = selectors.get("show_all_button")
        if not show_all_xpath:
            return

        buttons = parent_div_in.find_elements(By.XPATH, show_all_xpath)
        if buttons:
            button = buttons[0]
            browser.execute_script("arguments[0].scrollIntoView(true);", button)
            browser.execute_script("arguments[0].click();", button)
    except Exception as e:
        print(f"Issue with clicking 'Show All': {e}")


def is_login_modal_present(browser, selectors, timeout=5):
    """
    Checks if a login modal is present on the page.

    :param browser: Selenium WebDriver instance
    :param selectors: dict containing 'login_modal' XPath
    :param timeout: seconds to wait for modal
    :return: True if modal is found, False otherwise
    """
    modal_xpath = selectors.get("login_modal")
    if not modal_xpath:
        return False

    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.XPATH, modal_xpath))
        )
        return True
    except TimeoutException:
        return False