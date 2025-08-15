import logging
from typing import List, Optional, Union
from playwright.sync_api import Page, TimeoutError, Error, Locator
from urllib.parse import urlparse

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BasePage:
    """
    Base class for all Page Objects in the Page Object Model.

    Provides common functionalities such as navigation, element interaction,
    waiting, and error handling.
    """

    def __init__(self, page: Page):
        """
        Initializes the BasePage with a Playwright Page object.

        Args:
            page: The Playwright Page object to interact with.
        """
        if not isinstance(page, Page):
            raise TypeError("page must be an instance of playwright.sync_api.Page")
        self.page: Page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    def navigate_to(self, url: str) -> None:
        """
        Navigates the browser to the specified URL.

        Args:
            url: The URL to navigate to.

        Raises:
            ValueError: If the provided URL is invalid.
            Error: If Playwright encounters an error during navigation.
        """
        if not isinstance(url, str) or not urlparse(url).scheme or not urlparse(url).netloc:
            raise ValueError(f"Invalid URL provided: {url}")
        try:
            self.logger.info(f"Navigating to URL: {url}")
            self.page.goto(url)
            self.logger.info(f"Successfully navigated to: {url}")
        except Error as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            raise

    def wait_for_element(self, selector: str, timeout: int = 30000) -> Locator:
        """
        Waits for an element specified by the selector to be visible.

        Args:
            selector: The CSS selector or Playwright locator string for the element.
            timeout: The maximum time in milliseconds to wait for the element.

        Returns:
            The Playwright Locator object for the found element.

        Raises:
            TimeoutError: If the element is not visible within the specified timeout.
            Error: If Playwright encounters an error while waiting for the element.
        """
        if not isinstance(selector, str) or not selector:
            raise ValueError("Selector must be a non-empty string.")
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")
        try:
            self.logger.debug(f"Waiting for element: '{selector}' with timeout {timeout}ms")
            element = self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            self.logger.debug(f"Element '{selector}' is visible.")
            return element
        except TimeoutError:
            self.logger.error(f"Element '{selector}' did not become visible within {timeout}ms.")
            raise
        except Error as e:
            self.logger.error(f"An error occurred while waiting for element '{selector}': {e}")
            raise

    def click_with_retry(self, selector: str, retries: int = 3, timeout: int = 10000) -> bool:
        """
        Clicks an element with a specified selector, retrying if it fails.

        Args:
            selector: The CSS selector or Playwright locator string for the element.
            retries: The number of times to retry the click operation.
            timeout: The timeout in milliseconds for each click attempt.

        Returns:
            True if the click was successful, False otherwise.
        """
        if not isinstance(selector, str) or not selector:
            raise ValueError("Selector must be a non-empty string.")
        if not isinstance(retries, int) or retries < 0:
            raise ValueError("Retries must be a non-negative integer.")
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")

        for attempt in range(retries + 1):
            try:
                self.logger.debug(f"Attempt {attempt + 1}/{retries + 1}: Clicking element '{selector}' with timeout {timeout}ms.")
                self.page.locator(selector).click(timeout=timeout)
                self.logger.info(f"Successfully clicked element: '{selector}'")
                return True
            except TimeoutError:
                self.logger.warning(f"Attempt {attempt + 1}/{retries + 1}: Element '{selector}' not clickable or not visible within {timeout}ms.")
                if attempt < retries:
                    self.logger.info("Retrying click...")
                    self.page.wait_for_timeout(1000)  # Wait a bit before retrying
            except Error as e:
                self.logger.error(f"Attempt {attempt + 1}/{retries + 1}: An error occurred during click for '{selector}': {e}")
                if attempt < retries:
                    self.logger.info("Retrying click due to error...")
                    self.page.wait_for_timeout(1000)
                else:
                    return False
        self.logger.error(f"Failed to click element '{selector}' after {retries + 1} attempts.")
        return False

    def fill_field(self, selector: str, value: str) -> None:
        """
        Fills a form field with the specified value.

        Args:
            selector: The CSS selector or Playwright locator string for the input field.
            value: The string value to fill into the field.

        Raises:
            ValueError: If the selector or value is invalid.
            Error: If Playwright encounters an error during the fill operation.
        """
        if not isinstance(selector, str) or not selector:
            raise ValueError("Selector must be a non-empty string.")
        if not isinstance(value, str):
            raise ValueError("Value must be a string.")

        try:
            self.logger.debug(f"Filling field '{selector}' with value: '{value[:50]}{'...' if len(value) > 50 else ''}'")
            self.wait_for_element(selector)  # Ensure element is visible before filling
            self.page.locator(selector).fill(value)
            self.logger.info(f"Successfully filled field '{selector}'.")
        except TimeoutError:
            self.logger.error(f"Timeout waiting for field '{selector}' to fill.")
            raise
        except Error as e:
            self.logger.error(f"Error filling field '{selector}' with value '{value}': {e}")
            raise

    def get_text(self, selector: str) -> str:
        """
        Retrieves the text content of an element.

        Args:
            selector: The CSS selector or Playwright locator string for the element.

        Returns:
            The text content of the element.

        Raises:
            ValueError: If the selector is invalid.
            Error: If Playwright encounters an error while getting the text.
        """
        if not isinstance(selector, str) or not selector:
            raise ValueError("Selector must be a non-empty string.")

        try:
            element = self.wait_for_element(selector)
            text_content = element.text_content()
            self.logger.debug(f"Retrieved text for '{selector}': '{text_content[:50]}{'...' if len(text_content) > 50 else ''}'")
            return text_content
        except TimeoutError:
            self.logger.error(f"Timeout waiting to get text from element '{selector}'.")
            raise
        except Error as e:
            self.logger.error(f"Error getting text from element '{selector}': {e}")
            raise

    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Checks if an element is visible on the page.

        Args:
            selector: The CSS selector or Playwright locator string for the element.
            timeout: The maximum time in milliseconds to wait for the element's visibility check.

        Returns:
            True if the element is visible, False otherwise.
        """
        if not isinstance(selector, str) or not selector:
            raise ValueError("Selector must be a non-empty string.")
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")

        try:
            self.logger.debug(f"Checking visibility of element: '{selector}' with timeout {timeout}ms.")
            is_visible = self.page.locator(selector).is_visible(timeout=timeout)
            self.logger.debug(f"Element '{selector}' visibility: {is_visible}")
            return is_visible
        except TimeoutError:
            self.logger.warning(f"Element '{selector}' not visible within {timeout}ms.")
            return False
        except Error as e:
            self.logger.error(f"An error occurred while checking visibility of '{selector}': {e}")
            return False

    def take_screenshot(self, name: str, full_page: bool = False) -> None:
        """
        Takes a screenshot of the current page or a specific element.

        Args:
            name: The base name for the screenshot file (e.g., 'homepage').
                  The actual filename will include a timestamp.
            full_page: Whether to capture the entire scrollable page. Defaults to False.

        Raises:
            ValueError: If the screenshot name is invalid.
            Error: If Playwright encounters an error during screenshot capture.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Screenshot name must be a non-empty string.")
        if not isinstance(full_page, bool):
            raise ValueError("full_page must be a boolean.")

        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            self.logger.info(f"Taking screenshot: '{filename}' (full_page={full_page})")
            self.page.screenshot(path=filename, full_page=full_page)
            self.logger.info(f"Screenshot saved to: {filename}")
        except Error as e:
            self.logger.error(f"Error taking screenshot '{filename}': {e}")
            raise

    def wait_for_load_state(self, state: str = "load", timeout: int = 30000) -> None:
        """
        Waits for the page to reach a specific load state.

        Args:
            state: The load state to wait for. Common values: "load", "domcontentloaded", "networkidle".
                   Defaults to "load".
            timeout: The maximum time in milliseconds to wait for the load state.

        Raises:
            ValueError: If the provided state is not a recognized load state or timeout is invalid.
            Error: If Playwright encounters an error while waiting.
        """
        valid_states = ["load", "domcontentloaded", "networkidle"]
        if state not in valid_states:
            raise ValueError(f"Invalid state '{state}'. Must be one of: {valid_states}")
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")

        try:
            self.logger.debug(f"Waiting for page load state: '{state}' with timeout {timeout}ms")
            self.page.wait_for_load_state(state, timeout=timeout)
            self.logger.info(f"Page reached '{state}' load state.")
        except TimeoutError:
            self.logger.error(f"Page did not reach '{state}' load state within {timeout}ms.")
            raise
        except Error as e:
            self.logger.error(f"An error occurred while waiting for load state '{state}': {e}")
            raise

    def handle_dialog(self, accept: bool, text: Optional[str] = None, timeout: int = 5000) -> None:
        """
        Handles a JavaScript dialog (alert, confirm, prompt).

        Args:
            accept: True to accept (click OK/Yes), False to dismiss (click Cancel/No).
            text: The text to enter into a prompt dialog. Only applicable if `accept` is True.
            timeout: The maximum time in milliseconds to wait for the dialog.

        Raises:
            ValueError: If the text is provided for a non-prompt dialog or timeout is invalid.
            Error: If Playwright encounters an error while handling the dialog.
        """
        if not isinstance(accept, bool):
            raise ValueError("Accept must be a boolean.")
        if text is not None and not isinstance(text, str):
            raise ValueError("Text must be a string or None.")
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")

        try:
            self.logger.debug(f"Handling dialog: accept={accept}, text='{text}', timeout={timeout}ms")
            # Playwright automatically handles dialogs that appear during page operations
            # This method is more for explicit handling or when waiting for a specific dialog type
            # For general dialog handling during navigation, one might use page.on("dialog", ...)
            # However, if we expect a dialog *after* an action, this pattern can be useful.
            # For simplicity and common use cases, we'll use wait_for_event which might be overkill
            # or directly interact with the dialog if it appears.
            # A more robust approach for guaranteed dialog handling is using event listeners.
            # For this method signature, we'll assume an expected dialog and attempt to handle it.

            # This is a simplified approach. In real scenarios, you'd likely attach a listener
            # before the action that triggers the dialog.
            # The following code attempts to handle a dialog that *might* appear.
            dialog = self.page.wait_for_event("dialog", timeout=timeout)
            if dialog:
                if accept:
                    if text is not None:
                        dialog.accept(text)
                        self.logger.info(f"Accepted dialog with text '{text}'.")
                    else:
                        dialog.accept()
                        self.logger.info("Accepted dialog.")
                else:
                    dialog.dismiss()
                    self.logger.info("Dismissed dialog.")
            else:
                self.logger.warning("No dialog appeared within the timeout.")

        except TimeoutError:
            self.logger.warning(f"No dialog appeared within the specified timeout of {timeout}ms.")
        except Error as e:
            self.logger.error(f"An error occurred while handling dialog: {e}")
            raise

    def safe_click(self, selector: str, timeout: int = 30000) -> bool:
        """
        Safely clicks an element if it's visible and enabled, returning success status.

        Args:
            selector: The CSS selector or Playwright locator string for the element.
            timeout: The maximum time in milliseconds to wait for the element to be clickable.

        Returns:
            True if the click was successful, False otherwise.
        """
        if not isinstance(selector, str) or not selector:
            raise ValueError("Selector must be a non-empty string.")
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")

        try:
            self.logger.debug(f"Attempting safe click on element: '{selector}' with timeout {timeout}ms.")
            locator = self.page.locator(selector)
            locator.click(timeout=timeout)
            self.logger.info(f"Successfully clicked element: '{selector}'.")
            return True
        except TimeoutError:
            self.logger.warning(f"Element '{selector}' not clickable or not visible within {timeout}ms.")
            return False
        except Error as e:
            self.logger.error(f"An error occurred during safe click on '{selector}': {e}")
            return False

    def wait_and_type(self, selector: str, text: str, timeout: int = 30000) -> None:
        """
        Waits for an element to be visible and then types text into it.

        Args:
            selector: The CSS selector or Playwright locator string for the input field.
            text: The string to type into the field.
            timeout: The maximum time in milliseconds to wait for the element.

        Raises:
            ValueError: If selector or text is invalid.
            Error: If Playwright encounters an error during the operation.
        """
        if not isinstance(selector, str) or not selector:
            raise ValueError("Selector must be a non-empty string.")
        if not isinstance(text, str):
            raise ValueError("Text must be a string.")
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")

        try:
            self.logger.debug(f"Waiting for and typing into field '{selector}' with text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            element = self.wait_for_element(selector, timeout=timeout)
            element.type(text)
            self.logger.info(f"Successfully typed into field '{selector}'.")
        except TimeoutError:
            self.logger.error(f"Timeout waiting for element '{selector}' to type into.")
            raise
        except Error as e:
            self.logger.error(f"Error typing into field '{selector}' with text '{text}': {e}")
            raise

    def get_element_with_fallback(self, selectors_list: List[str]) -> Locator:
        """
        Finds the first visible element from a list of selectors.

        Args:
            selectors_list: A list of CSS selectors or Playwright locator strings.

        Returns:
            The Playwright Locator object for the first found visible element.

        Raises:
            ValueError: If the selectors_list is empty or contains invalid selectors.
            TimeoutError: If no element is found visible from the provided selectors.
            Error: If Playwright encounters an error during the search.
        """
        if not isinstance(selectors_list, list) or not selectors_list:
            raise ValueError("selectors_list must be a non-empty list of strings.")
        if not all(isinstance(s, str) and s for s in selectors_list):
            raise ValueError("All items in selectors_list must be non-empty strings.")

        for selector in selectors_list:
            try:
                self.logger.debug(f"Attempting to find element with selector: '{selector}'")
                locator = self.page.locator(selector)
                # Check if the locator is attached and visible
                if locator.count() > 0 and locator.is_visible():
                    self.logger.info(f"Found visible element using selector: '{selector}'")
                    return locator
                self.logger.debug(f"Element with selector '{selector}' not found or not visible.")
            except Error as e:
                self.logger.warning(f"Error checking selector '{selector}': {e}. Trying next selector.")
                continue  # Continue to the next selector if an error occurs for this one

        self.logger.error(f"Could not find any visible element from the provided selectors: {selectors_list}")
        raise TimeoutError(f"None of the provided selectors found a visible element: {selectors_list}")

if __name__ == '__main__':
    # Example usage (requires Playwright to be installed and browsers to be installed)
    # To run this example:
    # 1. Install playwright: pip install playwright
    # 2. Install browsers: playwright install

    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            class SamplePage(BasePage):
                def __init__(self, page: Page):
                    super().__init__(page)
                    self.url = "https://playwright.dev/"
                    self.get_started_button_selector = "a[href='/docs/intro']"
                    self.search_input_selector = "input[type='search']"
                    self.search_results_selector = ".DocSearch-Hit-title"
                    self.dialog_button_selector = "button[onclick='alert(\"Hello!\")']" # Example for alert

                def click_get_started(self) -> None:
                    self.click_with_retry(self.get_started_button_selector)

                def search(self, query: str) -> None:
                    self.wait_and_type(self.search_input_selector, query)
                    # Wait for search results to potentially appear
                    self.page.press(self.search_input_selector, "Enter")
                    self.wait_for_element(self.search_results_selector, timeout=10000)

                def get_first_search_result_text(self) -> str:
                    return self.get_text(self.search_results_selector)

                def trigger_dialog(self) -> None:
                    self.logger.info("Triggering a JavaScript alert dialog.")
                    self.page.evaluate("alert('This is a test alert!');")
                    # Or use a button that triggers it:
                    # self.safe_click(self.dialog_button_selector)


            sample_page = SamplePage(page)

            # Test navigate_to
            sample_page.navigate_to(sample_page.url)

            # Test wait_for_element and get_text
            try:
                get_started_text = sample_page.get_text(sample_page.get_started_button_selector)
                print(f"\nText of 'Get Started' button: {get_started_text}")
            except TimeoutError:
                print("\n'Get Started' button not found.")

            # Test safe_click and take_screenshot
            if sample_page.safe_click(sample_page.get_started_button_selector):
                sample_page.take_screenshot("after_get_started_click")
            else:
                print("\nFailed to safe_click 'Get Started' button.")

            # Test wait_and_type and is_element_visible
            try:
                sample_page.wait_and_type(sample_page.search_input_selector, "Playwright")
                if sample_page.is_element_visible(sample_page.search_input_selector):
                    print("\nSearch input is visible after typing.")
            except (TimeoutError, ValueError) as e:
                print(f"\nError during wait_and_type or is_element_visible: {e}")

            # Test search functionality
            try:
                sample_page.search("Page Object Model")
                first_result = sample_page.get_first_search_result_text()
                print(f"\nFirst search result: {first_result}")
            except (TimeoutError, ValueError) as e:
                print(f"\nError during search: {e}")

            # Test wait_for_load_state
            sample_page.navigate_to(sample_page.url)
            sample_page.wait_for_load_state("networkidle")
            print("\nWaited for networkidle state.")

            # Test handle_dialog (this example focuses on alert, prompt/confirm would need adjustment)
            # For demonstration, we'll trigger an alert and attempt to handle it.
            # In a real scenario, you'd likely listen for dialogs *before* the action.
            try:
                sample_page.trigger_dialog()
                # Note: wait_for_event in handle_dialog might catch this.
                # The manual accept/dismiss here is illustrative.
                # A more common pattern is `page.on("dialog", lambda dialog: dialog.accept())` before the action.
                print("\nAttempted to handle dialog.")
            except TimeoutError:
                 print("\nDialog did not appear or could not be handled.")
            except Exception as e:
                print(f"\nError during dialog handling test: {e}")


            # Test get_element_with_fallback
            try:
                fallback_selectors = ["#nonexistent-id", "article[role='main'] p", "footer"]
                main_content_locator = sample_page.get_element_with_fallback(fallback_selectors)
                print(f"\nFound element using fallback: {main_content_locator.inner_text()[:50]}...")
            except (TimeoutError, ValueError) as e:
                print(f"\nError during get_element_with_fallback: {e}")


            browser.close()

    except Exception as e:
        logging.exception("An unexpected error occurred during the example execution.")

