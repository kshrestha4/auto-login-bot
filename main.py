"""Command-line entry point for the Python Auto-Login Bot."""

import logging

from src.browser import close_driver, create_driver
from src.config import ConfigurationError, load_config
from src.logger import configure_logging
from src.login import login

logger = logging.getLogger(__name__)


def main() -> int:
    configure_logging()
    logger.info("Starting Auto-Login Bot")
    driver = None
    try:
        logger.info("Loading configuration")
        config = load_config()
        logger.info("Starting Chrome")
        driver = create_driver()
        result = login(driver, config)
        if result.verified:
            logger.info(result.message)
            return 0
        logger.error(result.message)
        return 1
    except ConfigurationError as exc:
        logger.error("Configuration error: %s", exc)
        return 2
    except RuntimeError as exc:
        logger.error("Browser startup error: %s", exc)
        return 3
    except Exception:
        logger.exception("Unexpected error while running the bot")
        return 4
    finally:
        logger.info("Closing browser")
        close_driver(driver)


if __name__ == "__main__":
    raise SystemExit(main())
