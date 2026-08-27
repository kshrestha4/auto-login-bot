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
    success_check_type: str = "url"
    success_selector: Tuple[str, str] | None = None
    wait_timeout: int = 15
    dry_run: bool = False


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigurationError(
            f"Missing required setting {name}. Copy .env.example to .env and fill it in."
        )
    return value


def parse_selector(selector_type: str, selector_value: str, name: str = "selector") -> Tuple[str, str]:
    """Convert a readable selector strategy and value into Selenium's tuple format."""
    normalized_type = selector_type.strip().lower()
    value = selector_value.strip()
    if not value:
        raise ConfigurationError(f"{name} selector value cannot be empty.")
    try:
        return _SELECTOR_TYPES[normalized_type], value
    except KeyError as exc:
        supported = ", ".join(sorted(_SELECTOR_TYPES))
        raise ConfigurationError(
            f"Unsupported {name} selector type {selector_type!r}. Use: {supported}."
        ) from exc


def _selector(prefix: str) -> Tuple[str, str]:
    return parse_selector(
        _required(f"{prefix}_SELECTOR_TYPE"),
        _required(f"{prefix}_SELECTOR_VALUE"),
        prefix,
    )


def load_config(env_path: str | Path | None = None) -> Config:
    """Load .env values and return validated configuration."""
    load_dotenv(dotenv_path=env_path)
    try:
        wait_timeout = int(os.getenv("WAIT_TIMEOUT_SECONDS", "15"))
    except ValueError as exc:
        raise ConfigurationError("WAIT_TIMEOUT_SECONDS must be a whole number.") from exc
    if wait_timeout <= 0:
        raise ConfigurationError("WAIT_TIMEOUT_SECONDS must be greater than zero.")
    dry_run_value = os.getenv("DRY_RUN", "false").strip().lower()
    if dry_run_value not in {"true", "false"}:
        raise ConfigurationError("DRY_RUN must be either true or false.")

    success_check_type = os.getenv("SUCCESS_CHECK_TYPE", "url").strip().lower()
    if success_check_type not in {"url", "element", "either"}:
        raise ConfigurationError("SUCCESS_CHECK_TYPE must be url, element, or either.")
    success_url_contains = _required("SUCCESS_URL_CONTAINS")
    success_selector = None
    if success_check_type in {"element", "either"}:
        success_selector = _selector("SUCCESS")

    return Config(
        login_url=_required("LOGIN_URL"),
        username=_required("LOGIN_USERNAME"),
        password=_required("LOGIN_PASSWORD"),
        username_selector=_selector("USERNAME"),
        password_selector=_selector("PASSWORD"),
        login_button_selector=_selector("LOGIN_BUTTON"),
        success_url_contains=success_url_contains,
        success_check_type=success_check_type,
        success_selector=success_selector,
        wait_timeout=wait_timeout,
        dry_run=dry_run_value == "true",
    )
