import pytest
import os
import logging
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright
from dotenv import load_dotenv
from typing import Dict, Any

# Assume GithubcomPage is available in pages.githubcompage module
# from pages.githubcompage import GithubcomPage

# Mocking the Page Object for demonstration if it's not provided
class MockLocator:
    def __init__(self, page: Page, selector: str):
        self._page = page
        self._selector = selector
        self._element = None

    def _get_element(self):
        if self._element is None:
            try:
                # Simulate finding an element. For real scenarios, use page.locator
                # This is a placeholder; actual Playwright methods will be used in the real test.
                pass
            except Exception as e:
                logging.error(f"Failed to locate element '{self._selector}': {e}")
                raise
        return self._element

    def fill(self, text: str):
        logging.info(f"Filling '{self._selector}' with '{text}'")
        # In a real scenario: self._page.locator(self._selector).fill(text)
        pass

    def click(self):
        logging.info(f"Clicking '{self._selector}'")
        # In a real scenario: self._page.locator(self._selector).click()
        pass

    def wait_for(self, state: str = "visible", timeout: int = 5000):
        logging.info(f"Waiting for '{self._selector}' to be in state '{state}'")
        # In a real scenario: self._page.locator(self._selector).wait_for(state=state, timeout=timeout)
        pass

    def inner_text(self) -> str:
        logging.info(f"Getting inner text of '{self._selector}'")
        # In a real scenario: return self._page.locator(self._selector).inner_text()
        return "mock_inner_text"

    def evaluate(self, expression: str) -> Any:
        logging.info(f"Evaluating expression on '{self._selector}': {expression}")
        # In a real scenario: return self._page.locator(self._selector).evaluate(expression)
        return True # Mock return value

    def blur(self):
        logging.info(f"Blurring '{self._selector}'")
        # In a real scenario: self._page.locator(self._selector).blur()
        pass

    def is_visible(self) -> bool:
        logging.info(f"Checking if '{self._selector}' is visible")
        # In a real scenario: return self._page.locator(self._selector).is_visible()
        return True # Mock return value

    def get_attribute(self, attribute: str) -> str | None:
        logging.info(f"Getting attribute '{attribute}' of '{self._selector}'")
        # In a real scenario: return self._page.locator(self._selector).get_attribute(attribute)
        if attribute == "value":
            return "mock_value"
        return None # Mock return value

class MockPage:
    def __init__(self, browser_context: BrowserContext):
        self._browser_context = browser_context
        self._url = ""
        self._logging_prefix = "MockPage: "

    def goto(self, url: str, wait_until: str = "load") -> None:
        self._url = url
        logging.info(f"{self._logging_prefix}Navigating to {url}")
        # In a real scenario: self._page.goto(url, wait_until=wait_until)
        pass

    def locator(self, selector: str) -> MockLocator:
        logging.info(f"{self._logging_prefix}Locating element with selector: {selector}")
        # In a real scenario: return self._page.locator(selector)
        return MockLocator(self, selector) # Return a mock locator

    def get_by_role(self, role: str, name: str) -> MockLocator:
        selector = f"role={role}, name={name}"
        logging.info(f"{self._logging_prefix}Getting element by role: {selector}")
        return MockLocator(self, selector)

    def close(self) -> None:
        logging.info(f"{self._logging_prefix}Closing page.")
        pass

class MockBrowserContext:
    def __init__(self, browser: Browser):
        self._browser = browser
        self._page = MockPage(self)
        self._logging_prefix = "MockBrowserContext: "

    def new_page(self) -> MockPage:
        logging.info(f"{self._logging_prefix}Creating new page.")
        return self._page

    def close(self) -> None:
        logging.info(f"{self._logging_prefix}Closing browser context.")
        pass

class MockBrowser:
    def __init__(self):
        self._logging_prefix = "MockBrowser: "

    def new_context(self, **kwargs) -> MockBrowserContext:
        logging.info(f"{self._logging_prefix}Creating new browser context.")
        return MockBrowserContext(self)

    def close(self) -> None:
        logging.info(f"{self._logging_prefix}Closing browser.")
        pass

# If the actual page object is not available, use this mock for basic structure testing.
# In a real execution, 'from pages.githubcompage import GithubcomPage' would be used.
try:
    from pages.githubcompage import GithubcomPage
