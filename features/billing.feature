@api @billing
Feature: Billing — submeter and after-hours HVAC charge accuracy
  Billing = revenue. A wrong multiplier or a wrong duration becomes a billing
  dispute (Genea has a published case study about exactly a wrong-multiplier
  error), so these scenarios validate calculation accuracy to the cent.

  As a tenant billing operator
  I want utility and after-hours HVAC charges calculated exactly
  So that every invoice is correct to the cent and disputes are avoided

  Background:
    Given the Genea billing system

  # ------------------------------------------------------------------
  # SUBMETER BILLING — data-driven accuracy
  # ------------------------------------------------------------------
  @submeter
  Scenario Outline: Submeter charge is calculated accurately
    When I calculate a submeter charge from reading <prev> to <curr> at rate <rate> with multiplier <mult>
    Then the charge is <expected>

    Examples:
      | prev | curr | rate  | mult | expected | note                          |
      | 1000 | 1100 | 0.50  | 1    | 50.00    | 100 units * 0.50              |
      | 2000 | 2500 | 0.12  | 1    | 60.00    | 500 units * 0.12              |
      | 500  | 600  | 1.00  | 10   | 1000.00  | multiplier of 10 (CT meter)   |
      | 0    | 0    | 0.50  | 1    | 0.00     | no consumption -> zero charge |
      | 1000 | 1001 | 0.333 | 1    | 0.33     | rounding to cents             |

  @submeter @multiplier
  Scenario: The meter multiplier is applied to consumption and charge
    # The multiplier bug class: 100 units at rate 1.00 with x5 multiplier = 500, not 100
    When I calculate a submeter charge from reading 1000 to 1100 at rate 1.00 with multiplier 5
    Then the consumption is 500
    And the charge is 500.00

  @submeter @negative
  Scenario: A meter reading that went backwards is rejected
    When I try to calculate a submeter charge from reading 1100 to 1000 at rate 0.50 with multiplier 1
    Then the billing request is rejected as invalid

  @submeter @negative
  Scenario: A negative submeter rate is rejected
    When I try to calculate a submeter charge from reading 1000 to 1100 at rate -0.50 with multiplier 1
    Then the billing request is rejected as invalid

  @submeter @negative
  Scenario: A zero multiplier is rejected
    When I try to calculate a submeter charge from reading 1000 to 1100 at rate 0.50 with multiplier 0
    Then the billing request is rejected as invalid

  # ------------------------------------------------------------------
  # AFTER-HOURS HVAC BILLING — data-driven accuracy
  # ------------------------------------------------------------------
  @hvac
  Scenario Outline: After-hours HVAC charge is calculated accurately
    When I calculate an HVAC charge from "<start>" to "<end>" at hourly rate <rate> with a minimum of <min_hours> hours
    Then the charge is <expected>

    Examples:
      | start | end   | rate  | min_hours | expected | note                          |
      | 18:00 | 20:00 | 75.00 | 0         | 150.00   | 2 hours * 75                  |
      | 22:00 | 23:30 | 60.00 | 0         | 90.00    | 1.5 hours * 60                |
      | 18:00 | 18:30 | 80.00 | 1         | 80.00    | 0.5h but 1h minimum applies   |
      | 09:00 | 17:00 | 50.00 | 0         | 400.00   | full 8-hour window            |

  @hvac @minimum_hours
  Scenario: A short request bills the minimum hours
    # A 15-minute request with a 1-hour minimum should bill the full hour
    When I calculate an HVAC charge from "20:00" to "20:15" at hourly rate 100.00 with a minimum of 1 hours
    Then the applied hours are 1
    And the charge is 100.00

  @hvac @minimum_hours
  Scenario: A request above the minimum bills the actual duration
    # A 3-hour request with a 1-hour minimum bills the actual 3 hours
    When I calculate an HVAC charge from "18:00" to "21:00" at hourly rate 70.00 with a minimum of 1 hours
    Then the applied hours are 3
    And the charge is 210.00

  @hvac @negative
  Scenario: An HVAC window that ends before it starts is rejected
    When I try to calculate an HVAC charge from "20:00" to "18:00" at hourly rate 75.00 with a minimum of 0 hours
    Then the billing request is rejected as invalid

  @hvac @negative
  Scenario: A negative HVAC hourly rate is rejected
    When I try to calculate an HVAC charge from "18:00" to "20:00" at hourly rate -75.00 with a minimum of 0 hours
    Then the billing request is rejected as invalid

  # ------------------------------------------------------------------
  # CROSS-CUTTING — no silent money errors
  # ------------------------------------------------------------------
  @rounding
  Scenario: Every charge is rounded to the cent
    # Money must always be to the cent — never a long floating-point tail
    When I calculate a submeter charge from reading 1000 to 1003 at rate 0.333 with multiplier 1
    And I calculate an HVAC charge from "18:00" to "19:20" at hourly rate 45.00 with a minimum of 0 hours
    Then every calculated charge has at most two decimal places
