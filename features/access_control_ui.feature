@ui @access_control
Feature: Access Control — admin console (UI layer)
  Drives the same provision / revoke journeys a property administrator performs
  in the admin console, through a real browser (Playwright).

  As a property administrator
  I want to grant and revoke access from the admin console
  So that I can manage who can enter the building without touching the API

  Background:
    Given the admin console is open

  # ------------------------------------------------------------------
  # PROVISIONING (UI)
  # ------------------------------------------------------------------
  @provisioning
  Scenario: Granting access shows an active credential in the table
    When I grant "Card" access to "alice@corp.com" for door group "Floor-3"
    Then the credential row for "alice@corp.com" shows status "active"

  @provisioning
  Scenario: Granting access shows a success toast
    When I grant "Card" access to "bob@corp.com" for door group "Lobby"
    Then a toast containing "Access granted" is shown

  @provisioning @negative
  Scenario: Granting access with a missing door group shows an error and adds no row
    When I enter the user "eve@corp.com" and click Grant Access without a door group
    Then a toast containing "Error" is shown
    And there is no credential row for "eve@corp.com"

  @provisioning
  Scenario: Granting mobile access shows the type and door group in the row
    When I grant "Mobile" access to "carol@corp.com" for door group "Garage"
    Then the credential row for "carol@corp.com" contains "mobile"
    And the credential row for "carol@corp.com" contains "Garage"

  # ------------------------------------------------------------------
  # REVOKING (UI)
  # ------------------------------------------------------------------
  @revoking
  Scenario: Revoking changes the status to revoked
    Given "Card" access has been granted to "grace@corp.com" for door group "Floor-2"
    And the credential row for "grace@corp.com" shows status "active"
    When I revoke access for "grace@corp.com"
    Then the credential row for "grace@corp.com" shows status "revoked"

  @revoking
  Scenario: Revoking removes the Revoke button
    Given "Card" access has been granted to "heidi@corp.com" for door group "Lobby"
    When I revoke access for "heidi@corp.com"
    Then there is no Revoke button for "heidi@corp.com"

  @revoking
  Scenario: Revoking shows a success toast
    Given "Card" access has been granted to "ivan@corp.com" for door group "Floor-5"
    When I revoke access for "ivan@corp.com"
    Then a toast containing "revoked" is shown

  # ------------------------------------------------------------------
  # FULL LIFECYCLE (UI end-to-end)
  # ------------------------------------------------------------------
  @lifecycle @isolation
  Scenario: Revoking one user leaves another user's access untouched
    Given "Card" access has been granted to "alice@corp.com" for door group "Floor-3"
    And "Card" access has been granted to "bob@corp.com" for door group "Floor-3"
    And the credential row for "alice@corp.com" shows status "active"
    And the credential row for "bob@corp.com" shows status "active"
    When I revoke access for "alice@corp.com"
    Then the credential row for "alice@corp.com" shows status "revoked"
    And the credential row for "bob@corp.com" shows status "active"
