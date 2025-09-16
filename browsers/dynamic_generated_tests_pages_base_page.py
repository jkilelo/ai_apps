import logging
from typing import List, Optional, Union

from playwright.sync_api import Page, TimeoutError, Error as PlaywrightError

# Configure basic logging for demonstration purposes
# In a real application, this would likely be configured at the application entry point
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class BasePage:
    """
    A base class for Page Object Model (POM) pages, providing common
    web interaction functionalities.

    This class encapsulates actions like navigation, waiting, clicking,
    typing, and screenshotting, making it easier to build robust and
    maintainable test automation scripts. It utilizes Playwright's
    synchronous API.
    """

    def __init__(self, page: Page):
        """
        Initializes the BasePage with a Playwright Page object.

        Args:
            page: The Playwright Page object to interact with.
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("BasePage initialized.")

    def navigate_to(self, url: str) -> None:
        """
        Navigates the page to the specified URL.

        Args:
            url: The URL to navigate to.

        Raises:
            PlaywrightError: If navigation fails.
        """
        try:
            self.logger.info(f"Navigating to URL: {url}")
            self.page.goto(url)
            self.logger.info(f"Successfully navigated to: {url}")
        except PlaywrightError as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            raise

    def wait_for_element(self, selector: str, timeout: int = 30000) -> None:
        """
        Waits for an element specified by the selector to be visible.

        Args:
            selector: The CSS selector or locator for the element.
            timeout: The maximum time in milliseconds to wait for the element.

        Raises:
            TimeoutError: If the element is not visible within the timeout.
            PlaywrightError: For other Playwright-related errors.
        """
        try:
            self.logger.info(f"Waiting for element: {selector} with timeout {timeout}ms")
            self.page.wait_for_selector(selector, timeout=timeout)
            self.logger.info(f"Element found: {selector}")
        except TimeoutError:
            self.logger.error(f"Element not found within timeout: {selector}")
            raise
        except PlaywrightError as e:
            self.logger.error(f"An error occurred while waiting for element {selector}: {e}")
            raise

    def click_with_retry(self, selector: str, retries: int = 3, timeout: int = 30000) -> bool:
        """
        Attempts to click an element, retrying if it fails.

        This method is useful for elements that might be temporarily
        unclickable due to animations or race conditions.

        Args:
            selector: The CSS selector or locator for the element to click.
            retries: The number of times to retry the click operation.
            timeout: The maximum time in milliseconds to wait for the element to be clickable.

        Returns:
            True if the click was successful within the retries, False otherwise.
        """
        for attempt in range(retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{retries}: Clicking element: {selector}")
                self.page.click(selector, timeout=timeout)
                self.logger.info(f"Successfully clicked element: {selector}")
                return True
            except TimeoutError:
                self.logger.warning(f"Attempt {attempt + 1}/{retries}: Element not clickable: {selector}. Retrying...")
                if attempt < retries - 1:
                    self.page.wait_for_timeout(1000)  # Wait 1 second before retrying
                else:
                    self.logger.error(f"Failed to click element after {retries} retries: {selector}")
                    return False
            except PlaywrightError as e:
                self.logger.error(f"Attempt {attempt + 1}/{retries}: An error occurred while clicking {selector}: {e}")
                if attempt < retries - 1:
                    self.page.wait_for_timeout(1000)
                else:
                    return False
        return False

    def fill_field(self, selector: str, value: str) -> None:
        """
        Fills a form field with the specified value.

        This method first waits for the element to be visible and then fills it.
        It clears the field before typing.

        Args:
            selector: The CSS selector or locator for the input field.
            value: The string value to enter into the field.

        Raises:
            PlaywrightError: If the field is not found or an error occurs during typing.
        """
        try:
            self.logger.info(f"Filling field '{selector}' with value: '********'")  # Masking value for logging
            self.wait_for_element(selector)
            self.page.locator(selector).fill(value)
            self.logger.info(f"Successfully filled field '{selector}'.")
        except PlaywrightError as e:
            self.logger.error(f"Failed to fill field '{selector}': {e}")
            raise

    def get_text(self, selector: str) -> str:
        """
        Retrieves the text content of an element.

        Args:
            selector: The CSS selector or locator for the element.

        Returns:
            The text content of the element.

        Raises:
            PlaywrightError: If the element is not found or an error occurs.
        """
        try:
            self.logger.info(f"Getting text from element: {selector}")
            self.wait_for_element(selector)
            element_text = self.page.locator(selector).text_content()
            if element_text is None:
                element_text = ""  # Handle cases where text_content might return None
            self.logger.info(f"Text retrieved from '{selector}': '{element_text[:50]}...'")  # Log snippet
            return element_text
        except PlaywrightError as e:
            self.logger.error(f"Failed to get text from element {selector}: {e}")
            raise

    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Checks if an element is visible on the page.

        Args:
            selector: The CSS selector or locator for the element.
            timeout: The maximum time in milliseconds to wait for visibility.

        Returns:
            True if the element is visible, False otherwise.
        """
        try:
            self.logger.debug(f"Checking visibility of element: {selector} with timeout {timeout}ms")
            is_visible = self.page.locator(selector).is_visible(timeout=timeout)
            self.logger.debug(f"Element '{selector}' visibility: {is_visible}")
            return is_visible
        except TimeoutError:
            self.logger.debug(f"Element '{selector}' not visible within timeout {timeout}ms.")
            return False
        except PlaywrightError as e:
            self.logger.warning(f"An error occurred checking visibility of {selector}: {e}. Assuming not visible.")
            return False

    def take_screenshot(self, name: str, full_page: bool = False) -> None:
        """
        Takes a screenshot of the current page or a specific element.

        Args:
            name: The base name for the screenshot file (e.g., "homepage").
                  The actual filename will include a timestamp.
            full_page: If True, captures the entire scrollable page. If False,
                       captures only the currently visible viewport.
        """
        try:
            timestamp = self.page.evaluate("new Date().toISOString().replace(/[:.]/g, '-')")
            filename = f"{name}_{timestamp}.png"
            self.logger.info(f"Taking screenshot: {filename}")
            self.page.screenshot(path=filename, full_page=full_page)
            self.logger.info(f"Screenshot saved as: {filename}")
        except PlaywrightError as e:
            self.logger.error(f"Failed to take screenshot '{filename}': {e}")
            # Depending on requirements, you might want to re-raise or just log

    def wait_for_load_state(self, state: str = "load", timeout: int = 60000) -> None:
        """
        Waits for the page to reach a specific load state.

        Common states include: 'load', 'domcontentloaded', 'networkidle'.

        Args:
            state: The load state to wait for. Defaults to 'load'.
            timeout: The maximum time in milliseconds to wait.

        Raises:
            PlaywrightError: If the timeout is reached or an error occurs.
        """
        if state not in ["load", "domcontentloaded", "networkidle"]:
            self.logger.warning(f"Invalid load state '{state}'. Using 'load' instead.")
            state = "load"

        try:
            self.logger.info(f"Waiting for page load state: '{state}' with timeout {timeout}ms")
            self.page.wait_for_load_state(state, timeout=timeout)
            self.logger.info(f"Page reached '{state}' load state.")
        except TimeoutError:
            self.logger.error(f"Timeout waiting for page load state '{state}'.")
            raise
        except PlaywrightError as e:
            self.logger.error(f"An error occurred while waiting for load state '{state}': {e}")
            raise

    def handle_dialog(self, accept: bool, text: Optional[str] = None, timeout: int = 5000) -> bool:
        """
        Handles JavaScript dialogs (alert, confirm, prompt).

        Args:
            accept: True to accept the dialog (click OK), False to dismiss (click Cancel).
            text: The text to enter if it's a prompt dialog.
            timeout: The maximum time in milliseconds to wait for the dialog.

        Returns:
            True if the dialog was handled successfully, False otherwise.
        """
        try:
            self.logger.info(f"Handling dialog: accept={accept}, text={text if text else 'N/A'}")
            # Using wait_for_event to ensure the dialog is present before handling
            with self.page.expect_dialog(timeout=timeout) as dialog_info:
                if accept:
                    dialog_info.value.accept(text)
                    self.logger.info("Dialog accepted.")
                else:
                    dialog_info.value.dismiss()
                    self.logger.info("Dialog dismissed.")
            return True
        except TimeoutError:
            self.logger.error(f"Timeout waiting for dialog.")
            return False
        except PlaywrightError as e:
            self.logger.error(f"An error occurred handling dialog: {e}")
            return False

    def safe_click(self, selector: str, timeout: int = 30000) -> bool:
        """
        Safely attempts to click an element without raising an exception on timeout.

        This method waits for the element to be clickable and then clicks it.
        It returns True if successful, False if a TimeoutError occurs.

        Args:
            selector: The CSS selector or locator for the element to click.
            timeout: The maximum time in milliseconds to wait for the element to be clickable.

        Returns:
            True if the click was successful, False if a TimeoutError occurred.
        """
        try:
            self.logger.info(f"Attempting to safely click element: {selector} with timeout {timeout}ms")
            self.page.click(selector, timeout=timeout)
            self.logger.info(f"Successfully clicked element: {selector}")
            return True
        except TimeoutError:
            self.logger.warning(f"Timeout waiting for element to be clickable: {selector}")
            return False
        except PlaywrightError as e:
            self.logger.error(f"An error occurred during safe click for {selector}: {e}")
            return False

    def wait_and_type(self, selector: str, text: str, timeout: int = 30000) -> None:
        """
        Waits for an element to be visible and then types text into it.

        This is a convenience method that combines waiting and filling.

        Args:
            selector: The CSS selector or locator for the input field.
            text: The string value to type into the field.
            timeout: The maximum time in milliseconds to wait for the element.

        Raises:
            PlaywrightError: If the element is not found or an error occurs during typing.
        """
        try:
            self.logger.info(f"Waiting for element '{selector}' and typing: '********'")  # Masking value
            self.wait_for_element(selector, timeout=timeout)
            self.page.locator(selector).type(text)
            self.logger.info(f"Successfully typed into field '{selector}'.")
        except PlaywrightError as e:
            self.logger.error(f"Failed to wait and type into field '{selector}': {e}")
            raise

    def get_element_with_fallback(self, selectors_list: List[str], timeout: int = 10000) -> Optional[str]:
        """
        Attempts to find an element using a list of selectors and returns the first one found.

        This is useful when an element's selector might change slightly but can be
        identified by a set of alternative locators.

        Args:
            selectors_list: A list of CSS selectors or locators to try in order.
            timeout: The maximum time in milliseconds to wait for any of the elements.

        Returns:
            The CSS selector of the first element found, or None if none are found within the timeout.
        """
        self.logger.info(f"Attempting to find element with fallback selectors: {selectors_list}")
        for selector in selectors_list:
            try:
                self.logger.debug(f"Trying selector: {selector}")
                self.page.wait_for_selector(selector, timeout=timeout)
                self.logger.info(f"Element found using selector: {selector}")
                return selector
            except TimeoutError:
                self.logger.debug(f"Selector '{selector}' timed out.")
                continue  # Try the next selector
            except PlaywrightError as e:
                self.logger.warning(f"Error checking selector '{selector}': {e}. Trying next.")
                continue

        self.logger.warning("No element found with any of the provided fallback selectors.")
        return None