except ImportError:
    logging.warning("Could not import GithubcomPage. Using a mock implementation.")
    GithubcomPage = MockPage # Fallback to mock if import fails


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL from environment or default
GITHUB_URL = os.getenv("GITHUB_URL", "https://github.com")

# Define selectors for the hero section email input
HERO_EMAIL_INPUT_SELECTOR = "css=#hero_user_email"
# Alternative selectors for robustness, as per test case comments
HERO_EMAIL_INPUT_ALT_SELECTOR_1 = "css=input[data-testid=hero_user_email]"
HERO_EMAIL_INPUT_ALT_SELECTOR_2 = "xpath=//input[@id='hero_user_email']"


class TestGithubHomepageSignup:
    """
    Test suite for validating the signup functionality on the GitHub homepage.
    Covers email input validation for both valid and invalid formats.
    """

    @pytest.fixture(scope="class")
    def browser_context(self) -> BrowserContext:
        """
        Pytest fixture to set up and tear down the Playwright browser context.
        Includes environment variable loading and browser launch.
        """
        logger.info("Setting up browser context...")
        # Load configuration from environment variables
        browser_type = os.getenv("BROWSER_TYPE", "chromium")
        headless = os.getenv("HEADLESS", "true").lower() == "true"
        slow_mo_ms = int(os.getenv("SLOW_MO_MS", "0"))

        try:
            playwright = sync_playwright().start()
            if browser_type == "chromium":
                browser = playwright.chromium
            elif browser_type == "firefox":
                browser = playwright.firefox
            elif browser_type == "webkit":
                browser = playwright.webkit
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")

            context = browser.new_context(
                headless=headless,
                slow_mo=slow_mo_ms,
                viewport={"width": 1280, "height": 720} # Set a default viewport
            )
            logger.info(f"Browser context created: {browser_type}, headless={headless}, slow_mo={slow_mo_ms}")
            yield context
        except Exception as e:
            logger.error(f"Failed to initialize Playwright or browser context: {e}")
            pytest.fail(f"Browser setup failed: {e}")
        finally:
            if 'context' in locals() and context:
                logger.info("Tearing down browser context...")
                try:
                    context.close()
                    logger.info("Browser context closed successfully.")
                except Exception as e:
                    logger.error(f"Error closing browser context: {e}")
            if 'playwright' in locals() and playwright:
                logger.info("Stopping Playwright...")
                try:
                    playwright.stop()
                    logger.info("Playwright stopped successfully.")
                except Exception as e:
                    logger.error(f"Error stopping Playwright: {e}")

    @pytest.fixture(autouse=True)
    def setup_test(self, browser_context: BrowserContext, request) -> None:
        """
        Fixture to set up a new page for each test and handle screenshots on failure.
        """
        self.page = browser_context.new_page()
        self.page_object = GithubcomPage(self.page) # Instantiate the Page Object
        logger.info(f"Starting test: {request.node.name}")

        # Take screenshot on test failure
        yield

        if request.node.rep_call.failed:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/{request.node.name}_{timestamp}.png"
            try:
                os.makedirs("screenshots", exist_ok=True)
                self.page.screenshot(path=screenshot_path, full_page=True)
                logger.error(f"Test failed. Screenshot saved to: {screenshot_path}")
            except Exception as e:
                logger.error(f"Failed to take screenshot on failure: {e}")

        logger.info(f"Finished test: {request.node.name}")
        self.page.close() # Close the page after each test

    @pytest.mark.critical
    @pytest.mark.general
    def test_tc001_validate_correct_email_format_input_in_hero_section_signup(self) -> None:
        """
        TC001: Validate Correct Email Format Input in Hero Section Signup.
        Verifies that the primary email input field in the hero section correctly
        accepts a standard, syntactically valid email address.
        """
        test_data: Dict[str, Any] = {
            "email_valid": "qa.architect+test1@example.com"
        }
        expected_input_value = test_data["email_valid"]

        try:
            # Step 1: Navigate to the GitHub homepage.
            logger.info(f"Navigating to {GITHUB_URL}")
            self.page.goto(GITHUB_URL)
            self.page.wait_for_load_state("domcontentloaded") # Wait for basic page load
            logger.info("GitHub homepage loaded successfully.")

            # Step 2: Type a valid, standard email address into the hero section email input.
            logger.info(f"Typing valid email: {expected_input_value} into {HERO_EMAIL_INPUT_SELECTOR}")
            email_input = self.page.locator(HERO_EMAIL_INPUT_SELECTOR)
            email_input.fill(expected_input_value)

            # Assertion for step 2: Verify the email address is accurately displayed.
            actual_input_value = email_input.get_attribute("value")
            assert actual_input_value == expected_input_value, \
                f"Expected email '{expected_input_value}' not found in input. Found: '{actual_input_value}'"
            logger.info(f"Email '{expected_input_value}' correctly displayed in input field.")

            # Step 3: Trigger field validation by blurring the input.
            logger.info(f"Blurring input field: {HERO_EMAIL_INPUT_SELECTOR}")
            email_input.blur()
            # Add a small wait for potential client-side validation to process
            self.page.wait_for_timeout(500) # Adjust timeout as needed

            # Step 4: Verify input field state after blur.
            logger.info(f"Verifying input field state after blur for {HERO_EMAIL_INPUT_SELECTOR}")
            # Assertion: No validation error message is displayed.
            # This assumes error messages are in specific elements. We'll check for absence.
            # A common pattern is an error message near the input.
            error_message_selector = "css=.error-message-selector" # Placeholder selector for error message
            assert not self.page.locator(error_message_selector).is_visible(), \
                "Unexpected error message found for valid email."

            # Assertion: The input field retains its default (valid) styling.
            # Check for absence of common error classes.
            assert not email_input.evaluate("el => el.classList.contains('is-invalid') or el.classList.contains('has-error')"), \
                "Input field shows error styling unexpectedly for valid email."
            logger.info("Input field retains valid styling, no errors detected.")

            # Additional Assertions from test case:
            # Assertion: Accessibility: Ensure the input field has a valid `aria-label` or is correctly associated with its visible label.
            aria_label = email_input.get_attribute("aria-label")
            aria_labelledby = email_input.get_attribute("aria-labelledby")
            assert aria_label or aria_labelledby, \
                "Input field is missing 'aria-label' or 'aria-labelledby' attribute."

            # Assertion: Visual AI: A visual comparison checkpoint confirms no unexpected UI elements or error states appear.
            # This is typically done with visual testing tools. For this example, we'll simulate a check.
            # Example: Compare against a baseline image or check for specific elements.
            # If using a visual testing framework like Applitools or Percy, integrate here.
            logger.info("Skipping Visual AI check in this mock implementation. Integrate with a visual testing tool.")

            # Assertion: Browser auto-fill compatibility: Verify the field accepts auto-filled data without functional degradation.
            # This often requires manual verification or specific browser emulation features.
            logger.info("Skipping Browser auto-fill compatibility check. Requires manual verification or advanced tooling.")

            logger.info("TC001 executed successfully.")

        except Exception as e:
            logger.error(f"An error occurred during TC001: {e}")
            pytest.fail(f"TC001 failed: {e}")

    @pytest.mark.critical
    @pytest.mark.general
    def test_tc002_validate_rejection_of_invalid_email_format_in_hero_section_signup(self) -> None:
        """
        TC002: Validate Rejection of Invalid Email Format in Hero Section Signup.
        Ensures the primary email input field correctly identifies and rejects
        syntactically invalid email addresses, providing clear error feedback.
        """
        test_data: Dict[str, Any] = {
            "email_invalid_format": "this-is-not-an-email",
            "expected_error_message": "Please enter a valid email address."
        }
        invalid_email = test_data["email_invalid_format"]
        expected_error_msg = test_data["expected_error_message"]

        try:
            # Step 1: Navigate to the GitHub homepage.
            logger.info(f"Navigating to {GITHUB_URL}")
            self.page.goto(GITHUB_URL)
            self.page.wait_for_load_state("domcontentloaded")
            logger.info("GitHub homepage loaded successfully.")

            # Step 2: Type a clearly invalid email format into the hero section email input.
            logger.info(f"Typing invalid email: {invalid_email} into {HERO_EMAIL_INPUT_SELECTOR}")
            email_input = self.page.locator(HERO_EMAIL_INPUT_SELECTOR)
            email_input.fill(invalid_email)

            # Assertion for step 2: Verify the text is displayed and note potential immediate feedback.
            actual_input_value = email_input.get_attribute("value")
            assert actual_input_value == invalid_email, \
                f"Expected invalid email '{invalid_email}' not found in input. Found: '{actual_input_value}'"
            logger.info(f"Invalid email '{invalid_email}' displayed in input.")

            # Step 3: Trigger field validation by blurring the input.
            logger.info(f"Blurring input field: {HERO_EMAIL_INPUT_SELECTOR}")
            email_input.blur()
            # Add a small wait for client-side validation and error message to appear
            self.page.wait_for_timeout(500) # Adjust timeout as needed

            # Step 4: Verify the input field's error state.
            logger.info(f"Verifying input field error state for {HERO_EMAIL_INPUT_SELECTOR}")

            # Assertion: A clear, user-friendly error message is displayed.
            # Assuming a common structure for error messages. Adjust selector as needed.
            error_message_selector = "css=[id*='error']" # Example: find any element with an ID containing 'error'
            # More specific selector based on common patterns or available test IDs
            potential_error_selectors = [
                f"xpath=//input[@id='{HERO_EMAIL_INPUT_SELECTOR.split('#')[-1]}']/following-sibling::div[contains(@class, 'error-message')]",
                f"xpath=//input[@id='{HERO_EMAIL_INPUT_SELECTOR.split('#')[-1]}']/../following-sibling::div[contains(@class, 'error-message')]",
                f"css=div[data-testid='{HERO_EMAIL_INPUT_SELECTOR.split('#')[-1]}-error']", # Example data-testid
                f"css=label[for='{HERO_EMAIL_INPUT_SELECTOR.split('#')[-1]}'] + div.error-message", # If error is next to label
                f"css=p[class*='help-text'][class*='error']" # General error text
            ]

            error_element = None
            for selector in potential_error_selectors:
                try:
                    found_error = self.page.locator(selector)
                    if found_error.is_visible():
                        error_element = found_error
                        actual_error_text = error_element.inner_text()
                        assert expected_error_msg in actual_error_text, \
                            f"Expected error message '{expected_error_msg}' not found. Found: '{actual_error_text}'"
                        logger.info(f"Error message '{actual_error_text}' found as expected.")
                        break
                except Exception:
                    continue # Try next selector if current one fails or element not found

            assert error_element is not None, f"Error message element not found using any of the potential selectors."

            # Assertion: The input field applies an error-indicating CSS class or attribute.
            # Check for `aria-invalid='true'` or specific error classes.
            assert email_input.get_attribute("aria-invalid") == "true", \
                "Input field is missing 'aria-invalid=\"true\"' attribute."
            # Add checks for specific error classes if known
            # assert email_input.evaluate("el => el.classList.contains('is-invalid') or el.classList.contains('has-error')"), \
            #     "Input field does not have expected error CSS classes."
            logger.info("Input field shows expected error state (e.g., 'aria-invalid=\"true\"').")

            # Assertion: Accessibility: The error message must be programmatically linked.
            aria_describedby = email_input.get_attribute("aria-describedby")
            assert aria_describedby is not None, \
                "Input field is missing 'aria-describedby' attribute to link error message."
            # Further check if the describedby ID actually points to the error element
            assert error_element and error_element.get_attribute("id") in aria_describedby, \
                "The 'aria-describedby' attribute does not correctly link to the visible error message."

            # Assertion: Visual AI: A visual comparison checkpoint confirms the error message and styling are rendered correctly.
            # Integrate with a visual testing tool here.
            logger.info("Skipping Visual AI check in this mock implementation. Integrate with a visual testing tool.")

            # Assertion: Mutation Test: Assertions should be resistant to superficial changes; check for specific error message text and attribute presence.
            # This is more of a test design principle. Ensure assertions target essential properties.

            logger.info("TC002 executed successfully.")

        except Exception as e:
            logger.error(f"An error occurred during TC002: {e}")
            pytest.fail(f"TC002 failed: {e}")

# Example of how to run this test file:
# 1. Save the code as a Python file (e.g., test_github_signup.py).
# 2. Make sure you have pytest and playwright installed:
#    pip install pytest playwright python-dotenv
# 3. Install Playwright browsers:
#    playwright install
# 4. Optionally, create a .env file in the same directory with:
#    GITHUB_URL=https://github.com
#    BROWSER_TYPE=chromium
#    HEADLESS=true
#    SLOW_MO_MS=0
# 5. Run pytest from your terminal in the same directory:
#    pytest
