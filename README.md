# DracoFusion 101 – Multi-User Selenium Automation

This repository contains a fully automated end-to-end test for the “Okey 101” game on the DracoFusion web client.  
The test starts real browser sessions, registers new users, logs them in, navigates to the 101 lobby, creates a game table as a host, joins that table with guest players, and waits until the game ends (host returns to the lobby).

It is designed to run both locally and in GitHub Actions CI, with support for multiple simultaneous tables via a matrix strategy.

---

## Key features

- Python + Selenium based browser automation.
- Automatic user creation with unique email/username for every run.
- Configurable number of guest players per table:
    - `--guests 1` → 2-player table (1 host + 1 guest)
    - `--guests 3` → 4-player table (1 host + 3 guests)
- Robust registration and login flows with timeouts and fallbacks tuned for CI.
- Navigation to Okey 101 lobby, including iframe handling.
- Host-side table creation with:
    - Unique table names (timestamp + random suffix).
    - 2- or 4-player configuration depending on guest count.
- Guest table join: each guest sits at the correct host table, not a random one.
- Nickname entry screen handling for all players.
- Game end detection: script waits until the host is automatically returned to the lobby, then shuts everything down.
- CI-friendly:
    - Headless Chrome through `webdriver-manager`.
    - Optional “human delay” typing and sleeps that can be disabled in CI.
    - GitHub Actions workflow examples for scheduled, parallel multi-table runs.

---

## Project structure

Typical layout (simplified):

```text
.
├── common/
│   └── browser_utils.py        # WebDriver setup (Chrome, options, timeouts, headless)
├── locators/
│   └── okey101_locators.py     # All Selenium locators (XPaths) for register/login/101 flows
├── .github/
│   └── workflows/
│       ├── okey101-manual.yml  # Example manual CI workflow (single run)
│       └── okey101-4p-30min.yml (or similar)  # Scheduled multi-table workflow
├── 101.py                      # Main multi-user Okey 101 scenario (host + guests)
├── main.py                     # Thin wrapper used by CI; passes --guests into 101.py
├── requirements.txt            # Python dependencies
└── README.md                   # This file


Browser utilities

common/browser_utils.py:

Creates a Chrome WebDriver using webdriver-manager.

Uses BASE_URL env var (defaults to https://skin.dracofusion.com/).

Enables headless mode and CI flags when CI=1 is set.

Locators

locators/okey101_locators.py defines:

Registration locators (open button, inputs, submit, modal root).

Login locators (header button, inputs, submit, modal root).

Okey 101 locators (101 banner, create-table button, form fields, nickname input/button).

All flows refer to these constants instead of hard-coding XPaths.

Scenario logic (101.py)

Key elements:

Player dataclass bundles role, driver, wait, email, username, password.

generate_valid_credentials() builds unique email/username using timestamp + random number.

generate_table_name() builds unique table names such as auto_table_73842159.

Main steps:

create_player(role)

Opens browser.

Registers new user.

Logs in if the login button is visible.

Returns a Player instance.

go_to_101_lobby(player)

Clicks the 101 banner.

Locates the lobby’s create-table button, switching into iframes if needed.

host_create_table(host, total_players)

Opens the create-table modal.

Fills unique table name and bet amount.

Selects 2-player or 4-player table based on total_players.

Submits the form and returns the table name.

guest_join_table(guest, table_name)

Locates the lobby row whose first column equals table_name.

Clicks the Sit/Otur button in that row.

enter_table_nickname(player, nickname)

Finds the nickname input (current context or iframes).

Types nickname, submits, waits for the nickname screen to disappear.

wait_for_game_end(host, poll_interval, max_wait_minutes)

Periodically checks if the 101 lobby is visible again for the host.

When visible (or timeout exceeded), ends the run.

All WebDrivers are closed in a finally block in main().

Command-line usage

101.py expects a --guests argument:

# 1 host + 1 guest (2-player table)
python 101.py --guests 1

# 1 host + 3 guests (4-player table)
python 101.py --guests 3


Rules:

--guests must be 1 or 3.

On invalid or missing values, the script prints usage info and exits with code 1.

main.py is a thin wrapper; CI workflows call:

python main.py --guests 3


which internally runs 101.py with the same argument.

Local setup

Create environment and install dependencies:

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt


(Optional) Configure base URL:

export BASE_URL="https://skin.dracofusion.com/"


Run a test:

# 4-player table
python 101.py --guests 3


To mimic CI behaviour (no “human” delays, headless etc.), set:

export CI=1
python 101.py --guests 3

GitHub Actions usage

A minimal workflow to run one table on schedule or manually:

name: DracoFusion 101 – CI run

on:
  schedule:
    - cron: "0,30 * * * *"       # every 30 minutes (UTC)
  workflow_dispatch:

jobs:
  run-101:
    runs-on: ubuntu-latest
    env:
      PYTHONUNBUFFERED: "1"     # live logs
      GUESTS: "3"
      BASE_URL: https://skin.dracofusion.com/

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run 101 multi-user flow
        run: |
          echo "Running 101.py with $GUESTS guests..."
          python -u main.py --guests "$GUESTS"


To run several tables in parallel, add a strategy.matrix section and optionally max-parallel to control concurrency.

Notes

All XPaths are centralized in locators/okey101_locators.py.
If the UI changes, updating that file is usually sufficient.

The test tolerates slower responses by using longer explicit waits and by not failing immediately when the registration modal does not close fast enough.

Unique credentials and table names are generated per run, so it is safe to execute under high parallel load in CI.
