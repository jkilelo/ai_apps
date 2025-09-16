# Imports
import logging
from typing import List, Optional, Tuple

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Base URL
GITHUB_URL = "https://github.com"

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class github_com_homePage:
    """
    Page Object Model for the GitHub Homepage (https://github.com).

    This class encapsulates the elements and interactions found on the GitHub
    homepage, providing a clean interface for test automation.
    """

    def __init__(self, driver: WebDriver):
        """
        Initializes the github_com_homePage.

        Args:
            driver: The Selenium WebDriver instance.
        """
        self.driver = driver
        self.base_url = GITHUB_URL
        self.timeout = 10  # Default timeout for waits

        # --- Element Locators ---
        # Using tuples for (selector_type, selector_value) for clarity and reusability.
        # The types are inferred from the provided selectors.

        # Input field for email (primary and fallback)
        self._hero_user_email_locator: Tuple[str, str] = ("css selector", "#hero_user_email")
        self._bottom_cta_user_email_locator: Tuple[str, str] = ("css selector", "#bottom_cta_section_user_email")

        # Signup Button (multiple selectors for resilience)
        self._signup_button_locator: Tuple[str, str] = (
            "css selector",
            "#hero_user_email + button, button[data-testid='hero-signup-button'], .hero-signup-button-css"
        )
        self._mktg_primary_button_locator: Tuple[str, str] = (
            "css selector",
            "button.btn.btn-mktg.btn-primary.mb-3.js-navigation-target"
        )

        # Success Message
        self._signup_success_message_locator: Tuple[str, str] = (
            "css selector",
            "[data-testid='signup-success-message'], .signup-success-class"
        )

        # Navigation Menu
        self._header_menu_nav_locator: Tuple[str, str] = ("css selector", "nav.HeaderMenu-nav")

        # Hero Section
        self._hero_section_locator: Tuple[str, str] = ("css selector", "#hero")
        self._primer_hero_locator: Tuple[str, str] = (
            "css selector",
            "section.Primer_Brand__Hero-module__Hero___EM3jf.Primer_Brand__Hero-module__Hero--align-center___HUXm3.lp-IntroHero-hero"
        )

        # Another input field within a form
        self._form_input_locator: Tuple[str, str] = ("css selector", "form > section > div > div > span > input")

    # --- Navigation Methods ---

    def navigate_to_url(self, url: str) -> None:
        """
        Navigates the browser to the specified URL.

        Args:
            url: The URL to navigate to.
        """
        logger.info(f"Navigating to URL: {url}")
        try:
            self.driver.get(url)
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise

    def go_to_github_home(self) -> None:
        """
        Navigates the browser to the GitHub homepage.
        """
        self.navigate_to_url(self.base_url)

    def go_to_join_page(self) -> None:
        """
        Navigates to the GitHub join page.
        This method is based on the 'url_contains('/join')' selector.
        """
        join_url = f"{self.base_url}/join"
        logger.info(f"Navigating to GitHub join page: {join_url}")
        try:
            # The prompt indicated 'url_contains('/join')' which implies a navigation
            # action. We construct the join URL directly.
            self.driver.get(join_url)
            # Optional: Add a wait to ensure the page has loaded.
            WebDriverWait(self.driver, self.timeout).until(
                EC.url_contains("/join")
            )
        except TimeoutException:
            logger.error(f"Timeout waiting for URL to contain '/join' after navigation.")
            raise
        except Exception as e:
            logger.error(f"Failed to navigate to join page: {e}")
            raise

    # --- Helper Methods for Element Interaction ---

    def _wait_for_element(self, locator: Tuple[str, str]) -> WebElement:
        """
        Waits for an element to be visible and returns it.

        Args:
            locator: A tuple containing the locator strategy and value
                     (e.g., ("css selector", "#element_id")).

        Returns:
            The WebElement if found.

        Raises:
            TimeoutException: If the element is not found within the timeout.
            ValueError: If the locator format is invalid.
        """
        strategy, value = locator
        logger.debug(f"Waiting for element with strategy '{strategy}' and value '{value}'")
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            if strategy.lower() == "css selector":
                element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, value)))
            elif strategy.lower() == "xpath":
                element = wait.until(EC.visibility_of_element_located((By.XPATH, value)))
            elif strategy.lower() == "id":
                element = wait.until(EC.visibility_of_element_located((By.ID, value)))
            elif strategy.lower() == "link text":
                element = wait.until(EC.visibility_of_element_located((By.LINK_TEXT, value)))
            elif strategy.lower() == "partial link text":
                element = wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, value)))
            elif strategy.lower() == "tag name":
                element = wait.until(EC.visibility_of_element_located((By.TAG_NAME, value)))
            elif strategy.lower() == "class name":
                element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, value)))
            else:
                raise ValueError(f"Unsupported locator strategy: {strategy}")
            logger.debug(f"Element found: {value}")
            return element
        except TimeoutException:
            logger.error(f"Timeout waiting for element with selector: {value}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while waiting for element {value}: {e}")
            raise

    def _wait_for_elements(self, locator: Tuple[str, str]) -> List[WebElement]:
        """
        Waits for multiple elements to be visible and returns them.

        Args:
            locator: A tuple containing the locator strategy and value
                     (e.g., ("css selector", "#element_id")).

        Returns:
            A list of WebElements if found.

        Raises:
            TimeoutException: If elements are not found within the timeout.
            ValueError: If the locator format is invalid.
        """
        strategy, value = locator
        logger.debug(f"Waiting for elements with strategy '{strategy}' and value '{value}'")
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            if strategy.lower() == "css selector":
                elements = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, value)))
            elif strategy.lower() == "xpath":
                elements = wait.until(EC.visibility_of_all_elements_located((By.XPATH, value)))
            elif strategy.lower() == "id":
                elements = wait.until(EC.visibility_of_all_elements_located((By.ID, value)))
            elif strategy.lower() == "tag name":
                elements = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, value)))
            elif strategy.lower() == "class name":
                elements = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, value)))
            else:
                raise ValueError(f"Unsupported locator strategy for multiple elements: {strategy}")

            if not elements: # Check if the list is empty after wait
                 raise TimeoutException(f"No elements found for selector: {value}")

            logger.debug(f"Found {len(elements)} elements for selector: {value}")
            return elements
        except TimeoutException:
            logger.error(f"Timeout waiting for elements with selector: {value}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while waiting for elements {value}: {e}")
            raise

    def _click_element(self, locator: Tuple[str, str]) -> None:
        """
        Waits for an element and clicks it.

        Args:
            locator: A tuple containing the locator strategy and value.
        """
        try:
            element = self._wait_for_element(locator)
            logger.info(f"Clicking element with selector: {locator[1]}")
            element.click()
        except (TimeoutException, ValueError) as e:
            logger.error(f"Could not click element {locator[1]}: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during click for {locator[1]}: {e}")
            raise

    def _send_keys_to_element(self, locator: Tuple[str, str], text: str) -> None:
        """
        Waits for an element, clears it, and sends keys.

        Args:
            locator: A tuple containing the locator strategy and value.
            text: The text to send to the element.
        """
        try:
            element = self._wait_for_element(locator)
            logger.info(f"Sending keys '{text}' to element with selector: {locator[1]}")
            element.clear()
            element.send_keys(text)
        except (TimeoutException, ValueError) as e:
            logger.error(f"Could not send keys to element {locator[1]}: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending keys to {locator[1]}: {e}")
            raise

    def _get_element_text(self, locator: Tuple[str, str]) -> str:
        """
        Waits for an element and returns its text.

        Args:
            locator: A tuple containing the locator strategy and value.

        Returns:
            The text content of the element.

        Raises:
            ValueError: If the element is not found or has no text.
        """
        try:
            element = self._wait_for_element(locator)
            text = element.text
            logger.info(f"Retrieved text '{text}' from element with selector: {locator[1]}")
            return text
        except (TimeoutException, ValueError) as e:
            logger.error(f"Could not get text from element {locator[1]}: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while getting text from {locator[1]}: {e}")
            raise

    # --- Specific Page Element Properties/Methods ---

    @property
    def hero_user_email_input(self) -> WebElement:
        """
        Gets the hero user email input field element.
        Uses ID #hero_user_email or CSS #hero_user_email.
        """
        try:
            return self._wait_for_element(self._hero_user_email_locator)
        except (TimeoutException, ValueError) as e:
            logger.error(f"Hero user email input not found: {e}")
            raise

    def enter_hero_user_email(self, email: str) -> None:
        """
        Enters an email address into the hero user email input field.
        """
        self._send_keys_to_element(self._hero_user_email_locator, email)

    @property
    def bottom_cta_user_email_input(self) -> WebElement:
        """
        Gets the bottom CTA user email input field element.
        Uses CSS #bottom_cta_section_user_email.
        """
        try:
            return self._wait_for_element(self._bottom_cta_user_email_locator)
        except (TimeoutException, ValueError) as e:
            logger.error(f"Bottom CTA user email input not found: {e}")
            raise

    def enter_bottom_cta_user_email(self, email: str) -> None:
        """
        Enters an email address into the bottom CTA user email input field.
        """
        self._send_keys_to_element(self._bottom_cta_user_email_locator, email)

    def click_signup_button(self) -> None:
        """
        Clicks the main signup button.
        Uses compound selector for resilience:
        #hero_user_email + button, button[data-testid='hero-signup-button'], .hero-signup-button-css
        """
        self._click_element(self._signup_button_locator)

    @property
    def signup_success_message(self) -> str:
        """
        Gets the text of the signup success message.
        Uses selectors: [data-testid='signup-success-message'], .signup-success-class
        """
        try:
            return self._get_element_text(self._signup_success_message_locator)
        except (TimeoutException, ValueError) as e:
            logger.error(f"Signup success message not found or has no text: {e}")
            raise

    @property
    def header_menu_nav(self) -> WebElement:
        """
        Gets the main navigation menu element.
        Uses CSS selector: nav.HeaderMenu-nav
        """
        try:
            return self._wait_for_element(self._header_menu_nav_locator)
        except (TimeoutException, ValueError) as e:
            logger.error(f"Header menu navigation not found: {e}")
            raise

    @property
    def hero_section(self) -> WebElement:
        """
        Gets the main hero section element.
        Uses CSS selector: #hero
        """
        try:
            return self._wait_for_element(self._hero_section_locator)
        except (TimeoutException, ValueError) as e:
            logger.error(f"Hero section not found: {e}")
            raise

    @property
    def primer_hero_section(self) -> WebElement:
        """
        Gets the Primer Brand Hero section element.
        Uses complex CSS selector for specific hero variant.
        """
        try:
            return self._wait_for_element(self._primer_hero_locator)
        except (TimeoutException, ValueError) as e:
            logger.error(f"Primer hero section not found: {e}")
            raise

    @property
    def form_input_field(self) -> WebElement:
        """
        Gets a generic input field within a form.
        Uses CSS selector: form > section > div > div > span > input
        """
        try:
            return self._wait_for_element(self._form_input_locator)
        except (TimeoutException, ValueError) as e:
            logger.error(f"Generic form input field not found: {e}")
            raise

    def click_mktg_primary_button(self) -> None:
        """
        Clicks a primary marketing button.
        Uses CSS selector: button.btn.btn-mktg.btn-primary.mb-3.js-navigation-target
        """
        self._click_element(self._mktg_primary_button_locator)


