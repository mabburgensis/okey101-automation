# DracoFusion 101 – Multi-User Selenium Automation

This repository contains a Python/Selenium suite that drives real browsers against the DracoFusion Okey 101 client.

The main scenario:

- Creates test users (host + guests) with unique credentials.
- Logs them in.
- Navigates to the Okey 101 lobby.
- Host creates a table (2 or 4 players).
- Guests join that specific table.
- All players enter nicknames and sit at the table.
- The script waits until the host returns to the lobby and then closes all browsers.

The same scenario runs locally and in GitHub Actions.

---

## Components

```text
.
├── 101.py                      # Main multi-user scenario (host + guests)
├── main.py                     # Simple runner used by CI (forwards --guests to 101.py)
├── requirements.txt            # Python dependencies
├── common/
│   └── browser_utils.py        # WebDriver setup (Chrome, headless in CI, BASE_URL handling)
├── locators/
│   └── okey101_locators.py     # All XPaths for register/login/101 UI
└── .github/
    └── workflows/              # Example GitHub Actions workflows
