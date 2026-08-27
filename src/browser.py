"""Chrome WebDriver lifecycle helpers."""

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


def create_driver(headless: bool = False) -> webdriver.Chrome:
    """Start Chrome; Selenium Manager resolves a compatible driver automatically."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    else:
        options.add_argument("--start-maximized")
    try:
        return webdriver.Chrome(options=options)
    except WebDriverException as exc:
        raise RuntimeError(
            "Could not start Chrome. Confirm Google Chrome is installed and try again."
        ) from exc


def close_driver(driver: webdriver.Chrome | None) -> None:
    """Close the browser if it was successfully created."""
    if driver is not None:
        try:
            driver.quit()
        except WebDriverException:
            # Cleanup should not hide the original login error.
            pass
