import logging
from typing import List, Optional, Tuple

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class github_com_homePage:
    """
    Page Object Model for the GitHub homepage (https://github.com).

    This class encapsulates the elements and interactions on the GitHub homepage,
    as derived from the provided selectors used in test cases.
    """

    # --- Locators ---
    # Using tuples of (By strategy, selector string)
    _HERO_SECTION_PRIMARY = (By.CSS_SELECTOR, "section.Primer_Brand__Hero-module__Hero___EM3jf.Primer_Brand__Hero-module__Hero--align-center___HUXm3.lp-IntroHero-hero")
    _HERO_SECTION_FALLBACK = (By.ID, "hero")

    _HERO_EMAIL_INPUT_PRIMARY = (By.ID, "hero_user_email")
    _HERO_EMAIL_INPUT_FALLBACK_1 = (By.CSS_SELECTOR, "css:#hero_user_email") # Redundant but explicitly listed
    _HERO_EMAIL_INPUT_FALLBACK_2 = (By.ID, "id=hero_user_email") # Redundant but explicitly listed

    _HERO_SIGNUP_BUTTON_PRIMARY = (By.CSS_SELECTOR, "#hero_user_email + button")
    _HERO_SIGNUP_BUTTON_FALLBACK_1 = (By.CSS_SELECTOR, "button[data-testid='hero-signup-button']")
    _HERO_SIGNUP_BUTTON_FALLBACK_2 = (By.CSS_SELECTOR, ".hero-signup-button-css")

    _BOTTOM_CTA_EMAIL_INPUT = (By.ID, "#bottom_cta_section_user_email")

    _MAIN_NAV_MENU = (By.CSS_SELECTOR, "nav.HeaderMenu-nav")

    _SIGNUP_SUCCESS_MESSAGE = (By.CSS_SELECTOR, "[data-testid='signup-success-message'], .signup-success-class")

    _GENERIC_PRIMARY_BUTTON = (By.CSS_SELECTOR, "button.btn.btn-mktg.btn-primary.mb-3.js-navigation-target")

    _FORM_INPUT_FIELD = (By.CSS_SELECTOR, "form > section > div > div > span > input")

    # --- Page URL ---
    _BASE_URL = "https://github.com"

    def __init__(self, driver: WebDriver):
        """
        Initializes the HomePage with a WebDriver instance.

        Args:
            driver: The Selenium WebDriver instance.
        """
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10) # Default wait time of 10 seconds
        logger.info("GitHub Home Page Object Initialized")

    # --- Helper Methods for Waits ---

    def _wait_for_element_visible(self, locator: Tuple[str, str], timeout: int = 10) -> Optional[WebDriverWait]:
        """
        Waits for an element to be visible on the page.

        Args:
            locator: A tuple containing the By strategy and selector string.
            timeout: The maximum time to wait in seconds.

        Returns:
            The WebDriverWait object if the element becomes visible, None otherwise.
        """
        try:
            logger.debug(f"Waiting for element visible: {locator}")
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located(locator))
            logger.debug(f"Element visible: {locator}")
            return element
        except (NoSuchElementException, TimeoutException) as e:
            logger.warning(f"Element not visible within timeout: {locator}. Error: {e}")
            return None
        except StaleElementReferenceException as e:
            logger.warning(f"Stale element reference while waiting for visibility: {locator}. Error: {e}")
            return None

    def _wait_for_element_clickable(self, locator: Tuple[str, str], timeout: int = 10) -> Optional[WebDriverWait]:
        """
        Waits for an element to be clickable on the page.

        Args:
            locator: A tuple containing the By strategy and selector string.
            timeout: The maximum time to wait in seconds.

        Returns:
            The WebDriverWait object if the element becomes clickable, None otherwise.
        """
        try:
            logger.debug(f"Waiting for element clickable: {locator}")
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable(locator))
            logger.debug(f"Element clickable: {locator}")
            return element
        except (NoSuchElementException, TimeoutException) as e:
            logger.warning(f"Element not clickable within timeout: {locator}. Error: {e}")
            return None
        except StaleElementReferenceException as e:
            logger.warning(f"Stale element reference while waiting for clickability: {locator}. Error: {e}")
            return None

    def _wait_for_url_contains(self, partial_url: str, timeout: int = 10) -> bool:
        """
        Waits for the current URL to contain a specific substring.

        Args:
            partial_url: The substring expected in the URL.
            timeout: The maximum time to wait in seconds.

        Returns:
            True if the URL contains the substring within the timeout, False otherwise.
        """
        try:
            logger.debug(f"Waiting for URL to contain: '{partial_url}'")
            wait = WebDriverWait(self.driver, timeout)
            result = wait.until(EC.url_contains(partial_url))
            if result:
                logger.debug(f"URL contains '{partial_url}'")
            else:
                logger.warning(f"URL did not contain '{partial_url}' within timeout.")
            return result
        except TimeoutException as e:
            logger.warning(f"URL did not contain '{partial_url}' within timeout. Error: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while checking URL: {e}")
            return False

    def _find_element_with_fallbacks(self, primary_locator: Tuple[str, str], *fallback_locators: Tuple[str, str]):
        """
        Tries to find an element using a primary locator and then a series of fallbacks.

        Args:
            primary_locator: The first locator tuple to try.
            *fallback_locators: Additional locator tuples to try if the primary fails.

        Returns:
            The WebElement if found, otherwise None.
        """
        locators_to_try = [primary_locator] + list(fallback_locators)
        for locator in locators_to_try:
            try:
                # Use wait.until to ensure element is present and potentially visible/clickable
                # based on the calling context. Here, we just ensure presence.
                element = self.wait.until(EC.presence_of_element_located(locator))
                logger.debug(f"Found element using locator: {locator}")
                return element
            except (NoSuchElementException, TimeoutException):
                logger.debug(f"Locator failed: {locator}")
            except StaleElementReferenceException:
                 logger.warning(f"Stale element reference for locator: {locator}. Retrying...")
                 try:
                     element = self.wait.until(EC.presence_of_element_located(locator))
                     logger.debug(f"Found element using locator after retry: {locator}")
                     return element
                 except (NoSuchElementException, TimeoutException):
                     logger.debug(f"Locator failed after retry: {locator}")
        logger.warning(f"Could not find element with any of the locators: {locators_to_try}")
        return None

    # --- Page Actions ---

    def navigate_to(self) -> None:
        """Navigates the browser to the GitHub homepage."""
        try:
            logger.info(f"Navigating to: {self._BASE_URL}")
            self.driver.get(self._BASE_URL)
            # Optionally, wait for a key element to ensure the page has loaded
            self.wait.until(EC.presence_of_element_located(self._HERO_SECTION_PRIMARY))
            logger.info("Successfully navigated to GitHub homepage.")
        except Exception as e:
            logger.error(f"Failed to navigate to {self._BASE_URL}. Error: {e}")
            raise

    def get_current_url(self) -> str:
        """
        Gets the current URL of the browser.

        Returns:
            The current URL as a string.
        """
        current_url = self.driver.current_url
        logger.debug(f"Current URL is: {current_url}")
        return current_url

    def is_url_containing(self, partial_url: str) -> bool:
        """
        Checks if the current browser URL contains the specified substring.

        Args:
            partial_url: The substring to look for in the URL.

        Returns:
            True if the URL contains the substring, False otherwise.
        """
        logger.info(f"Checking if URL contains '{partial_url}'")
        return self._wait_for_url_contains(partial_url)

    def enter_email_in_hero(self, email: str) -> None:
        """
        Enters an email address into the hero section's email input field.

        Args:
            email: The email address to enter.
        """
        logger.info(f"Entering email '{email}' into hero email input.")
        element = self._find_element_with_fallbacks(
            self._HERO_EMAIL_INPUT_PRIMARY,
            self._HERO_EMAIL_INPUT_FALLBACK_1,
            self._HERO_EMAIL_INPUT_FALLBACK_2
        )
        if element:
            try:
                # Clear existing text and send new email
                element.clear()
                element.send_keys(email)
                logger.info(f"Successfully entered email '{email}' in hero input.")
            except Exception as e:
                logger.error(f"Failed to enter email '{email}' into hero input. Error: {e}")
                raise
        else:
            error_msg = "Hero email input element not found."
            logger.error(error_msg)
            raise NoSuchElementException(error_msg)

    def click_hero_signup_button(self) -> None:
        """Clicks the signup button located in the hero section."""
        logger.info("Clicking hero signup button.")
        element = self._find_element_with_fallbacks(
            self._HERO_SIGNUP_BUTTON_PRIMARY,
            self._HERO_SIGNUP_BUTTON_FALLBACK_1,
            self._HERO_SIGNUP_BUTTON_FALLBACK_2
        )
        if element:
            try:
                # Wait for clickability specifically
                clickable_element = self._wait_for_element_clickable(
                    (By.CSS_SELECTOR, "selector_that_matches_found_element"), # Placeholder, needs actual locator of 'element'
                    timeout=5
                )
                if clickable_element:
                    clickable_element.click()
                    logger.info("Successfully clicked hero signup button.")
                else:
                    # If wait_for_element_clickable failed, try clicking directly (less reliable)
                    element.click()
                    logger.warning("Clicked hero signup button directly after clickability wait failed.")
            except Exception as e:
                logger.error(f"Failed to click hero signup button. Error: {e}")
                raise
        else:
            error_msg = "Hero signup button element not found."
            logger.error(error_msg)
            raise NoSuchElementException(error_msg)

    def is_signup_success_message_displayed(self) -> bool:
        """
        Checks if the signup success message is displayed on the page.

        Returns:
            True if the success message is displayed, False otherwise.
        """
        logger.info("Checking for signup success message.")
        element = self._wait_for_element_visible(self._SIGNUP_SUCCESS_MESSAGE)
        if element:
            logger.info("Signup success message found.")
            return True
        else:
            logger.warning("Signup success message not found.")
            return False

    def enter_email_in_bottom_cta(self, email: str) -> None:
        """
        Enters an email address into the bottom call-to-action email input field.

        Args:
            email: The email address to enter.
        """
        logger.info(f"Entering email '{email}' into bottom CTA email input.")
        element = self._wait_for_element_visible(self._BOTTOM_CTA_EMAIL_INPUT)
        if element:
            try:
                element.clear()
                element.send_keys(email)
                logger.info(f"Successfully entered email '{email}' in bottom CTA input.")
            except Exception as e:
                logger.error(f"Failed to enter email '{email}' into bottom CTA input. Error: {e}")
                raise
        else:
            error_msg = "Bottom CTA email input element not found."
            logger.error(error_msg)
            raise NoSuchElementException(error_msg)

    def click_generic_primary_button(self) -> None:
        """Clicks the generic primary button."""
        logger.info("Clicking generic primary button.")
        element = self._wait_for_element_clickable(self._GENERIC_PRIMARY_BUTTON)
        if element:
            try:
                element.click()
                logger.info("Successfully clicked generic primary button.")
            except Exception as e:
                logger.error(f"Failed to click generic primary button. Error: {e}")
                raise
        else:
            error_msg = "Generic primary button element not found."
            logger.error(error_msg)
            raise NoSuchElementException(error_msg)

    def get_hero_section_element(self) -> Optional[WebDriverWait]:
        """
        Returns the hero section element if found.

        Returns:
            The WebElement representing the hero section, or None if not found.
        """
        logger.info("Getting hero section element.")
        return self._find_element_with_fallbacks(self._HERO_SECTION_PRIMARY, self._HERO_SECTION_FALLBACK)

    def get_main_nav_menu_element(self) -> Optional[WebDriverWait]:
        """
        Returns the main navigation menu element if found.

        Returns:
            The WebElement representing the main navigation menu, or None if not found.
        """
        logger.info("Getting main navigation menu element.")
        return self._wait_for_element_visible(self._MAIN_NAV_MENU)

    def get_form_input_field_element(self) -> Optional[WebDriverWait]:
        """
        Returns the specific form input field element if found.

        Returns:
            The WebElement representing the form input field, or None if not found.
        """
        logger.info("Getting form input field element.")
        return self._wait_for_element_visible(self._FORM_INPUT_FIELD)


