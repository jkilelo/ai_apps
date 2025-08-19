Feature: User Login and Navigation on Quotes to Scrape Login Page

  As a user,
  I want to be able to log in to the system with various credentials
  And navigate to different parts of the website from the login page
  So that I can access secure content and browse information.

  Background:
    Given I am on the "Quotes to Scrape" login page at "https://quotes.toscrape.com/login"
    And I see the "Login" form

  @smoke @critical @regression @happy-path
  Scenario: Successful user login with valid credentials
    When I enter "toscrape" into the "username" field with selector "#username"
    And I enter "password" into the "password" field with selector "input[name='password']"
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should be redirected to the "https://quotes.toscrape.com/" home page
    And I should see the "Logout" link
    And I should not see the "Login" link

  @negative @regression @login-form
  Scenario Outline: Failed user login with invalid or missing credentials
    When I enter "<username>" into the "username" field with selector "#username"
    And I enter "<password>" into the "password" field with selector "input[name='password']"
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should see the error message "Invalid username or password."
    And I should remain on the "https://quotes.toscrape.com/login" page
    And I should see the "Login" link

    Examples:
      | username      | password      |
      | wronguser     | wrongpass     |
      | toscrape      | wrongpass     |
      | wronguser     | password      |
      |               | password      |  # Missing username
      | toscrape      |               |  # Missing password
      |               |               |  # Both missing

  @smoke @regression @navigation
  Scenario: Navigate to Quotes Home Page from Login page
    When I click the "Quotes to Scrape" link with selector "a[href='https://quotes.toscrape.com/']"
    Then I should be redirected to the "https://quotes.toscrape.com/" home page
    And I should see the main header "Quotes to Scrape"

  @regression @navigation @external-link
  Scenario: Navigate to external GoodReads.com website
    When I click the "GoodReads.com" link with selector "a[href='https://www.goodreads.com/quotes']"
    Then a new tab should open with the URL "https://www.goodreads.com/quotes"
    And the current tab should remain on the "https://quotes.toscrape.com/login" page

  @regression @navigation @external-link
  Scenario: Navigate to external Zyte website
    When I click the "Zyte" link with selector "a.zyte"
    Then a new tab should open with the URL "https://www.zyte.com/"
    And the current tab should remain on the "https://quotes.toscrape.com/login" page

  @regression @page-elements @ui-validation
  Scenario: Verify presence and visibility of key elements on the login page
    Then I should see the "username" input field with selector "#username"
    And I should see the "password" input field with selector "input[name='password']"
    And I should see the "Login" button with selector "input.btn.btn-primary"
    And I should see the "Quotes to Scrape" link with selector "a[href='https://quotes.toscrape.com/']"
    And I should see the "GoodReads.com" link with selector "a[href='https://www.goodreads.com/quotes']"
    And I should see the "Zyte" link with selector "a.zyte"
    And the page title should be "Login"
    And the current URL should be "https://quotes.toscrape.com/login"
```