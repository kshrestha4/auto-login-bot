"""Logging setup for the application."""

import logging


def configure_logging() -> None:
    """Configure human-readable informational logs once at application startup."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
