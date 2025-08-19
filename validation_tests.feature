Feature: User Login Form Validation

  As a user,
  I want to interact with the login form,
  So that I can log in securely and receive appropriate feedback for invalid inputs.

  @login @ui
  Background:
    Given I am on the "https://quotes.toscrape.com/login" page

  @validation @negative @required
  Scenario: Attempt login with an empty username
    When I leave the username field empty
    And I enter "password123" into the "password" field
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should see an error message indicating "No active account found with the given credentials." or similar
    And I should remain on the "https://quotes.toscrape.com/login" page

  @validation @negative @required
  Scenario: Attempt login with an empty password
    When I enter "testuser" into the "username" field with selector "#username"
    And I leave the password field empty
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should see an error message indicating "No active account found with the given credentials." or similar
    And I should remain on the "https://quotes.toscrape.com/login" page

  @validation @negative @required
  Scenario: Attempt login with both username and password fields empty
    When I leave the username field empty
    And I leave the password field empty
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should see an error message indicating "No active account found with the given credentials." or similar
    And I should remain on the "https://quotes.toscrape.com/login" page

  @validation @negative @error_message
  Scenario Outline: Verify error message for invalid credentials
    When I enter "<username>" into the "username" field with selector "#username"
    And I enter "<password>" into the "password" field
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should see an error message with text "<expected_error_message>"

    Examples:
      | username       | password      | expected_error_message                        |
      | non_existent   | some_password | No active account found with the given credentials. |
      | testuser       | wrong_password | No active account found with the given credentials. |
      | another_user   | invalid_pass  | No active account found with the given credentials. |

  @validation @positive @successful_login
  Scenario: Successful login with valid credentials
    Given I have a valid username "test" and password "test"
    When I enter "test" into the "username" field with selector "#username"
    And I enter "test" into the "password" field
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should be redirected to the "https://quotes.toscrape.com/" page
    And I should see a success message indicating "You are now logged in." or similar
    And I should see a "Logout" link

  # Note: The provided analysis mentions "Password Complexity (length, special characters, etc.)"
  # This implies the system might have specific password rules.
  # Based on the observed behavior of quotes.toscrape.com, it uses a simple "test/test" credential.
  # If it had actual complexity, these scenarios would be relevant.
  # For the purpose of demonstration, I'll include hypothetical complexity scenarios.

  @validation @negative @password_complexity @boundary
  Scenario Outline: Verify password length constraints (hypothetical)
    When I enter "testuser" into the "username" field with selector "#username"
    And I enter "<password>" into the "password" field
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should see an error message indicating "<expected_error_message>"

    Examples:
      | password | expected_error_message                        |
      | short    | Please enter a password between 6 and 20 characters. |
      | toolongpasswordforthisfieldtestinginvalidatingtheentry  | Please enter a password between 6 and 20 characters. |

  @validation @negative @password_complexity @pattern
  Scenario Outline: Verify password format constraints (hypothetical)
    When I enter "testuser" into the "username" field with selector "#username"
    And I enter "<password>" into the "password" field
    And I click the "Login" button with selector "input.btn.btn-primary"
    Then I should see an error message indicating "<expected_error_message>"

    Examples:
      | password   | expected_error_message                                   |
      | nopassword | Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character. |
      | 12345abc   | Password must contain at least one uppercase letter and one special character. |
      | Abcde!23   | No active account found with the given credentials. (This would be if it passes format but is still invalid) |

  @validation @navigation @external_link
  Scenario: Verify GoodReads.com link opens in a new tab
    When I click the "GoodReads.com" link with selector "a[href='https://www.goodreads.com/quotes']"
    Then the "https://www.goodreads.com/quotes" URL should open in a new tab or window
    And I should remain on the "https://quotes.toscrape.com/login" page in the original tab