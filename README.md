# Genea Demo Automation Suite — BDD / Gherkin edition

The same demonstration suite for two of **Genea's core products**, re-expressed
as **executable Gherkin specifications** (Behaviour-Driven Development) using
`pytest-bdd` + Playwright:

- **Access Control** — the credential lifecycle (provision / revoke), at **API and UI** layers
- **Billing** — **submeter billing** and **after-hours HVAC** charge accuracy

Plus a **GitHub Actions CI/CD pipeline** whose quality gates are selected by
Gherkin `@tags`.

> Demo/portfolio artifact. Runs against self-contained **mocks** of Genea's
> systems, so it executes anywhere with no access to the real application.
> Against the real product you'd swap the mock fixtures in `tests/conftest.py`
> for a thin REST client (and a real URL + login for the UI). The **feature
> files and step definitions stay the same** — that's the point of BDD.

## Why Gherkin?

The original pytest suite encoded the *what* and the *why* in docstrings and
comments. Gherkin moves that into first-class, readable specifications:

| Concern | pytest suite | BDD suite |
|---|---|---|
| Business intent | docstrings | `Feature:` narrative + `Scenario:` titles |
| Test data | `@pytest.mark.parametrize` | `Scenario Outline` + `Examples:` tables |
| Risk prioritisation | comments | `@security`, `@isolation`, `@negative` tags |
| Reuse | helper functions | shared step definitions (one step, many scenarios) |
| CI gate selection | file paths | tag/marker expressions (`-m "api and billing"`) |
| Reporting | pytest output | pytest output **and** `cucumber.json` living docs |

Product owners, QA and developers can read, review and extend the `.feature`
files without reading Python. Adding a billing edge case is a new row in an
`Examples:` table; it is executed automatically and lands in the right CI gate
because of its tags.

## What's covered (38 scenarios)

**`features/access_control_api.feature`** (12 scenarios, `@api @access_control`)
Provision, revoke, authorization (can't open other doors), **revoked access
stops working**, invalid input, isolation, full lifecycle with audit trail.

**`features/access_control_ui.feature`** (8 scenarios, `@ui @access_control`)
Provision + revoke through the admin console, status changes, toasts, error
handling, full lifecycle with isolation. Driven by Playwright.

**`features/billing.feature`** (18 scenarios, `@api @billing`)
Submeter charge accuracy (data-driven), **multiplier applied correctly**,
backwards-meter rejection; HVAC charge accuracy, minimum-hours billing,
invalid-window rejection; money always rounded to the cent.

## Structure

```
genea-demo-bdd/
├── features/                              # Gherkin specs (the source of truth)
│   ├── access_control_api.feature
│   ├── access_control_ui.feature
│   └── billing.feature
├── tests/
│   ├── conftest.py                        # fixtures: fresh system per scenario, Playwright page
│   └── step_defs/                         # thin glue: step text -> mock/API call -> assertion
│       ├── test_access_control_api_steps.py
│       ├── test_access_control_ui_steps.py
│       └── test_billing_steps.py
├── mock/
│   ├── genea_access_system.py             # access-control backend stand-in
│   └── genea_billing_system.py            # billing backend stand-in
├── ui/genea_admin.html                    # mock admin console (for UI scenarios)
├── .github/workflows/qa-pipeline.yml      # CI/CD with tag-driven staged gates
├── pytest.ini                             # feature dir + registered markers
├── requirements.txt
└── README.md
```

## Running locally

```bash
pip install -r requirements.txt
playwright install chromium          # for the UI feature

pytest                               # all 38 scenarios
pytest -m api                        # access-control API + billing (30)
pytest -m ui                         # Playwright scenarios (8)
pytest -m "api and billing"          # billing only (18)
pytest -m security                   # the highest-risk assertions only
pytest -m "negative"                 # every invalid-input scenario across features
pytest -v                            # scenario titles become readable test names

# Living-documentation report (Cucumber JSON, consumable by any Cucumber reporter)
mkdir -p reports && pytest --cucumberjson=reports/cucumber.json
```

All scenarios pass out of the box — no API key, no real app, no network.

## How a scenario maps to code

```gherkin
@revoking @security
Scenario: A revoked credential can no longer unlock its door
  Given a "card" credential has been provisioned for "heidi@corp.com" at door group "Lobby"
  And presenting the credential at "Lobby" is granted
  When I revoke the credential
  Then presenting the credential at "Lobby" is denied
```

```python
@when("I revoke the credential")
def revoke_current(system, ctx):
    ctx["credential"] = system.revoke_credential(ctx["credential"]["credential_id"])

@then(parsers.parse('presenting the credential at "{door}" is denied'))
def unlock_denied(system, ctx, door):
    assert system.attempt_unlock(ctx["credential"]["credential_id"], door) is False
```

Step definitions use `parsers.parse` (typed placeholders such as `{rate:g}`) so
one step serves every row of an `Examples:` table. Where a value may legally be
empty (missing user / door group), a `parsers.re` regex is used instead.

## CI/CD pipeline (GitHub Actions)

`.github/workflows/qa-pipeline.yml` runs on every push/PR with **staged quality
gates selected by tag**:

1. **API Scenarios** — `-m "api and access_control"`, `-m "api and billing"`, then `-m security` re-run as an explicit gate
2. **UI Scenarios** — `-m ui` with Playwright, only if gate 1 passed; uploads traces on failure
3. **Full Suite** — all features + `cucumber.json` living-docs artifact; only if both prior gates passed

A broken gate blocks promotion — quality is enforced in the pipeline, not hoped for.

## Design notes (the QA thinking)

- **Specification first** — the `.feature` files are readable by non-engineers and double as living documentation; the Cucumber JSON report can feed any BDD reporting tool.
- **API-first** — the bulk of coverage is at the API layer (Postman / API-validation focus); UI covers critical user journeys.
- **Risk-prioritised** — `@security` and `@isolation` tags make the highest-value assertions (revoked-access-stops-working, door authorization, one user's revocation not touching another) individually runnable and gate-able.
- **Data-driven billing** — `Scenario Outline` tables catch calculation errors across many inputs, including the multiplier bug class; a `note` column documents each row's intent.
- **Resilient, isolated** — fresh fixtures per scenario, Playwright web-first assertions, test-id locators, parallel-safe (`pytest -n auto` with `pytest-xdist` works unchanged).
- **Shift-left in CI** — staged, tag-driven gates give fast feedback and block bad changes.
