import logging
from typing import List, Optional, Union

from playwright.sync_api import Page, TimeoutError, ElementHandle, PlaywrightException

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class BasePage:
    """
    Base class for all Page Objects in the Page Object Model.

    This class provides common functionalities that are used across multiple
    pages, such as navigation, waiting for elements, interacting with elements,
    and taking screenshots. It leverages Playwright's Page object.
    """

    def __init__(self, page: Page):
        """
        Initializes the BasePage with a Playwright Page object.

        Args:
            page: The Playwright Page object to interact with.
        """
        if not isinstance(page, Page):
            raise TypeError("The 'page' argument must be a Playwright Page object.")
        self.page: Page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initialized {self.__class__.__name__}")

    def navigate_to(self, url: str) -> None:
        """
        Navigates the browser to the specified URL.

        Args:
            url: The URL to navigate to.

        Raises:
            ValueError: If the URL is empty or not a string.
            PlaywrightException: If Playwright encounters an error during navigation.
        """
        if not isinstance(url, str) or not url:
            self.logger.error("URL cannot be empty.")
            raise ValueError("URL cannot be empty.")

        try:
            self.logger.info(f"Navigating to: {url}")
            self.page.goto(url)
            self.logger.info(f"Successfully navigated to: {url}")
        except PlaywrightException as e:
            self.logger.error(f"Error navigating to {url}: {e}")
            raise e

    def wait_for_element(self, selector: str, timeout: int = 30000) -> ElementHandle:
        """
        Waits for an element specified by the selector to be present on the page.

        Args:
            selector: The CSS selector for the element.
            timeout: The maximum time in milliseconds to wait for the element.

        Returns:
            The ElementHandle of the found element.

        Raises:
            TimeoutError: If the element is not found within the specified timeout.
            ValueError: If the selector is empty or not a string.
            PlaywrightException: If Playwright encounters an error.
        """
        if not isinstance(selector, str) or not selector:
            self.logger.error("Selector cannot be empty.")
            raise ValueError("Selector cannot be empty.")
        if not isinstance(timeout, int) or timeout <= 0:
            self.logger.warning(f"Invalid timeout value: {timeout}. Using default.")
            timeout = 30000

        try:
            self.logger.debug(f"Waiting for element: {selector} with timeout {timeout}ms")
            element = self.page.locator(selector).wait_for(timeout=timeout)
            self.logger.debug(f"Element found: {selector}")
            return element
        except TimeoutError as e:
            self.logger.error(f"Timeout waiting for element: {selector} ({timeout}ms). Error: {e}")
            raise e
        except PlaywrightException as e:
            self.logger.error(f"Playwright error waiting for element {selector}: {e}")
            raise e

    def click_with_retry(self, selector: str, retries: int = 3, timeout: int = 30000) -> bool:
        """
        Clicks an element with a specified number of retries if it's not immediately clickable.

        Args:
            selector: The CSS selector for the element to click.
            retries: The number of times to retry clicking.
            timeout: The maximum time in milliseconds to wait for the element before each click attempt.

        Returns:
            True if the click was successful, False otherwise.

        Raises:
            ValueError: If selector is empty or retries/timeout are invalid.
            PlaywrightException: If Playwright encounters an error.
        """
        if not isinstance(selector, str) or not selector:
            self.logger.error("Selector cannot be empty for click_with_retry.")
            raise ValueError("Selector cannot be empty.")
        if not isinstance(retries, int) or retries < 0:
            self.logger.warning(f"Invalid retries value: {retries}. Using 0 retries.")
            retries = 0
        if not isinstance(timeout, int) or timeout <= 0:
            self.logger.warning(f"Invalid timeout value for click_with_retry: {timeout}. Using default.")
            timeout = 30000

        for attempt in range(retries + 1):
            try:
                element = self.wait_for_element(selector, timeout)
                element.click()
                self.logger.info(f"Successfully clicked element '{selector}' on attempt {attempt + 1}.")
                return True
            except TimeoutError:
                self.logger.warning(f"Timeout waiting for element '{selector}' on attempt {attempt + 1}. Retrying...")
            except PlaywrightException as e:
                self.logger.error(f"Playwright error clicking element '{selector}' on attempt {attempt + 1}: {e}")
                if attempt == retries:
                    return False
            except Exception as e:
                self.logger.error(f"An unexpected error occurred clicking element '{selector}' on attempt {attempt + 1}: {e}")
                if attempt == retries:
                    return False

        self.logger.error(f"Failed to click element '{selector}' after {retries + 1} attempts.")
        return False

    def fill_field(self, selector: str, value: str) -> None:
        """
        Fills a form field with the given value.

        Args:
            selector: The CSS selector for the input field.
            value: The string value to enter into the field.

        Raises:
            ValueError: If selector or value are invalid.
            PlaywrightException: If Playwright encounters an error.
        """
        if not isinstance(selector, str) or not selector:
            self.logger.error("Selector cannot be empty for fill_field.")
            raise ValueError("Selector cannot be empty.")
        if not isinstance(value, str):
            self.logger.error(f"Value for field '{selector}' must be a string, got {type(value)}.")
            raise ValueError("Value must be a string.")

        try:
            self.logger.debug(f"Filling field '{selector}' with value: '{value}'")
            element = self.wait_for_element(selector)
            element.fill(value)
            self.logger.info(f"Successfully filled field '{selector}'.")
        except TimeoutError:
            self.logger.error(f"Timeout waiting for element '{selector}' to fill.")
            raise
        except PlaywrightException as e:
            self.logger.error(f"Playwright error filling field '{selector}': {e}")
            raise

    def get_text(self, selector: str) -> Optional[str]:
        """
        Gets the text content of an element.

        Args:
            selector: The CSS selector for the element.

        Returns:
            The text content of the element, or None if the element is not found or an error occurs.

        Raises:
            ValueError: If selector is empty.
            PlaywrightException: If Playwright encounters an error.
        """
        if not isinstance(selector, str) or not selector:
            self.logger.error("Selector cannot be empty for get_text.")
            raise ValueError("Selector cannot be empty.")

        try:
            element = self.wait_for_element(selector)
            text_content = element.text_content()
            self.logger.debug(f"Retrieved text '{text_content}' from element '{selector}'.")
            return text_content
        except TimeoutError:
            self.logger.warning(f"Timeout waiting for element '{selector}' to get text.")
            return None
        except PlaywrightException as e:
            self.logger.error(f"Playwright error getting text from element '{selector}': {e}")
            return None

    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Checks if an element is visible on the page.

        Args:
            selector: The CSS selector for the element.
            timeout: The maximum time in milliseconds to wait for the element to become visible.

        Returns:
            True if the element is visible, False otherwise.

        Raises:
            ValueError: If selector is empty.
            PlaywrightException: If Playwright encounters an error.
        """
        if not isinstance(selector, str) or not selector:
            self.logger.error("Selector cannot be empty for is_element_visible.")
            raise ValueError("Selector cannot be empty.")
        if not isinstance(timeout, int) or timeout <= 0:
            self.logger.warning(f"Invalid timeout value for is_element_visible: {timeout}. Using default.")
            timeout = 5000

        try:
            self.logger.debug(f"Checking visibility of element: {selector} with timeout {timeout}ms")
            is_visible = self.page.locator(selector).is_visible(timeout=timeout)
            self.logger.debug(f"Element '{selector}' is visible: {is_visible}")
            return is_visible
        except TimeoutError:
            self.logger.debug(f"Element '{selector}' did not become visible within {timeout}ms.")
            return False
        except PlaywrightException as e:
            self.logger.error(f"Playwright error checking visibility of element '{selector}': {e}")
            return False

    def take_screenshot(self, name: str, path: Optional[str] = None) -> None:
        """
        Takes a screenshot of the current page.

        Args:
            name: The name for the screenshot file (e.g., "homepage_after_login").
            path: The directory path where the screenshot should be saved.
                  If None, it will be saved in the current working directory.

        Raises:
            ValueError: If the name is empty or not a string.
            PlaywrightException: If Playwright encounters an error during screenshot capture.
        """
        if not isinstance(name, str) or not name:
            self.logger.error("Screenshot name cannot be empty.")
            raise ValueError("Screenshot name cannot be empty.")
        if path is not None and (not isinstance(path, str) or not path):
            self.logger.error("Screenshot path must be a valid string if provided.")
            raise ValueError("Screenshot path must be a valid string if provided.")

        try:
            file_name = f"{name}.png"
            screenshot_options = {"path": path, "full_page": True} if path else {"full_page": True}
            self.logger.info(f"Taking screenshot: {file_name}" + (f" in path: {path}" if path else ""))
            self.page.screenshot(path=path, full_page=True)
            self.logger.info(f"Screenshot saved as: {file_name}" + (f" in {path}" if path else ""))
        except PlaywrightException as e:
            self.logger.error(f"Playwright error taking screenshot '{name}': {e}")
            raise

    def wait_for_load_state(self, state: str = 'load', timeout: int = 30000) -> None:
        """
        Waits for the page to reach a specific load state.

        Common states: 'load', 'domcontentloaded', 'networkidle'.

        Args:
            state: The load state to wait for. Defaults to 'load'.
            timeout: The maximum time in milliseconds to wait.

        Raises:
            ValueError: If the state is invalid or timeout is invalid.
            PlaywrightException: If Playwright encounters an error.
        """
        valid_states = ['load', 'domcontentloaded', 'networkidle']
        if not isinstance(state, str) or state not in valid_states:
            self.logger.error(f"Invalid load state '{state}'. Must be one of {valid_states}.")
            raise ValueError(f"Invalid load state. Must be one of {valid_states}.")
        if not isinstance(timeout, int) or timeout <= 0:
            self.logger.warning(f"Invalid timeout value for wait_for_load_state: {timeout}. Using default.")
            timeout = 30000

        try:
            self.logger.info(f"Waiting for page load state: '{state}' with timeout {timeout}ms")
            self.page.wait_for_load_state(state, timeout=timeout)
            self.logger.info(f"Page reached load state: '{state}'.")
        except TimeoutError as e:
            self.logger.error(f"Timeout waiting for page load state '{state}': {e}")
            raise e
        except PlaywrightException as e:
            self.logger.error(f"Playwright error waiting for load state '{state}': {e}")
            raise e

    def handle_dialog(self, accept: bool, text: Optional[str] = None, timeout: int = 5000) -> bool:
        """
        Handles a JavaScript dialog (alert, confirm, prompt).

        Args:
            accept: True to accept the dialog, False to dismiss it.
            text: The text to enter if it's a prompt dialog. Ignored for alert/confirm.
            timeout: The maximum time in milliseconds to wait for the dialog.

        Returns:
            True if the dialog was handled successfully, False otherwise.

        Raises:
            ValueError: If timeout is invalid.
            PlaywrightException: If Playwright encounters an error.
        """
        if not isinstance(accept, bool):
            self.logger.error("The 'accept' argument must be a boolean.")
            raise ValueError("The 'accept' argument must be a boolean.")
        if text is not None and not isinstance(text, str):
            self.logger.error("The 'text' argument must be a string or None.")
            raise ValueError("The 'text' argument must be a string or None.")
        if not isinstance(timeout, int) or timeout <= 0:
            self.logger.warning(f"Invalid timeout value for handle_dialog: {timeout}. Using default.")
            timeout = 5000

        try:
            self.logger.info(f"Handling dialog: {'Accept' if accept else 'Dismiss'} with text '{text if text else ''}'")
            dialog = self.page.wait_for_event("dialog", timeout=timeout)
            if dialog:
                if accept:
                    dialog.accept(text)
                    self.logger.info("Dialog accepted.")
                else:
                    dialog.dismiss()
                    self.logger.info("Dialog dismissed.")
                return True
            else:
                self.logger.warning("No dialog was triggered within the timeout.")
                return False
        except TimeoutError:
            self.logger.warning(f"No dialog appeared within {timeout}ms.")
            return False
        except PlaywrightException as e:
            self.logger.error(f"Playwright error handling dialog: {e}")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred handling dialog: {e}")
            return False

    def safe_click(self, selector: str, timeout: int = 30000) -> bool:
        """
        Safely clicks an element, returning True on success and False on failure.

        This method waits for the element to be available and attempts to click it.
        It handles TimeoutError gracefully.

        Args:
            selector: The CSS selector for the element to click.
            timeout: The maximum time in milliseconds to wait for the element.

        Returns:
            True if the element was successfully clicked, False otherwise.

        Raises:
            ValueError: If selector is empty.
            PlaywrightException: If Playwright encounters an error other than TimeoutError.
        """
        if not isinstance(selector, str) or not selector:
            self.logger.error("Selector cannot be empty for safe_click.")
            raise ValueError("Selector cannot be empty.")
        if not isinstance(timeout, int) or timeout <= 0:
            self.logger.warning(f"Invalid timeout value for safe_click: {timeout}. Using default.")
            timeout = 30000

        try:
            self.logger.debug(f"Attempting safe click on element: {selector} with timeout {timeout}ms")
            element = self.wait_for_element(selector, timeout)
            element.click()
            self.logger.info(f"Successfully clicked element: {selector}")
            return True
        except TimeoutError:
            self.logger.warning(f"Timeout occurred while trying to click element: {selector}")
            return False
        except PlaywrightException as e:
            self.logger.error(f"Playwright error during safe click on '{selector}': {e}")
            raise e # Re-raise to indicate a non-timeout Playwright issue

    def wait_and_type(self, selector: str, text: str, timeout: int = 30000) -> bool:
        """
        Waits for an element and types text into it.

        Args:
            selector: The CSS selector of the input field.
            text: The text to type into the field.
            timeout: The maximum time in milliseconds to wait for the element.

        Returns:
            True if typing was successful, False otherwise.

        Raises:
            ValueError: If selector or text are invalid.
            PlaywrightException: If Playwright encounters an error.
        """
        if not isinstance(selector, str) or not selector:
            self.logger.error("Selector cannot be empty for wait_and_type.")
            raise ValueError("Selector cannot be empty.")
        if not isinstance(text, str):
            self.logger.error(f"Text for field '{selector}' must be a string, got {type(text)}.")
            raise ValueError("Text must be a string.")
        if not isinstance(timeout, int) or timeout <= 0:
            self.logger.warning(f"Invalid timeout value for wait_and_type: {timeout}. Using default.")
            timeout = 30000

        try:
            self.logger.debug(f"Waiting for element and typing text into '{selector}'")
            element = self.wait_for_element(selector, timeout)
            element.type(text)
            self.logger.info(f"Successfully typed '{text}' into element: {selector}")
            return True
        except TimeoutError:
            self.logger.warning(f"Timeout waiting for element '{selector}' to type.")
            return False
        except PlaywrightException as e:
            self.logger.error(f"Playwright error typing into element '{selector}': {e}")
            raise e # Re-raise to indicate a Playwright issue

    def get_element_with_fallback(self, selectors_list: List[str]) -> Optional[ElementHandle]:
        """
        Attempts to find an element using a list of selectors and returns the first one found.

        This is useful when an element might have multiple possible selectors.

        Args:
            selectors_list: A list of CSS selectors to try in order.

        Returns:
            The ElementHandle of the first found element, or None if none of the selectors match.

        Raises:
            ValueError: If the selectors_list is empty or contains invalid selectors.
        """
        if not isinstance(selectors_list, list) or not selectors_list:
            self.logger.error("selectors_list cannot be empty.")
            raise ValueError("selectors_list cannot be empty.")

        for selector in selectors_list:
            if not isinstance(selector, str) or not selector:
                self.logger.warning(f"Skipping invalid selector in list: {selector}")
                continue
            try:
                self.logger.debug(f"Attempting to find element with selector: {selector}")
                # Use a shorter timeout here to quickly try the next selector
                element = self.wait_for_element(selector, timeout=5000)
                if element:
                    self.logger.info(f"Found element using fallback selector: {selector}")
                    return element
            except TimeoutError:
                self.logger.debug(f"Element not found with selector: {selector}. Trying next...")
            except PlaywrightException as e:
                self.logger.error(f"Playwright error with fallback selector '{selector}': {e}. Trying next...")
            except Exception as e:
                self.logger.error(f"Unexpected error with fallback selector '{selector}': {e}. Trying next...")

        self.logger.warning("Could not find element using any of the provided fallback selectors.")
        return None


if __name__ == '__main__':
    # Example Usage (requires pytest-playwright or manual Playwright setup)
    # To run this example:
    # 1. Install playwright: pip install playwright
    # 2. Install pytest: pip install pytest
    # 3. Install pytest-playwright: pip install pytest-playwright
    # 4. Run pytest in your terminal: pytest your_file_name.py
    #
    # Alternatively, you can run this block directly if you have playwright installed
    # and want to see a basic run without pytest.

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            # Create a new browser context
            context = browser.new_context()
            # Create a new page
            page = context.new_page()

            class SamplePage(BasePage):
                """A sample page class inheriting from BasePage for demonstration."""
                __slots__ = ("url",) # Optimize memory usage

                def __init__(self, page: Page):
                    super().__init__(page)
                    self.url = "https://playwright.dev/"
                    self.locators = {
                        "getting_started_link": "a[href='/docs/intro']",
                        "title_text": "h1",
                        "search_input": "#search-input",
                        "search_button": ".DocSearch-Button"
                    }

                def navigate_and_get_title(self) -> Optional[str]:
                    """Navigates to the sample page and returns its title."""
                    self.navigate_to(self.url)
                    self.wait_for_load_state()
                    return self.get_text(self.locators["title_text"])

                def search_for(self, query: str) -> bool:
                    """Performs a search on the sample page."""
                    if self.safe_click(self.locators["getting_started_link"]):
                        if self.wait_and_type(self.locators["search_input"], query):
                            # The search button might not be a direct click, but trigger on enter
                            # For demonstration, let's assume it's a visible button
                            # self.safe_click(self.locators["search_button"])
                            # A more realistic scenario would be to press Enter
                            self.page.press(self.locators["search_input"], "Enter")
                            self.logger.info(f"Searched for: {query}")
                            return True
                    return False

            print("\n--- Running BasePage Example ---")
            sample_page = SamplePage(page)

            # Test navigate_to and get_text
            title = sample_page.navigate_and_get_title()
            if title:
                print(f"Page Title: {title}")
                sample_page.take_screenshot("playwright_homepage")
            else:
                print("Failed to retrieve page title.")

            # Test wait_and_type and search
            if sample_page.search_for("installation"):
                print("Search performed successfully.")
                sample_page.wait_for_load_state() # Wait for search results
                sample_page.take_screenshot("playwright_search_results")
            else:
                print("Failed to perform search.")

            # Test is_element_visible
            if sample_page.is_element_visible(sample_page.locators["getting_started_link"]):
                print("Getting started link is visible.")
            else:
                print("Getting started link is not visible.")

            # Test click_with_retry
            if sample_page.click_with_retry(sample_page.locators["getting_started_link"], retries=2):
                print("Getting started link clicked with retry.")
            else:
                print("Failed to click getting started link even with retries.")

            # Test get_element_with_fallback
            fallback_selectors = ["invalid-selector", sample_page.locators["title_text"]]
            found_element = sample_page.get_element_with_fallback(fallback_selectors)
            if found_element:
                print(f"Element found using fallback selector. Text: {found_element.text_content()}")
            else:
                print("Element not found with fallback selectors.")


            # Test handle_dialog (requires a page that triggers a dialog)
            # For example, navigate to a page with an alert
            # page.goto("data:text/html,<script>alert('Hello');</script>")
            # print("\nTesting dialog handling (if page triggers alert)...")
            # if sample_page.handle_dialog(accept=True, timeout=5000):
            #     print("Alert dialog handled.")
            # else:
            #     print("No alert dialog detected or handled.")


            browser.close()
            print("--- BasePage Example Finished ---")

    except ImportError:
        print("\nPlaywright is not installed. Please install it: pip install playwright")
        print("To run this example, also install pytest: pip install pytest pytest-playwright")
        print("Then run: pytest your_file_name.py")
    except Exception as e:
        logging.exception(f"An error occurred during the example execution: {e}")

