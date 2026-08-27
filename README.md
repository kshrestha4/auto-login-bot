# Python Auto-Login Bot

A beginner-friendly Selenium 4 example that opens an authorized login page, enters credentials from a local `.env` file, submits the form, and verifies success using a configurable URL fragment.

> Use this only with websites and accounts you are authorized to automate. This project does not bypass CAPTCHA, MFA/2FA, bot detection, rate limits, or access controls. If CAPTCHA or MFA appears, stop and complete it manually.

## Features

- Opens a website in Google Chrome
- Uses Selenium Manager to find a compatible ChromeDriver where supported
- Loads credentials with `python-dotenv`
- Keeps secrets out of Python source and Git
- Uses Selenium 4 `By`, `WebDriverWait`, and expected conditions
- Configurable username, password, button, and success selectors
- Handles configuration, timeout, browser, and Selenium errors
- Includes unit tests that do not contact a live website
- Logs useful progress without logging the password

## Requirements

- Python 3.10 or newer recommended
- Google Chrome installed
- Internet access on the first Selenium run so Selenium Manager can resolve the driver when needed
- A login flow you are authorized to automate

## Installation on Windows PowerShell

Clone the repository and enter it:

```powershell
git clone <repository-url>
cd auto-login-bot
```

Create a virtual environment. A virtual environment gives this project its own isolated Python packages:

```powershell
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you may need to change your user execution policy according to your organization's policy. You can also run commands through `venv\Scripts\python.exe` without activating it.

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`pip` is Python's package installer. `requirements.txt` makes the dependencies reproducible for another developer.

## Configuration

Copy the safe template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace every placeholder:

```env
LOGIN_USERNAME=your_username
LOGIN_PASSWORD=your_password
LOGIN_URL=https://example.com/login

USERNAME_SELECTOR_TYPE=name
USERNAME_SELECTOR_VALUE=username
PASSWORD_SELECTOR_TYPE=name
PASSWORD_SELECTOR_VALUE=password
LOGIN_BUTTON_SELECTOR_TYPE=css selector
LOGIN_BUTTON_SELECTOR_VALUE=button[type='submit']
SUCCESS_URL_CONTAINS=/dashboard
WAIT_TIMEOUT_SECONDS=15
DRY_RUN=false
```

Never paste real credentials into `config.py`, `main.py`, tests, logs, or chat messages. `.env` is ignored by Git and must never be committed to GitHub. `.env.example` contains placeholders only and is safe to commit.

## Finding selectors

The example selectors are not universal. The configuration module converts each readable selector type and value into Selenium's `(By, value)` format. On an authorized website:

1. Right-click the username field and choose **Inspect**.
2. Look for a stable `id` or `name`, such as `name="username"`.
3. Inspect the password field and submit button in the same way.
4. Put the selector strategy in `*_SELECTOR_TYPE` and its value in `*_SELECTOR_VALUE`.

Examples:

- `id` + `email` becomes `(By.ID, "email")`.
- `name` + `username` becomes `(By.NAME, "username")`.
- `css selector` + `button[type='submit']` becomes a CSS selector matching a submit button.
- `xpath` can express relationships, but CSS selectors are usually shorter and easier to maintain.

A selector is an instruction for locating an element in the page's DOM (the browser's tree representation of HTML). Prefer stable, specific attributes over fragile generated class names. If several elements match, make the selector more specific.

## Safe dry run

Set `DRY_RUN=true` to validate the configuration without starting Chrome or submitting a login. This is useful when learning selectors or checking a new `.env` file. Set it back to `false` for an actual authorized browser run. Set `HEADLESS=true` only when you want Chrome to run without a visible window, such as in CI; visible Chrome is the default for easier learning and debugging.

## Running

Activate the environment, configure `.env`, then run:

```powershell
python main.py
```

Expected progress includes messages such as `Opening login page`, `Username field located`, `Submitting login`, and either `Login successful!` or `Login could not be verified.` The password is never printed.

The default verification checks whether the current URL contains `/dashboard`. Change `SUCCESS_URL_CONTAINS` to the fragment used by your authorized site. If the site stays on the same URL, set `SUCCESS_CHECK_TYPE=element` and configure `SUCCESS_SELECTOR_TYPE` and `SUCCESS_SELECTOR_VALUE`. `either` accepts whichever check succeeds first.

## How the code connects

- `main.py` is the entry point. It coordinates configuration, browser startup, login, result reporting, and cleanup.
- `src/config.py` is a module responsible for environment variables, validation, and converting readable selector settings into Selenium `(By, value)` tuples.
- `src/browser.py` creates Chrome with Selenium Manager and closes it safely.
- `src/login.py` performs the workflow and returns a small `LoginResult` instead of exposing browser details to `main.py`.
- `src/logger.py` configures readable application logs.
- `tests/` contains fast unit tests using mocks; they do not prove that a particular live site works. Browser option tests verify lifecycle behavior without launching Chrome.

Functions keep each job small and modules group related functions. Imports connect those modules without placing everything in one large script.

## Why explicit waits?

Web pages load asynchronously. `WebDriverWait(...).until(...)` waits only as long as needed for visibility or clickability and then times out with a controlled exception. Arbitrary `time.sleep()` calls are slower and still unreliable, so this project avoids them.

## Testing

Run the unit tests:

```powershell
pytest
```

These tests cover configuration validation, selector conversion, URL verification, successful workflow orchestration, and timeout handling. They intentionally do not submit credentials to a website. A live browser test should be added separately only with a safe test account and explicit authorization.

## Troubleshooting

### Configuration error

Confirm `.env` exists in the project root, has no missing required values, and uses the exact variable names from `.env.example`. Do not add quotes unless the value genuinely needs them.

### Chrome will not start

Confirm Google Chrome is installed and close incompatible or locked browser sessions. Selenium 4 uses Selenium Manager to obtain the driver where possible; manually installing ChromeDriver should be a last resort when a managed environment requires it.

### Timeout while locating an element

Inspect the page again. The field may be inside an iframe, appear only after another action, use a different attribute, or be blocked by a consent dialog. This basic project does not automatically bypass those conditions.

### Login cannot be verified

The login may have failed, the success URL may be different, or the site may use an element rather than a URL change. Update `SUCCESS_URL_CONTAINS` or extend `verify_login` for the site's documented success indicator.

### CAPTCHA or MFA appears

Stop automation. Complete the challenge manually if appropriate, or use the site's supported automation/API process. Do not attempt to bypass security controls.

For deeper debugging, run with Python logging enabled or inspect the exception details in a debugger. Never enable logging that prints credential values.

## Security

Credentials are secrets. `.env` is ignored locally, but still check `git status` and `git ls-files` before pushing. If a secret is ever committed, remove it from the repository history and rotate the credential; deleting the file in a later commit is not sufficient.

Do not store authenticated Chrome profiles, cookies, tokens, screenshots containing sensitive data, or production credentials in this repository.

## Git workflow

Make one meaningful commit per coherent change. Before committing:

```powershell
git status
git diff
pytest
git add <specific-files>
git commit -m "Describe the development step"
```

Review the identity and remote before pushing:

```powershell
git config user.name
git config user.email
git remote -v
git push origin main
```

Do not push to a repository or account you have not confirmed.

## Project limitations and future improvements

This is intentionally a small learning project. It does not support arbitrary site layouts, iframes, SSO flows, CAPTCHA/MFA automation, retries against rate limits, or secure secret managers. Possible authorized improvements include element-based success verification, a dry-run mode, structured JSON logs, a test HTML fixture, and integration with an organization-approved secret store.
