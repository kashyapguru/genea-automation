"""
Step definitions — features/access_control_api.feature

Thin glue between the Gherkin steps and the access-control system. Business
language lives in the .feature file; this module only translates it.
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("access_control_api.feature")


# ======================================================================
# GIVEN
# ======================================================================
@given("a fresh Genea access control system", target_fixture="system")
def fresh_system(access_system):
    return access_system


@given(parsers.parse('a "{cred_type}" credential has been provisioned for "{user}" '
                     'at door group "{door}"'))
def credential_provisioned(system, ctx, cred_type, user, door):
    cred = system.provision_credential(user, door, cred_type)
    ctx.setdefault("by_user", {})[user] = cred
    ctx["credential"] = cred          # most recent one is "the credential"


# ======================================================================
# WHEN
# ======================================================================
@when(parsers.parse('I provision a "{cred_type}" credential for "{user}" '
                    'at door group "{door}"'))
def provision(system, ctx, cred_type, user, door):
    cred = system.provision_credential(user, door, cred_type)
    ctx.setdefault("by_user", {})[user] = cred
    ctx["credential"] = cred


# Regex (not parse) so that an EMPTY user or door group still matches the step.
@when(parsers.re(r'I try to provision a credential for "(?P<user>.*?)" at door group "(?P<door>.*?)"'))
def try_provision(system, ctx, user, door):
    with pytest.raises(ValueError) as exc:
        system.provision_credential(user, door)
    ctx["error"] = exc.value


@when(parsers.parse('I try to provision a "{cred_type}" credential for "{user}" '
                    'at door group "{door}"'))
def try_provision_with_type(system, ctx, cred_type, user, door):
    with pytest.raises(ValueError) as exc:
        system.provision_credential(user, door, cred_type)
    ctx["error"] = exc.value


@when("I revoke the credential")
def revoke_current(system, ctx):
    cid = ctx["credential"]["credential_id"]
    ctx["credential"] = system.revoke_credential(cid)


@when(parsers.parse('I revoke the credential of "{user}"'))
def revoke_for_user(system, ctx, user):
    cid = ctx["by_user"][user]["credential_id"]
    ctx["by_user"][user] = system.revoke_credential(cid)


@when(parsers.parse('I try to revoke credential "{cred_id}"'))
def try_revoke_unknown(system, ctx, cred_id):
    with pytest.raises(KeyError) as exc:
        system.revoke_credential(cred_id)
    ctx["error"] = exc.value


# ======================================================================
# THEN
# ======================================================================
def _current(system, ctx):
    """Always re-read from the system so assertions reflect real state."""
    return system.get_credential(ctx["credential"]["credential_id"])


@then(parsers.parse('the credential status is "{status}"'))
def credential_status(system, ctx, status):
    assert _current(system, ctx)["status"] == status


@then(parsers.parse('the credential belongs to "{user}" at door group "{door}"'))
def credential_owner(system, ctx, user, door):
    cred = _current(system, ctx)
    assert cred["user"] == user
    assert cred["door_group"] == door


@then(parsers.parse('the credential id starts with "{prefix}"'))
def credential_id_prefix(ctx, prefix):
    assert ctx["credential"]["credential_id"].startswith(prefix)


@then(parsers.parse('the credential type is "{cred_type}"'))
def credential_type(system, ctx, cred_type):
    assert _current(system, ctx)["type"] == cred_type


@then("the credential records a revocation timestamp")
def credential_has_revoked_at(system, ctx):
    assert "revoked_at" in _current(system, ctx)


# Used as both Given (precondition) and Then (assertion) in the feature.
@given(parsers.parse('presenting the credential at "{door}" is granted'))
@then(parsers.parse('presenting the credential at "{door}" is granted'))
def unlock_granted(system, ctx, door):
    assert system.attempt_unlock(ctx["credential"]["credential_id"], door) is True


@then(parsers.parse('presenting the credential at "{door}" is denied'))
def unlock_denied(system, ctx, door):
    assert system.attempt_unlock(ctx["credential"]["credential_id"], door) is False


@then(parsers.parse('the credential of "{user}" has status "{status}"'))
def user_credential_status(system, ctx, user, status):
    cid = ctx["by_user"][user]["credential_id"]
    assert system.get_credential(cid)["status"] == status


@then(parsers.parse('presenting the credential of "{user}" at "{door}" is granted'))
def user_unlock_granted(system, ctx, user, door):
    cid = ctx["by_user"][user]["credential_id"]
    assert system.attempt_unlock(cid, door) is True


@then("provisioning is rejected with a validation error")
def provisioning_rejected(ctx):
    assert isinstance(ctx["error"], ValueError)


@then("revocation fails because the credential was not found")
def revocation_not_found(ctx):
    assert isinstance(ctx["error"], KeyError)


@then("the audit trail contains the events:")
def audit_trail_contains(system, datatable):
    # datatable: first row is the header ("event"), remaining rows are values
    expected = {row[0] for row in datatable[1:]}
    recorded = {e[0] for e in system.events}
    missing = expected - recorded
    assert not missing, f"audit trail missing events: {sorted(missing)}"
