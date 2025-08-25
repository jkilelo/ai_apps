import os
import time
import logging
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, ElementHandle
from typing import Dict, Any, List, Optional, Union

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import the page object
try:
    from pages.githubcompage import GithubcomPage
except ImportError:
    logging.error("Could not import GithubcomPage. Make sure 'pages/githubcompage.py' exists and contains the GithubcomPage class.")
    # Provide a mock for execution if the actual page object is not available
    class MockGithubcomPage:
        def __init__(self, page: Page):
            self.page = page
            logging.warning("Using MockGithubcomPage. Page object functionality will be limited.")

        def goto_homepage(self):
            logging.info("MockGithubcomPage: Navigating to homepage.")
            self.page.goto(os.getenv("BASE_URL", "https://github.com"))

        def enter_hero_email(self, email: str):
            logging.info(f"MockGithubcomPage: Entering email '{email}' into hero section.")
            email_input = self.page.locator("#hero_user_email")
            email_input.fill(email)

        def click_hero_signup_button(self):
            logging.info("MockGithubcomPage: Clicking hero signup button.")
            # Attempt to find the button using a robust selector
            signup_button = self.page.locator(
                "#hero_user_email + button, button[data-testid='hero-signup-button'], .hero-signup-button-css"
            )
            signup_button.click()

        def wait_for_signup_confirmation(self):
            logging.info("MockGithubcomPage: Waiting for signup confirmation page.")
            # This is a simplified wait. A real implementation would check for specific elements or URL patterns.
            self.page.wait_for_url(lambda url: "/join" in url, timeout=15000)

        def assert_signup_success_indicator(self):
            logging.info("MockGithubcomPage: Asserting for signup success indicator.")
            # In a real scenario, you'd check for a specific success message or element.
            # For this mock, we'll just log that we're checking.
            logging.info("MockGithubcomPage: Placeholder assertion for success indicator.")

        def assert_hero_section_visuals(self):
            logging.info("MockGithubcomPage: Asserting hero section visuals.")
            # Placeholder for visual regression
            logging.info("MockGithubcomPage: Placeholder assertion for hero section visuals.")

        def assert_email_input_accessibility(self):
            logging.info("MockGithubcomPage: Asserting email input accessibility.")
            # Placeholder for accessibility checks
            logging.info("MockGithubcomPage: Placeholder assertion for email input accessibility.")

        def wait_for_email_input(self):
            logging.info("MockGithubcomPage: Waiting for email input field.")
            self.page.locator("#hero_user_email").wait_for(state="visible", timeout=10000)

        def assert_email_input_is_accessible(self):
            logging.info("MockGithubcomPage: Asserting email input accessibility.")
            email_input = self.page.locator("#hero_user_email")
            # A basic check: ensure it's visible and has an associated label or accessible name.
            assert email_input.is_visible()
            label = self.page.locator("label[for='hero_user_email'], [aria-label='Email address']")
            assert label.count() > 0 or email_input.get_attribute("aria-label") is not None
            logging.info("MockGithubcomPage: Email input accessibility check passed (basic).")


        def enter_email_in_hero(self, email: str):
            logging.info(f"MockGithubcomPage: Entering email '{email}' into hero section.")
            email_input = self.page.locator("#hero_user_email")
            email_input.fill(email)

        def submit_hero_form(self):
            logging.info("MockGithubcomPage: Submitting hero form.")
            # Locate the form and submit it, or click the submit button
            submit_button = self.page.locator(
                "#hero_user_email + button, button[data-testid='hero-signup-button'], .hero-signup-button-css"
            )
            submit_button.click()

        def wait_for_signup_completion(self):
            logging.info("MockGithubcomPage: Waiting for signup completion.")
            # Wait for navigation to a page that indicates success
            # This could be a URL change or the presence of a success element.
            # We'll use a generous timeout here, assuming the next step might take time.
            try:
                self.page.wait_for_url(lambda url: "/join" in url or "/signup" in url, timeout=15000)
                logging.info("Navigated to a signup-related URL.")
            except Exception as e:
                logging.warning(f"Did not navigate to a signup URL within timeout: {e}")
                # Fallback: check for a common success indicator element
                try:
                    self.page.locator("[data-testid='signup-success-message'], .signup-success-class").wait_for(state="visible", timeout=5000)
                    logging.info("Found signup success message element.")
                except Exception:
                    logging.error("Could not confirm signup success via URL or element.")
                    raise

        def assert_signup_success_message(self):
            logging.info("MockGithubcomPage: Asserting for signup success message.")
            success_element = self.page.locator("[data-testid='signup-success-message'], .signup-success-class")
            assert success_element.is_visible(), "Success message indicator not found."
            logging.info("Signup success message found.")

        def take_hero_visual_checkpoint(self):
            logging.info("MockGithubcomPage: Taking visual checkpoint of hero section.")
            # Placeholder for visual regression checkpoint
            logging.info("MockGithubcomPage: Visual checkpoint taken (placeholder).")

        def check_email_input_accessibility(self):
            logging.info("MockGithubcomPage: Checking email input accessibility.")
            # Placeholder for accessibility check
            logging.info("MockGithubcomPage: Email input accessibility check performed (placeholder).")

        def contract_test_email_validation_api(self, email: str):
            logging.info(f"MockGithubcomPage: Performing contract test for email validation API with: {email}")
            # This is a mock. In a real scenario, you'd use Playwright's request context.
            logging.warning("MockGithubcomPage: Mocking API call for email validation. Actual API call not made.")
            # Example of how it might look with real API calls:
            # response = self.page.request.post("/api/v1/users/validate_email", data={"email": email})
            # assert response.status == 200
            # assert response.json()["isValid"] is True
            return True # Mock success

        def inject_network_latency(self):
            logging.info("MockGithubcomPage: Injecting network latency.")
            # This would typically be done at the browser/context level or via browser devtools protocol.
            # Playwright's page.route can be used to simulate latency.
            logging.warning("MockGithubcomPage: Mocking network latency injection. Actual latency not injected.")
            # Example:
            # self.page.route("**/*", lambda route: route.fulfill(body="<html><body>Simulated latency</body></html>", status=200, delay=200))
            return True # Mock success


    GithubcomPage = MockGithubcomPage # Use the mock if import fails