# Example Usage (requires a WebDriver setup)
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    # Setup WebDriver
    # Ensure you have ChromeDriver installed or use webdriver-manager
    try:
        # Using webdriver-manager to automatically download and manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()

        # Instantiate the page object
        home_page = github_com_homePage(driver)

        # --- Example Test Scenarios ---

        # 1. Navigate to the page
        home_page.navigate_to()
        print(f"Current URL after navigation: {home_page.get_current_url()}")
        assert home_page.is_url_containing("github.com")

        # 2. Interact with the hero section (if elements are present)
        # Note: GitHub's homepage structure might change, and these specific selectors
        # might not always correspond to visible elements or might be complex.
        # This is illustrative based on the provided selectors.

        hero_sec = home_page.get_hero_section_element()
        if hero_sec:
            print("Hero section found.")
            # Example: Try to enter email if the input field is found
            try:
                home_page.enter_email_in_hero("testuser@example.com")
                print("Successfully entered email in hero.")
                # Note: Clicking the button might lead to a different page or action
                # home_page.click_hero_signup_button()
                # print("Clicked hero signup button.")
                # # Check for success message if applicable after click
                # if home_page.is_signup_success_message_displayed():
                #     print("Signup success message displayed.")
            except Exception as e:
                print(f"Could not interact with hero email/button: {e}")
        else:
            print("Hero section not found using provided selectors.")

        # 3. Interact with the bottom CTA (if elements are present)
        # bottom_cta_email = home_page.get_bottom_cta_email_input() # This requires a property/method for the element itself
        # Let's use the action method directly
        try:
            home_page.enter_email_in_bottom_cta("another@example.com")
            print("Successfully entered email in bottom CTA.")
            # home_page.click_generic_primary_button() # Example interaction
            # print("Clicked generic primary button.")
        except Exception as e:
            print(f"Could not interact with bottom CTA email: {e}")


        # 4. Check for navigation menu presence
        nav_menu = home_page.get_main_nav_menu_element()
        if nav_menu:
            print("Main navigation menu found.")
        else:
            print("Main navigation menu not found.")

        # 5. Check for general form input presence
        form_input = home_page.get_form_input_field_element()
        if form_input:
            print("Generic form input field found.")
        else:
            print("Generic form input field not found.")


        print("\n--- Test Scenarios Completed ---")

    except Exception as e:
        print(f"\nAn error occurred during the example execution: {e}")
    finally:
        if 'driver' in locals() and driver:
            driver.quit()
            print("WebDriver closed.")
