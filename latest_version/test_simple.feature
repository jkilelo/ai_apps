Feature: Supreme Website Navigation
  As a user
  I want to navigate the Supreme website
  So that I can browse products

  Scenario: Navigate to shop page
    Given I am on the Supreme homepage
    When I click on the "shop" link
    Then I should be on the shop page
    And I should see product listings

  Scenario: View spring/summer collection
    Given I am on the Supreme homepage
    When I click on "spring/summer 2025 preview"
    Then I should see the preview page
    And the page should display collection items