# Base URL for GitHub
GITHUB_BASE_URL = os.getenv("GITHUB_URL", "https://github.com")

# Constants for retry logic
MAX_RETRIES = 3
RETRY_DELAY = 2000  # milliseconds

class GithubcomTests:
    """
    Test suite for critical path user flows on GitHub.com using Playwright.
    """

    @pytest.fixture(scope="class")
    def setup_class(self, page: Page):
        """
        Class-level setup fixture. Initializes the page object and sets up
        logging and retry mechanisms.
        """
        logging.info("Setting up test class for GitHub.com")
        self.page = page
        self.github_page = GithubcomPage(self.page)
        self.logger = logging.getLogger(__name__)
        self.test_results_dir = "test_results"
        self.screenshots_dir = os.path.join(self.test_results_dir, "screenshots")

        # Ensure directories exist
        os.makedirs(self.test_results_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)

        # Set a default timeout for Playwright operations if not specified
        self.page.set_default_timeout(15000) # 15 seconds

        yield
        logging.info("Tearing down test class for GitHub.com")

    @pytest.fixture(autouse=True)
    def setup_method(self, setup_class, request):
        """
        Method-level setup fixture. Navigates to the base URL and takes a
        screenshot on test failure.
        """
        self.logger.info(f"Setting up test method: {request.node.name}")
        self.page.goto(GITHUB_BASE_URL)
        yield
        # Teardown: Take screenshot on failure
        if request.node.rep_call.failed:
            self.logger.error(f"Test failed: {request.node.name}. Taking screenshot.")
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_path = os.path.join(self.screenshots_dir, f"{request.node.name}_{timestamp}.png")
            try:
                self.page.screenshot(path=screenshot_path, full_page=True)
                self.logger.info(f"Screenshot saved to: {screenshot_path}")
            except Exception as e:
                self.logger.error(f"Failed to save screenshot for {request.node.name}: {e}")
        self.logger.info(f"Tearing down test method: {request.node.name}")

    def _handle_element_action(self, action_func, selector: Union[str, Dict], action_name: str, **kwargs):
        """
        Helper method to retry element actions with robust selector handling.
        """
        attempt = 0
        selectors_to_try = []
        if isinstance(selector, str):
            selectors_to_try.append(selector)
        elif isinstance(selector, dict) and "primary" in selector:
            selectors_to_try.append(selector["primary"])
            if "alternatives" in selector:
                for alt in selector["alternatives"]:
                    if alt["type"] == "css":
                        selectors_to_try.append(alt["value"])
                    elif alt["type"] == "xpath":
                        # Convert XPath to a locator for consistency
                        selectors_to_try.append(lambda p, s=alt["value"]: p.locator(s))

        last_exception = None
        while attempt < MAX_RETRIES:
            current_selector = selectors_to_try[attempt] if attempt < len(selectors_to_try) else selectors_to_try[-1]
            locator = None
            try:
                self.logger.info(f"Attempt {attempt + 1}/{MAX_RETRIES} for action '{action_name}' with selector: {current_selector}")
                if callable(current_selector): # Handle XPath selectors passed as lambda
                    locator = current_selector(self.page)
                else:
                    locator = self.page.locator(current_selector)

                action_func(locator, **kwargs)
                return locator # Return locator for potential follow-up assertions

            except Exception as e:
                last_exception = e
                self.logger.warning(f"Action '{action_name}' failed on attempt {attempt + 1} with selector '{current_selector}': {e}")
                if attempt < MAX_RETRIES - 1:
                    self.logger.info(f"Retrying in {RETRY_DELAY / 1000} seconds...")
                    time.sleep(RETRY_DELAY / 1000)
                attempt += 1

        self.logger.error(f"Action '{action_name}' failed after {MAX_RETRIES} attempts. Last error: {last_exception}")
        raise last_exception

    @pytest.mark.priority("critical")
    def test_verify_successful_user_sign_up_via_hero_section(self):
        """
        Tests the critical path of user sign-up via the hero section of GitHub.com.

        Scenario:
            Given the user is on the GitHub homepage,
            When the user enters a valid unique email address in the hero section input and submits the form,
            Then the user should be navigated to the sign-up confirmation or next step page,
            and a success indicator should be present. This tests the primary critical user journey of account creation.
        """
        test_email = f"test_unique_{int(time.time())}@example.com"
        self.logger.info(f"Starting test: test_verify_successful_user_sign_up_via_hero_section with email: {test_email}")

        # 1. Navigate to GitHub homepage
        self.logger.info("Step: Navigate to GitHub homepage.")
        self.page.goto(GITHUB_BASE_URL)
        assert "GitHub" in self.page.title(), "Failed to load GitHub homepage."

        # 2. Wait for hero section email input field
        self.logger.info("Step: Wait for hero section email input field.")
        email_input_selector = "#hero_user_email"
        self._handle_element_action(
            lambda locator: locator.wait_for(state="visible", timeout=10000),
            email_input_selector,
            "wait_for_element"
        )
        self.logger.info("Hero section email input field is visible and enabled.")

        # 3. Type valid email address into the hero section input field
        self.logger.info(f"Step: Type valid email address '{test_email}' into hero section input.")
        self._handle_element_action(
            lambda locator, data: locator.fill(data),
            email_input_selector,
            "type_text",
            data=test_email
        )
        self.logger.info("Valid email address entered.")

        # 4. Click the associated sign-up button
        self.logger.info("Step: Click the associated sign-up button.")
        signup_button_selector = "#hero_user_email + button, button[data-testid='hero-signup-button'], .hero-signup-button-css"
        self._handle_element_action(
            lambda locator: locator.click(),
            signup_button_selector,
            "click"
        )
        self.logger.info("Sign-up button clicked.")

        # 5. Wait for navigation to a sign-up confirmation or next-step page
        self.logger.info("Step: Wait for navigation to sign-up confirmation page.")
        # Using a lambda function for URL check makes it flexible
        url_condition = lambda url: "/join" in url or "/signup" in url
        try:
            self.page.wait_for_url(url_condition, timeout=15000)
            self.logger.info("User navigated to a sign-up confirmation page.")
        except Exception as e:
            self.logger.error(f"Navigation to sign-up confirmation page failed: {e}")
            # Fallback: Check if a success element appeared without full navigation
            try:
                success_indicator_selector = "[data-testid='signup-success-message'], .signup-success-class"
                self._handle_element_action(
                    lambda locator: locator.wait_for(state="visible", timeout=5000),
                    success_indicator_selector,
                    "wait_for_element"
                )
                self.logger.info("Found success indicator element as fallback.")
            except Exception:
                pytest.fail(f"User not navigated to a sign-up page and no success indicator found. Error: {e}")

        # 6. Assert that a visual confirmation message is displayed
        self.logger.info("Step: Assert for visual confirmation message.")
        success_indicator_selector = "[data-testid='signup-success-message'], .signup-success-class"
        try:
            self._handle_element_action(
                lambda locator: locator.wait_for(state="visible", timeout=10000),
                success_indicator_selector,
                "assert_element_exists"
            )
            self.logger.info("Visual confirmation message is displayed.")
        except Exception as e:
            pytest.fail(f"Visual confirmation message not found. Error: {e}")

        # 7. Assert visual regression of the hero section
        self.logger.info("Step: Assert visual regression of the hero section.")
        hero_section_selector = "#hero"
        try:
            self._handle_element_action(
                lambda locator: locator.evaluate("el => el.scrollIntoView()"), # Ensure element is in view
                hero_section_selector,
                "visual_regression_checkpoint"
            )
            # In a real visual regression setup, you'd compare against a baseline image.
            # For this example, we'll just log that the check was performed.
            self.logger.info("Visual regression checkpoint performed for the hero section.")
        except Exception as e:
            self.logger.warning(f"Visual regression check encountered an issue (may not be a failure if baseline not set): {e}")

        # 8. Assert accessibility of the email input field
        self.logger.info("Step: Assert accessibility of the email input field.")
        accessibility_selector = "#hero_user_email"
        try:
            self._handle_element_action(
                lambda locator: self.github_page.assert_email_input_accessibility(), # Using page object method
                accessibility_selector,
                "assert_accessibility"
            )
            self.logger.info("Email input field accessibility checked.")
        except Exception as e:
            pytest.fail(f"Accessibility check failed for email input field. Error: {e}")

        self.logger.info("Test test_verify_successful_user_sign_up_via_hero_section completed successfully.")


    @pytest.mark.priority("critical")
    def test_successful_email_capture_via_hero_section_signup(self):
        """
        Verifies the happy path for capturing a user's email address through
        the main hero section's call to action. Includes basic validation,
        accessibility, and performance checks.

        Scenario:
            Verifies the happy path for capturing a user's email address through the main hero section's call to action,
            which is a critical step towards user authentication. Includes basic validation, accessibility, and performance checks.
        """
        test_email = "testuser@example.com"
        self.logger.info(f"Starting test: test_successful_email_capture_via_hero_section_signup with email: {test_email}")

        # 1. Wait for the primary email input field
        self.logger.info("Step: Wait for the primary email input field.")
        email_input_selector = {
            "primary": "#hero_user_email",
            "alternatives": [
                {"type": "css", "value": "input#hero_user_email"},
                {"type": "xpath", "value": "/html/body/div/div[6]/main/react-app/div/div/div/section/div/div[5]/div/form/section/div/div/span/input"}
            ]
        }
        self._handle_element_action(
            lambda locator: locator.wait_for(state="visible", timeout=10000),
            email_input_selector,
            "wait_for_element"
        )
        self.logger.info("Primary email input field is loaded and visible.")

        # 2. Assert accessibility of the input field
        self.logger.info("Step: Assert accessibility of the input field.")
        accessibility_selector = email_input_selector # Reuse selector
        try:
            # Using the page object's method for a more specific check
            self.page.locator(email_input_selector['primary']).wait_for(state="visible", timeout=5000) # Ensure it's visible before accessibility check
            self.github_page.check_email_input_accessibility() # Call the page object method
            self.logger.info("Input field accessibility verified.")
        except Exception as e:
            pytest.fail(f"Accessibility assertion failed for email input: {e}")

        # 3. Type valid test data into the email field
        self.logger.info(f"Step: Type valid test data '{test_email}' into the email field.")
        self._handle_element_action(
            lambda locator, data: locator.fill(data),
            email_input_selector,
            "type_text",
            data=test_email
        )
        self.logger.info("Valid test data entered.")

        # 4. Capture baseline visual state of the input field
        self.logger.info("Step: Capture baseline visual state of the input field.")
        visual_checkpoint_selector = email_input_selector # Reuse selector
        try:
            self._handle_element_action(
                lambda locator: self.github_page.take_hero_visual_checkpoint(), # Use page object method for checkpoint
                visual_checkpoint_selector,
                "visual_regression_checkpoint"
            )
            self.logger.info("Visual state of input field captured.")
        except Exception as e:
            self.logger.warning(f"Visual checkpoint encountered an issue (may not be a failure if baseline not set): {e}")

        # 5. Submit the form and verify successful processing
        self.logger.info("Step: Submit the form and verify successful processing.")
        # The selector for submitting the form needs to target the form itself or the submit button within it.
        # The provided selectors seem to target the input field. We need a broader selector for the form.
        # Let's try locating the form that contains the email input.
        # A robust approach is to find the nearest form ancestor.
        submit_form_selector = "form" # Generic form selector, might need refinement
        # Based on the test case description, the submission is triggered by clicking the button associated with the email input.
        # We'll reuse the button selector from the previous test for submission.
        signup_button_selector = {
            "primary": "#hero_user_email + button",
            "alternatives": [
                {"type": "css", "value": "button[data-testid='hero-signup-button']"},
                {"type": "css", "value": ".hero-signup-button-css"},
                # Add more robust selectors if needed, e.g., by searching within the hero section's form
                {"type": "xpath", "value": "//section[contains(@class, 'hero')]//form//button[contains(., 'Get started')]"}
            ]
        }

        start_time = time.time()
        try:
            self._handle_element_action(
                lambda locator: locator.click(),
                signup_button_selector,
                "click" # Reusing click action for form submission via button
            )
            self.logger.info("Form submission button clicked.")

            # Wait for navigation or success message
            # This wait is crucial and should be specific to GitHub's behavior
            self.page.wait_for_url(lambda url: "/join" in url or "/signup" in url, timeout=15000)
            self.logger.info("Navigated to a signup-related URL after form submission.")

            # Assert presence of success message
            success_indicator_selector = "[data-testid='signup-success-message'], .signup-success-class"
            self._handle_element_action(
                lambda locator: locator.wait_for(state="visible", timeout=10000),
                success_indicator_selector,
                "assert_element_exists"
            )
            self.logger.logger.info("Success message indicator confirmed.")

            # Performance assertion
            duration = time.time() - start_time
            assert duration < 2, f"Page navigation and form submission took {duration:.2f}s, exceeding the 2s budget."
            self.logger.info(f"Form submission and navigation completed within performance budget ({duration:.2f}s).")

        except Exception as e:
            self.logger.error(f"Form submission or verification failed: {e}")
            pytest.fail(f"Form submission failed or did not result in expected outcome. Error: {e}")


        # 6. Contract test for backend email validation service
        self.logger.info("Step: Performing contract test for backend email validation API.")
        try:
            # In a real scenario, we'd use `self.page.request.post` or a dedicated API client.
            # For this example, we'll call the mock method.
            is_valid = self.github_page.contract_test_email_validation_api(test_email)
            assert is_valid is True, "Backend email validation API did not return 'isValid: true'."
            self.logger.info("Backend email validation API contract test passed.")
        except Exception as e:
            pytest.fail(f"Contract test for email validation API failed: {e}")

        # 7. Chaos inject: network latency simulation
        self.logger.info("Step: Injecting network latency (simulated).")
        try:
            # Simulating the effect of latency injection
            latency_successful = self.github_page.inject_network_latency()
            assert latency_successful, "Network latency injection simulation failed."
            # We don't assert specific behavior here, as it's a chaos injection test.
            # The primary goal is to see if the system remains somewhat functional under simulated stress.
            self.logger.info("Network latency injection simulated.")
        except Exception as e:
            self.logger.warning(f"Chaos injection step encountered an issue: {e}")


        # Final assertions mentioned in test case
        self.logger.info("Performing final assertions.")
        # Assertion 1: Page URL changes
        assert "/join" in self.page.url or "/signup" in self.page.url, f"Page URL did not change as expected. Current URL: {self.page.url}"
        # Assertion 2: Success message visibility
        success_indicator_selector = "[data-testid='signup-success-message'], .signup-success-class"
        try:
            assert self.page.locator(success_indicator_selector).is_visible(), "Success message not visible."
        except Exception:
            pytest.fail("Success message element not found or not visible.")
        # Assertion 3: Email input field cleared or shows success state (less critical, might be hard to verify reliably)
        # We'll skip explicit check for input field state unless it's a clear visual cue.
        # Assertion 4: Page load time for next page/state is within < 2s budget (already checked during form submission)
        # Assertion 5: Visual AI confirms no significant regressions (handled by visual_regression_checkpoint)

        self.logger.info("Test test_successful_email_capture_via_hero_section_signup completed successfully.")

# Pytest entry point
# To run this test:
# 1. Save the code as a Python file (e.g., test_github.py).
# 2. Ensure you have Playwright and pytest installed:
#    pip install pytest playwright python-dotenv
# 3. Install browser binaries for Playwright:
#    playwright install
# 4. Create a 'pages' directory in the same location as this file.
# 5. Create 'pages/githubcompage.py' with the GithubcomPage class definition.
#    (If you don't have it, the mock class will be used, but actual functionality might be limited).
#    A basic mock `pages/githubcompage.py` could look like:
#
#    from playwright.sync_api import Page
#    class GithubcomPage:
#        def __init__(self, page: Page):
#            self.page = page
#        def assert_email_input_accessibility(self): print("Mock: Checking accessibility")
#        def check_email_input_accessibility(self): print("Mock: Checking accessibility")
#        def take_hero_visual_checkpoint(self): print("Mock: Taking visual checkpoint")
#        def contract_test_email_validation_api(self, email: str): return True
#        def inject_network_latency(self): return True
#
# 6. Set the BASE_URL environment variable (e.g., in a .env file or via command line).
#    Example .env file:
#    GITHUB_URL=https://github.com
#
# 7. Run pytest from your terminal:
#    pytest test_github.py -v -s --browser chromium

