@api @access_control
Feature: Access Control — credential lifecycle (API layer)
  Security = trust. A credential that still works after it has been revoked
  is a security breach, so these scenarios prioritise authorization and
  revoked-access-stops-working assertions.

  As a property administrator
  I want to provision and revoke access credentials through Genea's API
  So that only the right people can open the right doors, and only while authorised

  Background:
    Given a fresh Genea access control system

  # ------------------------------------------------------------------
  # PROVISIONING
  # ------------------------------------------------------------------
  @provisioning
  Scenario: Provisioning creates an active credential
    When I provision a "card" credential for "alice@corp.com" at door group "Floor-3"
    Then the credential status is "active"
    And the credential belongs to "alice@corp.com" at door group "Floor-3"
    And the credential id starts with "CRED-"

  @provisioning
  Scenario: A provisioned credential can unlock its assigned door
    When I provision a "card" credential for "bob@corp.com" at door group "Lobby"
    Then presenting the credential at "Lobby" is granted

  @provisioning
  Scenario: Provisioning a mobile credential
    When I provision a "mobile" credential for "carol@corp.com" at door group "Garage"
    Then the credential type is "mobile"
    And the credential status is "active"

  @provisioning @security
  Scenario: A credential cannot unlock a door group it was not granted
    When I provision a "card" credential for "dave@corp.com" at door group "Floor-3"
    Then presenting the credential at "Server-Room" is denied

  @provisioning @negative
  Scenario Outline: Provisioning with missing required fields is rejected
    When I try to provision a credential for "<user>" at door group "<door>"
    Then provisioning is rejected with a validation error

    Examples:
      | user         | door    | reason             |
      |              | Floor-3 | missing user       |
      | eve@corp.com |         | missing door group |

  @provisioning @negative
  Scenario: Provisioning with an unknown credential type is rejected
    When I try to provision a "retina" credential for "frank@corp.com" at door group "Floor-3"
    Then provisioning is rejected with a validation error

  # ------------------------------------------------------------------
  # REVOKING
  # ------------------------------------------------------------------
  @revoking
  Scenario: Revoking marks the credential as revoked
    Given a "card" credential has been provisioned for "grace@corp.com" at door group "Floor-2"
    When I revoke the credential
    Then the credential status is "revoked"
    And the credential records a revocation timestamp

  @revoking @security
  Scenario: A revoked credential can no longer unlock its door
    Given a "card" credential has been provisioned for "heidi@corp.com" at door group "Lobby"
    And presenting the credential at "Lobby" is granted
    When I revoke the credential
    Then presenting the credential at "Lobby" is denied

  @revoking @negative
  Scenario: Revoking an unknown credential fails
    When I try to revoke credential "CRED-DOESNOTEXIST"
    Then revocation fails because the credential was not found

  @revoking @isolation
  Scenario: Revoking one credential does not affect another
    Given a "card" credential has been provisioned for "alice@corp.com" at door group "Floor-3"
    And a "card" credential has been provisioned for "bob@corp.com" at door group "Floor-3"
    When I revoke the credential of "alice@corp.com"
    Then the credential of "alice@corp.com" has status "revoked"
    And the credential of "bob@corp.com" has status "active"
    And presenting the credential of "bob@corp.com" at "Floor-3" is granted

  # ------------------------------------------------------------------
  # FULL LIFECYCLE
  # ------------------------------------------------------------------
  @lifecycle @security
  Scenario: Full credential lifecycle — provision, use, revoke, denied, audited
    When I provision a "mobile" credential for "ivan@corp.com" at door group "Floor-5"
    Then the credential status is "active"
    And presenting the credential at "Floor-5" is granted
    When I revoke the credential
    Then the credential status is "revoked"
    And presenting the credential at "Floor-5" is denied
    And the audit trail contains the events:
      | event         |
      | provisioned   |
      | revoked       |
      | unlock_denied |
