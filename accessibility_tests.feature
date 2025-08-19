Feature: Accessibility of Login Page

  As a user with accessibility needs
  I want to interact with the login page
  So that I can log in successfully and comfortably

  Background:
    Given I am on the "Login" page at "https://quotes.toscrape.com/login"
    And I have refreshed the page

  @keyboard-navigation @tab-order @focus-management
  Scenario: Keyboard navigation follows a logical tab order and focus is visible
    When I press the "Tab" key
    Then the "Username" input field with selector "#username" should be focused
    And the focused element should have a visible outline
    When I press the "Tab" key
    Then the "Password" input field with selector "input[name='password']" should be focused
    And the focused element should have a visible outline
    When I press the "Tab" key
    Then the "Login" button with selector "input.btn.btn-primary" should be focused
    And the focused element should have a visible outline
    When I press the "Tab" key
    Then the "Quotes to Scrape" link with selector "a[href='https://quotes.toscrape.com/']" should be focused
    And the focused element should have a visible outline
    When I press the "Tab" key
    Then the "Login" link with selector "a[href='https://quotes.toscrape.com/login']" should be focused
    And the focused element should have a visible outline
    When I press the "Tab" key
    Then the "GoodReads.com" link with selector "a[href='https://www.goodreads.com/quotes']" should be focused
    And the focused element should have a visible outline
    When I press the "Tab" key
    Then the "Zyte" link with selector "a.zyte" should be focused
    And the focused element should have a visible outline

  @keyboard-navigation @tab-order @focus-management
  Scenario: Reverse keyboard navigation (Shift+Tab) follows a logical order
    Given I have navigated forward with Tab until the "Zyte" link with selector "a.zyte" is focused
    When I press the "Shift+Tab" key
    Then the "GoodReads.com" link with selector "a[href='https://www.goodreads.com/quotes']" should be focused
    When I press the "Shift+Tab" key
    Then the "Login" link with selector "a[href='https://quotes.toscrape.com/login']" should be focused
    When I press the "Shift+Tab" key
    Then the "Quotes to Scrape" link with selector "a[href='https://quotes.toscrape.com/']" should be focused
    When I press the "Shift+Tab" key
    Then the "Login" button with selector "input.btn.btn-primary" should be focused
    When I press the "Shift+Tab" key
    Then the "Password" input field with selector "input[name='password']" should be focused
    When I press the "Shift+Tab" key
    Then the "Username" input field with selector "#username" should be focused

  @form-labels @screen-reader @label-association
  Scenario: Username input field is correctly associated with its label
    Then the label for the "Username" input field with selector "#username" should be associated correctly
    And the label text should be "Username"

  @form-labels @screen-reader @label-association
  Scenario: Password input field is correctly associated with its label
    Then the label for the "Password" input field with selector "input[name='password']" should be associated correctly
    And the label text should be "Password"

  @error-handling @screen-reader @error-announcement
  Scenario: Invalid login attempt displays and announces a clear error message
    When I enter "invalid_user" into the "Username" field with selector "#username"
    And I enter "invalid_pass" into the "Password" field with selector "input[name='password']"
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should see an error message "Invalid username/password."
    And the error message should be perceivable by screen readers

  @error-handling @screen-reader @error-announcement
  Scenario: Attempting to login with an empty username field displays the general error message
    When I enter "" into the "Username" field with selector "#username"
    And I enter "password123" into the "Password" field with selector "input[name='password']"
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should see an error message "Invalid username/password."
    And the error message should be perceivable by screen readers

  @focus-management @initial-focus
  Scenario: Initial focus is on the username input field upon page load
    Then the "Username" input field with selector "#username" should be focused

  @color-contrast @text-readability
  Scenario: Page title has sufficient color contrast
    Then the element with text "Login" and selector "h2" should have a color contrast ratio of at least "4.5:1"

  @color-contrast @text-readability
  Scenario: Username label has sufficient color contrast
    Then the label for the "Username" input field with selector "#username" should have a color contrast ratio of at least "4.5:1"

  @color-contrast @text-readability
  Scenario: Password label has sufficient color contrast
    Then the label for the "Password" input field with selector "input[name='password']" should have a color contrast ratio of at least "4.5:1"

  @color-contrast @button-contrast
  Scenario: Login button text has sufficient color contrast
    Then the "Login" button with selector "input.btn.btn-primary" should have a color contrast ratio of at least "4.5:1"

  @aria-roles @form-structure @screen-reader
  Scenario: Login form is semantically structured and perceivable by assistive technologies
    Then the "Login" form with selector "form" should be a native HTML5 form element
    And the "Username" input field with selector "#username" should have an accessible name
    And the "Password" input field with selector "input[name='password']" should have an accessible name
    And the "Login" button with selector "input.btn.btn-primary" should have an accessible name
```