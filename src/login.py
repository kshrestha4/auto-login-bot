"""Authorized website login workflow."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.ui import WebDriverWait

from .config import Config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoginResult:
    """Outcome of a login attempt."""

    submitted: bool
    verified: bool
    message: str


def _wait(driver: WebDriver, timeout: int) -> WebDriverWait:
    return WebDriverWait(driver, timeout)


def verify_login(driver: WebDriver, config: Config) -> bool:
    """Verify success by waiting for and checking the configured URL fragment."""
    try:
        _wait(driver, config.wait_timeout).until(
            lambda current_driver: config.success_url_contains
            in current_driver.current_url
        )
        return True
    except TimeoutException:
        return False


def login(driver: WebDriver, config: Config) -> LoginResult:
    """Navigate, fill, submit, and verify a login form."""
    try:
        logger.info("Opening login page")
        driver.get(config.login_url)

        username = _wait(driver, config.wait_timeout).until(
            expected.visibility_of_element_located(config.username_selector)
        )
        logger.info("Username field located")
        username.clear()
        username.send_keys(config.username)

        password = _wait(driver, config.wait_timeout).until(
            expected.visibility_of_element_located(config.password_selector)
        )
        logger.info("Password field located")
        password.clear()
        password.send_keys(config.password)

        button = _wait(driver, config.wait_timeout).until(
            expected.element_to_be_clickable(config.login_button_selector)
        )
        logger.info("Login button located")
        logger.info("Submitting login")
        button.click()

        verified = verify_login(driver, config)
        if verified:
            return LoginResult(True, True, "Login successful!")
        return LoginResult(True, False, "Login could not be verified.")
    except TimeoutException:
        return LoginResult(False, False, "Timed out while waiting for a login element or result.")
    except (NoSuchElementException, WebDriverException) as exc:
        logger.debug("Selenium failure details: %s", exc, exc_info=True)
        return LoginResult(False, False, "The browser could not complete the login workflow.")
