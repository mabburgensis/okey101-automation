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
