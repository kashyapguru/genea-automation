"""
Mock Genea Billing System
=========================
In-memory stand-in for Genea's two billing-related products:

  1. Submeter Billing      — meter reading -> tenant utility charge
  2. On-Demand / Overtime HVAC — after-hours HVAC request -> itemized charge

Billing is where the business/legal RISK lives (disputes, lawsuits over wrong
charges), so the test focus is CALCULATION ACCURACY to the cent. Genea's own
published case study involved a wrong multiplier — exactly the kind of defect
these tests target.

In a real engagement these methods would call Genea's billing API; the
data-driven test cases and assertions would be identical.
"""

from datetime import datetime


class GeneaBillingSystem:

    # ==================================================================
    # SUBMETER BILLING
    # ==================================================================
    def calculate_submeter_charge(self, prev_reading, curr_reading,
                                  rate_per_unit, multiplier=1):
        """
        Calculate a tenant's submeter utility charge.

        consumption = (curr_reading - prev_reading) * multiplier
        charge      = consumption * rate_per_unit

        The `multiplier` models CT/meter multipliers (a real source of billing
        errors). Raises on invalid input (e.g. a meter that went backwards).
        """
        if curr_reading < prev_reading:
            raise ValueError("current reading cannot be less than previous reading")
        if rate_per_unit < 0 or multiplier <= 0:
            raise ValueError("rate and multiplier must be positive")

        consumption = (curr_reading - prev_reading) * multiplier
        charge = round(consumption * rate_per_unit, 2)
        return {
            "consumption": consumption,
            "rate_per_unit": rate_per_unit,
            "multiplier": multiplier,
            "charge": charge,
        }

    # ==================================================================
    # AFTER-HOURS (OVERTIME) HVAC BILLING
    # ==================================================================
    def calculate_hvac_charge(self, start_time, end_time, hourly_rate,
                              minimum_hours=0):
        """
        Calculate an after-hours HVAC charge from a request window.

        duration_hours = (end - start) in hours, billed to the applied hours
        (never below `minimum_hours`). charge = applied_hours * hourly_rate.

        start_time / end_time are 'HH:MM' 24h strings on the same day.
        """
        fmt = "%H:%M"
        start = datetime.strptime(start_time, fmt)
        end = datetime.strptime(end_time, fmt)
        if end <= start:
            raise ValueError("end_time must be after start_time")
        if hourly_rate < 0:
            raise ValueError("hourly_rate must be positive")

        duration_hours = (end - start).seconds / 3600
        applied_hours = max(duration_hours, minimum_hours)
        charge = round(applied_hours * hourly_rate, 2)
        return {
            "duration_hours": round(duration_hours, 2),
            "applied_hours": round(applied_hours, 2),
            "hourly_rate": hourly_rate,
            "charge": charge,
        }
