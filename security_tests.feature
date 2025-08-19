Feature: Login Page Security Vulnerability Testing
  As a security tester
  I want to verify the robustness of the login functionality
  To ensure protection against common web vulnerabilities like injection and bypass attempts.

  Background:
    Given I am on the "Login" page (https://quotes.toscrape.com/login)
    And I observe the initial session ID

  @sqli @vulnerability @negative
  Scenario Outline: Prevent SQL Injection via Username Field
    When I enter "<username_payload>" into the "Username" field (input#username)
    And I enter "securePass123" into the "Password" field (input[type='password'])
    And I click the "Login" button (input.btn.btn-primary)
    Then I should see an error message indicating "Invalid credentials" or "Login failed"
    And the page content should not show any database errors
    And I should not be logged in

    Examples:
      | username_payload           |
      | ' OR '1'='1                |
      | " OR "1"="1                |
      | ' OR 1=1 --                |
      | " OR 1=1 --                |
      | admin' --                  |
      | admin' #                   |
      | admin' OR 'a'='a          |
      | admin' AND '1'='1 --      |

  @sqli @vulnerability @negative
  Scenario Outline: Prevent SQL Injection via Password Field
    When I enter "testuser" into the "Username" field (input#username)
    And I enter "<password_payload>" into the "Password" field (input[type='password'])
    And I click the "Login" button (input.btn.btn-primary)
    Then I should see an error message indicating "Invalid credentials" or "Login failed"
    And the page content should not show any database errors
    And I should not be logged in

    Examples:
      | password_payload           |
      | ' OR '1'='1                |
      | " OR "1"="1                |
      | ' OR 1=1 --                |
      | " OR 1=1 --                |
      | password' OR '1'='1       |
      | password' #               |
      | password' AND '1'='1 --   |

  @xss @vulnerability @negative
  Scenario Outline: Prevent Cross-Site Scripting (XSS) via Username Field
    When I enter "<username_payload>" into the "Username" field (input#username)
    And I enter "securePass123" into the "Password" field (input[type='password'])
    And I click the "Login" button (input.btn.btn-primary)
    Then I should not see any script execution or pop-ups
    And the page content should be free of injected HTML or JavaScript elements
    And I should see an error message indicating "Invalid credentials" or "Login failed"
    And I should not be logged in

    Examples:
      | username_payload                                   |
      | <script>alert('XSS')</script>                      |
      | "><script>alert('XSS')</script>                   |
      | <img src=x onerror=alert('XSS')>                   |
      | '"; --><script>alert(document.domain)</script>    |
      | %3Cscript%3Ealert(%27XSS%27)%3C%2Fscript%3E        |
      | <body onload=alert('XSS')>                         |

  @xss @vulnerability @negative
  Scenario Outline: Prevent Cross-Site Scripting (XSS) via Password Field
    When I enter "testuser" into the "Username" field (input#username)
    And I enter "<password_payload>" into the "Password" field (input[type='password'])
    And I click the "Login" button (input.btn.btn-primary)
    Then I should not see any script execution or pop-ups
    And the page content should be free of injected HTML or JavaScript elements
    And I should see an error message indicating "Invalid credentials" or "Login failed"
    And I should not be logged in

    Examples:
      | password_payload                                   |
      | <script>alert('XSS')</script>                      |
      | "><script>alert('XSS')</script>                   |
      | <img src=x onerror=alert('XSS')>                   |
      | '"; --><script>alert(document.domain)</script>    |

  @bruteforce @penetration @negative
  Scenario: Verify Brute-Force Protection via Multiple Failed Attempts
    Given I have a known valid username "gooduser" (assuming this exists for testing lockout)
    When I attempt to log in with "gooduser" and invalid password "wrongpass1" for 5 times
    And I attempt to log in with "gooduser" and invalid password "wrongpass2" for another 5 times
    Then I should eventually see a "Too many failed login attempts" message or similar rate-limiting indication
    And I should not be able to log in with valid credentials immediately afterwards for a specified period

  @session @positive
  Scenario: Verify Session ID Changes After Successful Login
    Given I have valid credentials "test:test" (assuming these are default/valid credentials for quotes.toscrape.com)
    When I log in with "test" into the "Username" field (input#username) and "test" into the "Password" field (input[type='password'])
    And I click the "Login" button (input.btn.btn-primary)
    Then I should be redirected to the "Quotes" page
    And the current session ID should be different from the initial session ID

  @session @vulnerability @negative
  Scenario: Verify Session ID Is Securely Generated Before Login
    Then the initial session ID should be non-guessable and complex (e.g., sufficient length, alphanumeric)
    And the session ID should not contain any predictable patterns or sensitive information

  @input-validation @negative
  Scenario Outline: Handle Invalid Characters in Username
    When I enter "<username_input>" into the "Username" field (input#username)
    And I enter "securePass123" into the "Password" field (input[type='password'])
    And I click the "Login" button (input.btn.btn-primary)
    Then I should see an error message indicating "Invalid username format" or "Login failed"
    And I should not be logged in

    Examples:
      | username_input  |
      | user@domain.com |
      | user/name       |
      | !@#$%^&*()      |
      | `~[]{}|\        |
      | <script>        |

  @bypass @penetration @negative
  Scenario: Prevent Login with Common Default Credentials
    When I attempt to log in with common default credentials
      | username | password |
      | admin    | admin    |
      | root     | root     |
      | test     | test     |
      | user     | user     |
    Then I should see an error message indicating "Invalid credentials" or "Login failed"
    And I should not be logged in

  @mitm @encryption @positive
  Scenario: Verify HTTPS Protocol for Login Page
    Then the current URL should start with "https://"
    And the browser should indicate a secure connection (e.g., padlock icon)
    And no mixed content warnings should be displayed
```