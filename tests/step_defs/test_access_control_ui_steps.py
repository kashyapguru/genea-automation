"""
Step definitions — features/access_control_ui.feature

Playwright glue. Uses test-id locators and web-first, auto-retrying `expect`
assertions so no manual waits are needed. Against the real admin console
only the `page` fixture (URL + login) would change.
"""

from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("access_control_ui.feature")


def _grant(page, user, door, cred_type):
    page.get_by_test_id("user-input").fill(user)
    page.get_by_test_id("door-input").fill(door)
    page.get_by_test_id("type-select").select_option(label=cred_type)
    page.get_by_test_id("grant-btn").click()


# ======================================================================
# GIVEN
# ======================================================================
@given("the admin console is open", target_fixture="console")
def console_open(page):
    return page


@given(parsers.parse('"{cred_type}" access has been granted to "{user}" '
                     'for door group "{door}"'))
def access_already_granted(console, cred_type, user, door):
    _grant(console, user, door, cred_type)


# ======================================================================
# WHEN
# ======================================================================
@when(parsers.parse('I grant "{cred_type}" access to "{user}" for door group "{door}"'))
def grant_access(console, cred_type, user, door):
    _grant(console, user, door, cred_type)


@when(parsers.parse('I enter the user "{user}" and click Grant Access without a door group'))
def grant_without_door(console, user):
    console.get_by_test_id("user-input").fill(user)
    console.get_by_test_id("grant-btn").click()


@when(parsers.parse('I revoke access for "{user}"'))
def revoke_access(console, user):
    console.get_by_test_id(f"revoke-{user}").click()


# ======================================================================
# THEN  (several are also valid as Given preconditions)
# ======================================================================
@given(parsers.parse('the credential row for "{user}" shows status "{status}"'))
@then(parsers.parse('the credential row for "{user}" shows status "{status}"'))
def row_status(console, user, status):
    expect(console.get_by_test_id(f"status-{user}")).to_have_text(status)


@then(parsers.parse('the credential row for "{user}" contains "{text}"'))
def row_contains(console, user, text):
    expect(console.get_by_test_id(f"row-{user}")).to_contain_text(text)


@then(parsers.parse('there is no credential row for "{user}"'))
def no_row(console, user):
    expect(console.get_by_test_id(f"row-{user}")).to_have_count(0)


@then(parsers.parse('there is no Revoke button for "{user}"'))
def no_revoke_button(console, user):
    expect(console.get_by_test_id(f"revoke-{user}")).to_have_count(0)


@then(parsers.parse('a toast containing "{text}" is shown'))
def toast_shown(console, text):
    expect(console.get_by_test_id("toast")).to_contain_text(text)
