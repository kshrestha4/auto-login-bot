"""Unit tests for configuration loading."""

import pytest

from src.config import ConfigurationError, load_config, parse_selector


VALUES = {
    "LOGIN_URL": "https://example.test/login",
    "LOGIN_USERNAME": "alice",
    "LOGIN_PASSWORD": "not-printed",
    "USERNAME_SELECTOR_TYPE": "name",
    "USERNAME_SELECTOR_VALUE": "username",
    "PASSWORD_SELECTOR_TYPE": "id",
    "PASSWORD_SELECTOR_VALUE": "password",
    "LOGIN_BUTTON_SELECTOR_TYPE": "css",
    "LOGIN_BUTTON_SELECTOR_VALUE": "button[type='submit']",
    "SUCCESS_URL_CONTAINS": "/dashboard",
}


def set_values(monkeypatch, values=VALUES):
    for key, value in values.items():
        monkeypatch.setenv(key, value)


@pytest.mark.parametrize(
    ("selector_type", "expected"),
    [("id", "id"), ("name", "name"), ("css", "css selector"), ("xpath", "xpath")],
)
def test_parse_selector_supports_common_strategies(selector_type, expected):
    assert parse_selector(selector_type, "target") == (expected, "target")


def test_parse_selector_rejects_empty_value():
    with pytest.raises(ConfigurationError, match="cannot be empty"):
        parse_selector("id", " ", "USERNAME")


def test_load_config_returns_validated_config(monkeypatch):
    set_values(monkeypatch)

    config = load_config(env_path="/path/that/does/not/exist")

    assert config.login_url == VALUES["LOGIN_URL"]
    assert config.username_selector == ("name", "username")
    assert config.password_selector == ("id", "password")
    assert config.login_button_selector == ("css selector", "button[type='submit']")


def test_missing_setting_has_actionable_error(monkeypatch):
    set_values(monkeypatch)
    monkeypatch.delenv("LOGIN_PASSWORD")

    with pytest.raises(ConfigurationError, match="LOGIN_PASSWORD"):
        load_config(env_path="/path/that/does/not/exist")


def test_invalid_selector_type_has_actionable_error(monkeypatch):
    set_values(monkeypatch)
    monkeypatch.setenv("USERNAME_SELECTOR_TYPE", "unsupported")

    with pytest.raises(ConfigurationError, match="Unsupported USERNAME selector"):
        load_config(env_path="/path/that/does/not/exist")


def test_element_success_check_loads_selector(monkeypatch):
    set_values(monkeypatch)
    monkeypatch.setenv("SUCCESS_CHECK_TYPE", "element")
    monkeypatch.setenv("SUCCESS_SELECTOR_TYPE", "id")
    monkeypatch.setenv("SUCCESS_SELECTOR_VALUE", "account")

    config = load_config(env_path="/path/that/does/not/exist")

    assert config.success_check_type == "element"
    assert config.success_selector == ("id", "account")


def test_invalid_success_check_type_has_actionable_error(monkeypatch):
    set_values(monkeypatch)
    monkeypatch.setenv("SUCCESS_CHECK_TYPE", "unknown")

    with pytest.raises(ConfigurationError, match="SUCCESS_CHECK_TYPE"):
        load_config(env_path="/path/that/does/not/exist")


def test_dry_run_is_parsed(monkeypatch):
    set_values(monkeypatch)
    monkeypatch.setenv("DRY_RUN", "true")

    assert load_config(env_path="/path/that/does/not/exist").dry_run is True


def test_invalid_dry_run_has_actionable_error(monkeypatch):
    set_values(monkeypatch)
    monkeypatch.setenv("DRY_RUN", "sometimes")

    with pytest.raises(ConfigurationError, match="DRY_RUN"):
        load_config(env_path="/path/that/does/not/exist")


def test_invalid_timeout_has_actionable_error(monkeypatch):
    set_values(monkeypatch)
    monkeypatch.setenv("WAIT_TIMEOUT_SECONDS", "fast")

    with pytest.raises(ConfigurationError, match="whole number"):
        load_config(env_path="/path/that/does/not/exist")