if __name__ == '__main__':
    # Example Usage (requires Playwright to be installed and browsers to be installed)
    # To run this example:
    # 1. Save the code as base_page.py
    # 2. Run: pip install playwright
    # 3. Run: playwright install
    # 4. Run: python base_page.py

    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            base_page = BasePage(page)

            # --- Test Navigation ---
            try:
                base_page.navigate_to("https://www.example.com")
            except Exception as e:
                print(f"Navigation test failed: {e}")

            # --- Test Wait for Element ---
            try:
                base_page.wait_for_element("h1")
                print("Wait for element 'h1' test passed.")
            except Exception as e:
                print(f"Wait for element 'h1' test failed: {e}")

            # --- Test Get Text ---
            try:
                example_text = base_page.get_text("h1")
                print(f"Get text 'h1' test passed. Text: {example_text}")
            except Exception as e:
                print(f"Get text 'h1' test failed: {e}")

            # --- Test Fill Field (using a different site with an input) ---
            try:
                page.goto("https://the-internet.herokuapp.com/login")
                base_page.wait_for_element("#username")
                base_page.fill_field("#username", "testuser")
                base_page.fill_field("#password", "password123")
                print("Fill field tests passed.")
            except Exception as e:
                print(f"Fill field tests failed: {e}")

            # --- Test Safe Click ---
            try:
                if base_page.safe_click("button[type='submit']", timeout=5000):
                    print("Safe click 'submit' button test passed.")
                else:
                    print("Safe click 'submit' button test failed (element not clickable).")
            except Exception as e:
                print(f"Safe click test failed: {e}")

            # --- Test Wait and Type ---
            try:
                page.goto("https://the-internet.herokuapp.com/login")
                base_page.wait_and_type("#username", "anotheruser")
                base_page.wait_and_type("#password", "securepass")
                print("Wait and type tests passed.")
            except Exception as e:
                print(f"Wait and type tests failed: {e}")

            # --- Test Is Element Visible ---
            try:
                if base_page.is_element_visible("#username"):
                    print("Is element visible '#username' test passed.")
                else:
                    print("Is element visible '#username' test failed.")

                if not base_page.is_element_visible(".non-existent-element", timeout=1000):
                    print("Is element visible '.non-existent-element' test passed (correctly not found).")
                else:
                    print("Is element visible '.non-existent-element' test failed (incorrectly found).")
            except Exception as e:
                print(f"Is element visible test failed: {e}")

            # --- Test Click with Retry ---
            # This is harder to demo simply without a specific flaky element.
            # Imagine a button that sometimes takes a moment to become clickable.
            try:
                page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
                base_page.wait_for_element("#start button")
                if base_page.click_with_retry("#start button"):
                    print("Click with retry 'start button' test passed.")
                    base_page.wait_for_element("#finish") # wait for result
                    if base_page.is_element_visible("#finish"):
                        print("Dynamic loading content appeared as expected.")
                    else:
                        print("Dynamic loading content did not appear.")
                else:
                    print("Click with retry 'start button' test failed.")
            except Exception as e:
                print(f"Click with retry test failed: {e}")

            # --- Test Take Screenshot ---
            try:
                base_page.take_screenshot("example_page")
                print("Take screenshot test executed (check directory for example_page_*.png).")
            except Exception as e:
                print(f"Take screenshot test failed: {e}")

            # --- Test Wait for Load State ---
            try:
                base_page.navigate_to("https://www.example.com")
                base_page.wait_for_load_state("domcontentloaded")
                print("Wait for load state 'domcontentloaded' test passed.")
            except Exception as e:
                print(f"Wait for load state test failed: {e}")

            # --- Test Handle Dialog (confirm example) ---
            try:
                page.goto("https://the-internet.herokuapp.com/javascript_alerts")
                base_page.wait_for_element("#content > div > ul > li:nth-child(2) > button")
                # Click the button that triggers the confirm dialog
                page.locator("#content > div > ul > li:nth-child(2) > button").click()
                # Dismiss the dialog
                if base_page.handle_dialog(accept=False, timeout=2000):
                    print("Handle dialog (dismiss) test passed.")
                    # Verify the result message
                    if base_page.get_text("#result") == "You clicked Cancel":
                        print("Dialog dismissal result verified.")
                    else:
                        print(f"Dialog dismissal result mismatch: {base_page.get_text('#result')}")
                else:
                    print("Handle dialog (dismiss) test failed.")

                # Click again to trigger the confirm dialog
                page.locator("#content > div > ul > li:nth-child(2) > button").click()
                # Accept the dialog
                if base_page.handle_dialog(accept=True, timeout=2000):
                    print("Handle dialog (accept) test passed.")
                    # Verify the result message
                    if base_page.get_text("#result") == "You clicked Ok":
                        print("Dialog acceptance result verified.")
                    else:
                        print(f"Dialog acceptance result mismatch: {base_page.get_text('#result')}")
                else:
                    print("Handle dialog (accept) test failed.")

            except Exception as e:
                print(f"Handle dialog test failed: {e}")

            # --- Test Get Element with Fallback ---
            try:
                page.goto("https://www.example.com")
                found_selector = base_page.get_element_with_fallback(["h1.nonexistent", "h1"])
                if found_selector == "h1":
                    print("Get element with fallback test passed (found 'h1').")
                else:
                    print(f"Get element with fallback test failed (expected 'h1', got '{found_selector}').")

                found_selector_fail = base_page.get_element_with_fallback(["h1.nonexistent", "h2.nonexistent"], timeout=1000)
                if found_selector_fail is None:
                    print("Get element with fallback test passed (correctly found no element).")
                else:
                    print(f"Get element with fallback test failed (expected None, got '{found_selector_fail}').")
            except Exception as e:
                print(f"Get element with fallback test failed: {e}")

            browser.close()

    except Exception as e:
        print(f"An error occurred during the example execution: {e}")
