"""Configuration loading for the auto-login bot."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv
from selenium.webdriver.common.by import By


class ConfigurationError(ValueError):
    """Raised when required bot configuration is missing or invalid."""


_SELECTOR_TYPES = {
    "id": By.ID,
    "name": By.NAME,
    "css selector": By.CSS_SELECTOR,
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
    "class name": By.CLASS_NAME,
    "tag name": By.TAG_NAME,
}


@dataclass(frozen=True)
class Config:
    """All settings required to run a login attempt."""

    login_url: str
    username: str
    password: str
    username_selector: Tuple[str, str]
    password_selector: Tuple[str, str]
    login_button_selector: Tuple[str, str]
    success_url_contains: str
    wait_timeout: int = 15


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigurationError(
            f"Missing required setting {name}. Copy .env.example to .env and fill it in."
        )
    return value


def _selector(prefix: str) -> Tuple[str, str]:
    selector_type = _required(f"{prefix}_SELECTOR_TYPE").lower()
    selector_value = _required(f"{prefix}_SELECTOR_VALUE")
    try:
        return _SELECTOR_TYPES[selector_type], selector_value
    except KeyError as exc:
        supported = ", ".join(sorted(_SELECTOR_TYPES))
        raise ConfigurationError(
            f"Unsupported {prefix} selector type {selector_type!r}. Use: {supported}."
        ) from exc


def load_config(env_path: str | Path | None = None) -> Config:
    """Load .env values and return validated configuration."""
    load_dotenv(dotenv_path=env_path)
    try:
        wait_timeout = int(os.getenv("WAIT_TIMEOUT_SECONDS", "15"))
    except ValueError as exc:
        raise ConfigurationError("WAIT_TIMEOUT_SECONDS must be a whole number.") from exc
    if wait_timeout <= 0:
        raise ConfigurationError("WAIT_TIMEOUT_SECONDS must be greater than zero.")

    return Config(
        login_url=_required("LOGIN_URL"),
        username=_required("LOGIN_USERNAME"),
        password=_required("LOGIN_PASSWORD"),
        username_selector=_selector("USERNAME"),
        password_selector=_selector("PASSWORD"),
        login_button_selector=_selector("LOGIN_BUTTON"),
        success_url_contains=_required("SUCCESS_URL_CONTAINS"),
        wait_timeout=wait_timeout,
    )
