"""Unit tests for the login workflow."""

from unittest.mock import MagicMock

from selenium.common.exceptions import TimeoutException, WebDriverException

from src.config import Config
from src.login import LoginResult, login, verify_login


CONFIG = Config(
    login_url="https://example.test/login",
    username="alice",
    password="secret",
    username_selector=("name", "username"),
    password_selector=("name", "password"),
    login_button_selector=("css selector", "button[type='submit']"),
    success_url_contains="/dashboard",
    wait_timeout=1,
)


def test_verify_login_accepts_expected_url():
    driver = MagicMock(current_url="https://example.test/dashboard")

    assert verify_login(driver, CONFIG) is True


def test_verify_login_accepts_success_element(monkeypatch):
    config = CONFIG.__class__(**{**CONFIG.__dict__, "success_check_type": "element", "success_selector": ("id", "account")})
    driver = MagicMock(current_url="https://example.test/login")
    driver.find_elements.return_value = [MagicMock()]

    assert verify_login(driver, config) is True


def test_verify_login_rejects_unexpected_url():
    driver = MagicMock(current_url="https://example.test/login?error=1")

    assert verify_login(driver, CONFIG) is False


def test_login_returns_success_for_completed_workflow(monkeypatch):
    driver = MagicMock(current_url="https://example.test/login")
    username = MagicMock()
    password = MagicMock()
    button = MagicMock()
    driver.get.return_value = None

    elements = iter([username, password, button])
    monkeypatch.setattr(
        "src.login._wait",
        lambda *_args: MagicMock(
            until=lambda _condition: next(elements)
        ),
    )
    monkeypatch.setattr("src.login.verify_login", lambda *_args: True)

    result = login(driver, CONFIG)

    assert result == LoginResult(True, True, "Login successful!", "verification")
    username.send_keys.assert_called_once_with("alice")
    password.send_keys.assert_called_once_with("secret")
    button.click.assert_called_once()


def test_login_reports_navigation_failure():
    driver = MagicMock()
    driver.get.side_effect = WebDriverException("network unavailable")

    result = login(driver, CONFIG)

    assert result == LoginResult(False, False, "Could not open the configured login URL.", "navigation")


def test_login_converts_timeout_to_clear_result(monkeypatch):
    driver = MagicMock()
    wait = MagicMock()
    wait.until.side_effect = TimeoutException()
    monkeypatch.setattr("src.login._wait", lambda *_args: wait)

    result = login(driver, CONFIG)

    assert result.submitted is False
    assert result.stage == "element"
    assert "Timed out" in result.message
