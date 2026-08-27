"""Unit tests for browser lifecycle helpers."""

from unittest.mock import MagicMock, patch

from src.browser import close_driver, create_driver


def test_create_driver_uses_headless_option():
    with patch("src.browser.webdriver.Chrome") as chrome:
        create_driver(headless=True)

    options = chrome.call_args.kwargs["options"]
    assert "--headless=new" in options.arguments


def test_create_driver_uses_maximized_option_by_default():
    with patch("src.browser.webdriver.Chrome") as chrome:
        create_driver()

    options = chrome.call_args.kwargs["options"]
    assert "--start-maximized" in options.arguments


def test_close_driver_quits_browser():
    driver = MagicMock()

    close_driver(driver)

    driver.quit.assert_called_once_with()


def test_close_driver_accepts_none():
    close_driver(None)
