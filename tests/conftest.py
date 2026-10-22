"""
Shared fixtures for the Genea BDD suite.

Every scenario gets a FRESH system (isolation, parallel-safe) and a small
`ctx` dict that steps use to pass state between Given / When / Then.

Swapping the mocks for Genea's real REST API means changing ONLY these
fixtures — the .feature files and step definitions stay the same.
"""

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from mock.genea_access_system import GeneaAccessSystem  # noqa: E402
from mock.genea_billing_system import GeneaBillingSystem  # noqa: E402


@pytest.fixture
def ctx():
    """Scenario-scoped scratch space shared across steps."""
    return {}


@pytest.fixture
def access_system():
    return GeneaAccessSystem()


@pytest.fixture
def billing_system():
    return GeneaBillingSystem()


# ---- UI ---------------------------------------------------------------------
PAGE_URL = "file://" + os.path.join(ROOT, "ui", "genea_admin.html")


@pytest.fixture
def page():
    """A fresh Chromium page on the mock admin console, per scenario."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page()
        pg.goto(PAGE_URL)
        yield pg
        browser.close()
