"""Unit tests for configuration loading."""

import pytest

from src.config import ConfigurationError, load_config


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


def test_invalid_timeout_has_actionable_error(monkeypatch):
    set_values(monkeypatch)
    monkeypatch.setenv("WAIT_TIMEOUT_SECONDS", "fast")

    with pytest.raises(ConfigurationError, match="whole number"):
        load_config(env_path="/path/that/does/not/exist")
