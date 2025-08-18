import logging
from typing import List, Optional, Union

from playwright.sync_api import Page, TimeoutError, ElementHandle, PlaywrightException

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BasePage:
    """
    A base class for Page Object Model (POM) pages in Playwright.

    This class provides common functionalities and utilities that can be
    inherited by specific page classes. It includes methods for navigation,
    waiting, interacting with elements, handling dialogs, and taking screenshots.
    """

    def __init__(self, page: Page):
        """
        Initializes the BasePage with a Playwright Page object.

        Args:
            page: The Playwright Page object to interact with.
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_timeout = 30000  # Default timeout in milliseconds
        self.default_retries = 3      # Default number of retries

    def navigate_to(self, url: str) -> None:
        """
        Navigates the browser to the specified URL.

        Args:
            url: The URL to navigate to.

        Raises:
            PlaywrightException: If navigation fails.
        """
        try:
            self.logger.info(f"Navigating to: {url}")
            self.page.goto(url)
            self.logger.info(f"Successfully navigated to: {url}")
        except PlaywrightException as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            raise

    def wait_for_element(self, selector: str, timeout: int = None) -> ElementHandle:
        """
        Waits for an element specified by the selector to be visible and enabled.

        Args:
            selector: The CSS selector for the element.
            timeout: The maximum time in milliseconds to wait. Defaults to self.default_timeout.

        Returns:
            The Playwright ElementHandle for the located element.

        Raises:
            TimeoutError: If the element does not become visible or enabled within the timeout.
        """
        final_timeout = timeout if timeout is not None else self.default_timeout
        try:
            self.logger.info(f"Waiting for element: '{selector}' with timeout {final_timeout}ms")
            element = self.page.locator(selector).wait_for(state="visible", timeout=final_timeout)
            self.logger.info(f"Element found: '{selector}'")
            return element
        except TimeoutError:
            self.logger.error(f"Timeout waiting for element: '{selector}' after {final_timeout}ms")
            raise

    def click_with_retry(self, selector: str, retries: int = None) -> None:
        """
        Clicks an element with a specified number of retries if it's not immediately clickable.

        Args:
            selector: The CSS selector for the element to click.
            retries: The number of times to retry clicking. Defaults to self.default_retries.

        Raises:
            PlaywrightException: If the element cannot be clicked after all retries.
        """
        final_retries = retries if retries is not None else self.default_retries
        for attempt in range(final_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{final_retries}: Clicking element: '{selector}'")
                element = self.wait_for_element(selector)
                element.click()
                self.logger.info(f"Successfully clicked element: '{selector}'")
                return
            except (TimeoutError, PlaywrightException) as e:
                self.logger.warning(f"Click attempt {attempt + 1} failed for '{selector}': {e}")
                if attempt < final_retries - 1:
                    self.page.wait_for_timeout(1000)  # Wait 1 second before retrying
        self.logger.error(f"Failed to click element: '{selector}' after {final_retries} retries.")
        raise PlaywrightException(f"Could not click element '{selector}' after {final_retries} retries.")

    def fill_field(self, selector: str, value: str) -> None:
        """
        Fills a text input field with the given value.

        Args:
            selector: The CSS selector for the input field.
            value: The string value to fill into the field.

        Raises:
            PlaywrightException: If the field cannot be filled.
        """
        try:
            self.logger.info(f"Filling field '{selector}' with value: '{value}'")
            element = self.wait_for_element(selector)
            element.fill(value)
            self.logger.info(f"Successfully filled field '{selector}'")
        except PlaywrightException as e:
            self.logger.error(f"Failed to fill field '{selector}' with value '{value}': {e}")
            raise

    def get_text(self, selector: str) -> str:
        """
        Retrieves the text content of an element.

        Args:
            selector: The CSS selector for the element.

        Returns:
            The text content of the element.

        Raises:
            PlaywrightException: If the element is not found or text cannot be retrieved.
        """
        try:
            self.logger.info(f"Getting text from element: '{selector}'")
            element = self.wait_for_element(selector)
            text_content = element.text_content()
            self.logger.info(f"Retrieved text from '{selector}': '{text_content[:50]}...'")
            return text_content if text_content else ""
        except PlaywrightException as e:
            self.logger.error(f"Failed to get text from element '{selector}': {e}")
            raise

    def is_element_visible(self, selector: str) -> bool:
        """
        Checks if an element is visible on the page.

        Args:
            selector: The CSS selector for the element.

        Returns:
            True if the element is visible, False otherwise.
        """
        try:
            self.logger.debug(f"Checking visibility of element: '{selector}'")
            is_visible = self.page.locator(selector).is_visible()
            self.logger.debug(f"Element '{selector}' is visible: {is_visible}")
            return is_visible
        except PlaywrightException as e:
            self.logger.warning(f"Error checking visibility of element '{selector}': {e}")
            return False

    def take_screenshot(self, name: str) -> None:
        """
        Takes a screenshot of the current page and saves it to a file.

        The screenshot will be saved in the current working directory with the
        specified name and a .png extension.

        Args:
            name: The base name for the screenshot file (e.g., "homepage").
                  The file will be saved as "name.png".

        Raises:
            PlaywrightException: If taking the screenshot fails.
        """
        try:
            screenshot_path = f"{name}.png"
            self.logger.info(f"Taking screenshot: '{screenshot_path}'")
            self.page.screenshot(path=screenshot_path)
            self.logger.info(f"Screenshot saved to: '{screenshot_path}'")
        except PlaywrightException as e:
            self.logger.error(f"Failed to take screenshot '{name}.png': {e}")
            raise

    def wait_for_load_state(self, state: str = "load", timeout: int = None) -> None:
        """
        Waits for the page to reach a specific load state.

        Common states include "load", "domcontentloaded", and "networkidle".

        Args:
            state: The load state to wait for. Defaults to "load".
            timeout: The maximum time in milliseconds to wait. Defaults to self.default_timeout.

        Raises:
            PlaywrightException: If waiting for the load state fails.
        """
        final_timeout = timeout if timeout is not None else self.default_timeout
        try:
            self.logger.info(f"Waiting for page load state: '{state}' with timeout {final_timeout}ms")
            self.page.wait_for_load_state(state, timeout=final_timeout)
            self.logger.info(f"Page reached load state: '{state}'")
        except TimeoutError:
            self.logger.error(f"Timeout waiting for page load state '{state}' after {final_timeout}ms")
            raise
        except PlaywrightException as e:
            self.logger.error(f"Failed waiting for page load state '{state}': {e}")
            raise

    def handle_dialog(self, accept: bool, text: Optional[str] = None) -> None:
        """
        Handles a JavaScript dialog (alert, confirm, prompt).

        Args:
            accept: True to accept the dialog, False to dismiss it.
            text: The text to enter if it's a prompt dialog.

        Raises:
            PlaywrightException: If handling the dialog fails or if it's not a prompt and text is provided.
        """
        try:
            self.logger.info(f"Handling dialog: {'Accept' if accept else 'Dismiss'} (Text: {text if text else 'N/A'})")
            if accept:
                self.page.on("dialog", lambda dialog: dialog.accept(text) if dialog.type == "prompt" else dialog.accept())
                self.logger.info("Dialog accepted.")
            else:
                self.page.on("dialog", lambda dialog: dialog.dismiss())
                self.logger.info("Dialog dismissed.")
        except PlaywrightException as e:
            self.logger.error(f"Failed to handle dialog: {e}")
            raise

    def safe_click(self, selector: str, timeout: int = None) -> bool:
        """
        Safely clicks an element. Returns True if successful, False otherwise.
        This method does not raise an exception on timeout.

        Args:
            selector: The CSS selector for the element to click.
            timeout: The maximum time in milliseconds to wait for the element. Defaults to self.default_timeout.

        Returns:
            True if the click was successful, False if a TimeoutError occurred.
        """
        final_timeout = timeout if timeout is not None else self.default_timeout
        try:
            self.logger.info(f"Safely attempting to click element: '{selector}' with timeout {final_timeout}ms")
            element = self.wait_for_element(selector, timeout=final_timeout)
            element.click()
            self.logger.info(f"Safely clicked element: '{selector}'")
            return True
        except TimeoutError:
            self.logger.warning(f"Safe click failed: Timeout waiting for element '{selector}' after {final_timeout}ms")
            return False
        except PlaywrightException as e:
            self.logger.error(f"Safe click failed for element '{selector}': {e}")
            return False

    def wait_and_type(self, selector: str, text: str, timeout: int = None) -> None:
        """
        Waits for an element and then types the provided text into it.

        Args:
            selector: The CSS selector for the input field.
            text: The text to type.
            timeout: The maximum time in milliseconds to wait for the element. Defaults to self.default_timeout.

        Raises:
            PlaywrightException: If waiting for or typing into the element fails.
        """
        final_timeout = timeout if timeout is not None else self.default_timeout
        try:
            self.logger.info(f"Waiting for element and typing: '{selector}' with text: '{text}' (timeout {final_timeout}ms)")
            element = self.wait_for_element(selector, timeout=final_timeout)
            element.type(text)
            self.logger.info(f"Successfully typed '{text}' into element: '{selector}'")
        except PlaywrightException as e:
            self.logger.error(f"Failed to wait and type into element '{selector}': {e}")
            raise

    def get_element_with_fallback(self, selectors_list: List[str]) -> Optional[ElementHandle]:
        """
        Attempts to locate an element using a list of selectors, returning the
        first one found.

        Args:
            selectors_list: A list of CSS selectors to try in order.

        Returns:
            The ElementHandle of the first found element, or None if no element
            is found using any of the provided selectors.
        """
        for selector in selectors_list:
            try:
                self.logger.debug(f"Attempting to find element with selector: '{selector}'")
                # Use a short timeout for fallback, as we don't want to block indefinitely
                element = self.page.locator(selector).wait_for(state="attached", timeout=5000)
                if element:
                    self.logger.info(f"Found element using fallback selector: '{selector}'")
                    return element
            except TimeoutError:
                self.logger.debug(f"Selector '{selector}' did not yield an element within timeout.")
            except PlaywrightException as e:
                self.logger.warning(f"Error using fallback selector '{selector}': {e}")
        self.logger.warning(f"Could not find element using any of the provided fallback selectors: {selectors_list}")
        return None

# Example Usage (requires Playwright to be installed and browsers to be installed):
# pip install playwright
# playwright install

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        class ExamplePage(BasePage):
            def __init__(self, page: Page):
                super().__init__(page)
                self.url = "https://playwright.dev/"
                self.get_started_button_selector = "a[href='/docs/intro']"
                self.version_selector = ".version"
                self.non_existent_selector = "id=does-not-exist"

            def go_to_example_page(self) -> None:
                self.navigate_to(self.url)
                self.wait_for_load_state()

            def click_get_started(self) -> None:
                self.click_with_retry(self.get_started_button_selector)

            def get_version_text(self) -> str:
                return self.get_text(self.version_selector)

            def check_element_visibility(self) -> bool:
                return self.is_element_visible(self.get_started_button_selector)

            def check_non_existent_visibility(self) -> bool:
                return self.is_element_visible(self.non_existent_selector)

            def type_into_search(self, query: str) -> None:
                search_input_selector = "input[name='search']"
                self.wait_and_type(search_input_selector, query)

        example_page = ExamplePage(page)

        try:
            print("\n--- Testing BasePage Functionality ---")

            # Test navigation
            example_page.go_to_example_page()
            print("Navigation successful.")

            # Test wait_for_element and get_text
            version = example_page.get_version_text()
            print(f"Version text: {version}")

            # Test is_element_visible
            is_visible = example_page.check_element_visibility()
            print(f"Get Started button is visible: {is_visible}")
            is_not_visible = example_page.check_non_existent_visibility()
            print(f"Non-existent element is visible: {is_not_visible}")

            # Test wait_and_type
            example_page.type_into_search("Playwright")
            print("Typed into search bar.")

            # Test click_with_retry
            # Let's simulate a case where the click might fail initially (though unlikely for this stable element)
            # For demonstration, we'll just call it. In a real scenario, you'd test flaky elements.
            print("Attempting click_with_retry on Get Started button...")
            example_page.click_with_retry(example_page.get_started_button_selector)
            print("click_with_retry completed.")

            # Test safe_click
            print("Testing safe_click...")
            safe_click_success = example_page.safe_click("a[href='/docs/intro']")
            print(f"Safe click successful: {safe_click_success}")
            safe_click_fail = example_page.safe_click("id=non-existent-id", timeout=2000)
            print(f"Safe click on non-existent element successful: {safe_click_fail}")

            # Test get_element_with_fallback
            print("Testing get_element_with_fallback...")
            # Try finding a known element with a list including a wrong one first
            fallback_element = example_page.get_element_with_fallback([
                "id=non-existent-selector-first",
                "a[href='/docs/intro']",
                "div.main-header"
            ])
            if fallback_element:
                print(f"Found element using fallback: {fallback_element.inner_text()[:30]}...")
            else:
                print("Failed to find element using fallback selectors.")

            # Test take_screenshot
            example_page.take_screenshot("example_page_screenshot")
            print("Screenshot taken.")

            # Test handle_dialog (requires a page that triggers a dialog)
            # For demonstration, we'll skip actual dialog handling as it requires specific page setup.
            # If you had a page with `alert('test')`, you could do:
            # example_page.page.evaluate("alert('test')")
            # example_page.handle_dialog(accept=True)
            print("Skipping dialog handling test for brevity.")

            print("\n--- BasePage functionality tests completed ---")

        except Exception as e:
            print(f"\nAn error occurred during testing: {e}")
            example_page.take_screenshot("error_screenshot")
            print("Error screenshot taken.")

        finally:
            browser.close()