# --- Example Usage (for demonstration, not part of the POM class itself) ---
# This section shows how to use the class. It requires a WebDriver setup.

if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By # Import By

    # Setup WebDriver
    # Ensure you have chromedriver installed or use webdriver_manager
    try:
        logger.info("Setting up WebDriver...")
        # Use webdriver_manager to automatically download and manage ChromeDriver
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        logger.info("WebDriver setup complete.")

        # Instantiate the page object
        home_page = github_com_homePage(driver)

        # --- Test Scenarios ---

        # 1. Navigate to GitHub homepage
        logger.info("--- Test Scenario 1: Navigate to GitHub Home ---")
        home_page.go_to_github_home()
        logger.info(f"Current URL: {driver.current_url}")
        assert GITHUB_URL in driver.current_url

        # 2. Attempt to interact with an element (e.g., email input)
        # Note: The prompt stated "Total Elements Available: 0". If the page
        # dynamically loads content or if the selectors are incorrect, this
        # might fail. We'll proceed assuming the selectors are intended to work.
        logger.info("--- Test Scenario 2: Interact with Email Input ---")
        try:
            # Try entering email into the hero input field
            home_page.enter_hero_user_email("testuser@example.com")
            logger.info("Successfully entered email into hero_user_email input.")
            # You could assert the value if the input is visible and editable
            # assert home_page.hero_user_email_input.get_attribute("value") == "testuser@example.com"
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Could not interact with hero_user_email input. This might be expected if the element isn't present on the specific page load or the prompt's element count was accurate. Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during email input interaction: {e}")


        # 3. Navigate to the join page
        logger.info("--- Test Scenario 3: Navigate to Join Page ---")
        home_page.go_to_join_page()
        logger.info(f"Current URL after going to join page: {driver.current_url}")
        assert "/join" in driver.current_url
        assert "join" in driver.title.lower()


        # Example of getting text from a success message (if it were visible)
        # This would likely only work after a successful signup action,
        # which isn't implemented here.
        # try:
        #     success_msg = home_page.signup_success_message
        #     logger.info(f"Signup success message: {success_msg}")
        # except (TimeoutException, NoSuchElementException) as e:
        #     logger.warning(f"Signup success message not found: {e}")


        # Example of getting navigation elements
        try:
            nav_element = home_page.header_menu_nav
            logger.info(f"Found header menu navigation element: {nav_element.tag_name}")
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Header menu navigation element not found: {e}")


        logger.info("Example usage finished.")

    except Exception as e:
        logger.critical(f"An error occurred during WebDriver setup or execution: {e}")
    finally:
        if 'driver' in locals() and driver:
            logger.info("Closing WebDriver.")
            driver.quit()
            logger.info("WebDriver closed.")

