"""
Step definitions — features/billing.feature

Numbers in the feature file are parsed with `:g` so the same step accepts
integers and decimals (1000, 0.333, -75.00). Money assertions compare to
2-decimal values, matching the "accurate to the cent" intent.
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("billing.feature")

SUBMETER_STEP = ("I calculate a submeter charge from reading {prev:g} to {curr:g} "
                 "at rate {rate:g} with multiplier {mult:g}")
HVAC_STEP = ('I calculate an HVAC charge from "{start}" to "{end}" '
             "at hourly rate {rate:g} with a minimum of {min_hours:g} hours")


# ======================================================================
# GIVEN
# ======================================================================
@given("the Genea billing system", target_fixture="billing")
def billing(billing_system):
    return billing_system


# ======================================================================
# WHEN — happy path (result stored; several results may accumulate)
# ======================================================================
@when(parsers.parse(SUBMETER_STEP))
def calc_submeter(billing, ctx, prev, curr, rate, mult):
    result = billing.calculate_submeter_charge(prev, curr, rate, mult)
    ctx["result"] = result
    ctx.setdefault("results", []).append(result)


@when(parsers.parse(HVAC_STEP))
def calc_hvac(billing, ctx, start, end, rate, min_hours):
    result = billing.calculate_hvac_charge(start, end, rate, min_hours)
    ctx["result"] = result
    ctx.setdefault("results", []).append(result)


# ======================================================================
# WHEN — negative path (error captured, not raised)
# ======================================================================
@when(parsers.parse("I try to " + SUBMETER_STEP.removeprefix("I ")))
def try_submeter(billing, ctx, prev, curr, rate, mult):
    with pytest.raises(ValueError) as exc:
        billing.calculate_submeter_charge(prev, curr, rate, mult)
    ctx["error"] = exc.value


@when(parsers.parse("I try to " + HVAC_STEP.removeprefix("I ")))
def try_hvac(billing, ctx, start, end, rate, min_hours):
    with pytest.raises(ValueError) as exc:
        billing.calculate_hvac_charge(start, end, rate, min_hours)
    ctx["error"] = exc.value


# ======================================================================
# THEN
# ======================================================================
@then(parsers.parse("the charge is {expected:g}"))
def charge_is(ctx, expected):
    assert ctx["result"]["charge"] == round(expected, 2)


@then(parsers.parse("the consumption is {expected:g}"))
def consumption_is(ctx, expected):
    assert ctx["result"]["consumption"] == expected


@then(parsers.parse("the applied hours are {expected:g}"))
def applied_hours_are(ctx, expected):
    assert ctx["result"]["applied_hours"] == expected


@then("the billing request is rejected as invalid")
def billing_rejected(ctx):
    assert isinstance(ctx["error"], ValueError)


@then("every calculated charge has at most two decimal places")
def charges_rounded(ctx):
    for result in ctx["results"]:
        assert result["charge"] == round(result["charge"], 2)
