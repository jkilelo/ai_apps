# Imports
import logging
from typing import List, Optional, Tuple

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define constants
GITHUB_BASE_URL = "https://github.com/"

class github_com_homePage:
    """
    Page Object Model for the GitHub homepage.

    Handles interactions and element locating for the main GitHub landing page.
    """

    def __init__(self, driver: WebDriver, timeout: int = 10):
        """
        Initializes the GitHub homepage page object.

        Args:
            driver: The Selenium WebDriver instance.
            timeout: The maximum time in seconds to wait for elements.
        """
        self.driver = driver
        self.timeout = timeout
        self.url = GITHUB_BASE_URL
        logger.info(f"Initialized GitHub homepage page object with timeout: {self.timeout}s")

    def _wait_for_element(self, selectors: List[Tuple[By, str]], is_clickable: bool = False) -> Optional[WebElement]:
        """
        Waits for the first available element matching any of the provided selectors.

        Args:
            selectors: A list of (By, selector_string) tuples. The first one found wins.
            is_clickable: If True, waits until the element is clickable.

        Returns:
            The WebElement if found, otherwise None.
        """
        wait = WebDriverWait(self.driver, self.timeout)
        for by_strategy, selector in selectors:
            try:
                if is_clickable:
                    element = wait.until(EC.element_to_be_clickable((by_strategy, selector)))
                else:
                    element = wait.until(EC.visibility_of_element_located((by_strategy, selector)))
                logger.debug(f"Found element using {by_strategy.value}: '{selector}'")
                return element
            except (NoSuchElementException, TimeoutException):
                logger.debug(f"Element not found or not visible/clickable using {by_strategy.value}: '{selector}'")
                continue # Try the next selector
        logger.warning(f"Could not find any element matching selectors: {[(by.value, sel) for by, sel in selectors]}")
        return None

    def navigate_to(self) -> None:
        """
        Navigates the browser to the GitHub homepage URL.
        """
        try:
            self.driver.get(self.url)
            logger.info(f"Navigated to {self.url}")
            # Optional: Wait for a critical element on the page to confirm load
            if not self.hero_section:
                 raise TimeoutException(f"Failed to load homepage, hero section not found.")
        except Exception as e:
            logger.error(f"Failed to navigate to {self.url}: {e}")
            raise

    def verify_url_contains(self, path: str) -> bool:
        """
        Checks if the current URL contains the specified path string.

        Args:
            path: The string to check for in the current URL.

        Returns:
            True if the URL contains the path, False otherwise.
        """
        current_url = self.driver.current_url
        result = path in current_url
        logger.info(f"Checking if current URL '{current_url}' contains '{path}': {result}")
        return result

    @property
    def hero_section(self) -> Optional[WebElement]:
        """
        Gets the main hero section element on the page.

        Uses primary selector #hero with fallback.

        Returns:
            The WebElement for the hero section, or None if not found.
        """
        # Primary: #hero
        # Fallback: section.Primer_Brand__Hero... (highly specific, fragile)
        selectors: List[Tuple[By, str]] = [
            (By.ID, "hero"),
            (By.CSS_SELECTOR, "section.Primer_Brand__Hero-module__Hero___EM3jf.Primer_Brand__Hero-module__Hero--align-center___HUXm3.lp-IntroHero-hero"),
            (By.CSS_SELECTOR, "#hero") # Redundant but matches input
        ]
        element = self._wait_for_element(selectors)
        if element:
            logger.info("Successfully located hero section.")
        return element

    @property
    def hero_email_input(self) -> Optional[WebElement]:
        """
        Gets the email input field within the hero section.

        Uses primary selector #hero_user_email with fallbacks.

        Returns:
            The WebElement for the hero email input, or None if not found.
        """
        # Primary: #hero_user_email
        # Fallbacks: css:#hero_user_email, id=hero_user_email (interpreted as By.ID, 'hero_user_email')
        selectors: List[Tuple[By, str]] = [
            (By.ID, "hero_user_email"),
            (By.CSS_SELECTOR, "#hero_user_email"),
            (By.ID, "hero_user_email") # Redundant but matches input
        ]
        element = self._wait_for_element(selectors)
        if element:
            logger.info("Successfully located hero email input.")
        return element

    @property
    def hero_signup_button(self) -> Optional[WebElement]:
        """
        Gets the signup button associated with the hero section.

        Uses primary selector button[data-testid='hero-signup-button'] with fallbacks.

        Returns:
            The WebElement for the hero signup button, or None if not found.
        """
        # Primary: button[data-testid='hero-signup-button']
        # Fallbacks: #hero_user_email + button, .hero-signup-button-css, button.btn.btn-mktg...
        selectors: List[Tuple[By, str]] = [
            (By.CSS_SELECTOR, "button[data-testid='hero-signup-button']"),
            (By.CSS_SELECTOR, "#hero_user_email + button"), # Adjacent sibling
            (By.CSS_SELECTOR, ".hero-signup-button-css"),
            (By.CSS_SELECTOR, "button.btn.btn-mktg.btn-primary.mb-3.js-navigation-target") # Very specific button class
        ]
        element = self._wait_for_element(selectors, is_clickable=True)
        if element:
            logger.info("Successfully located hero signup button.")
        return element

    @property
    def main_form_input(self) -> Optional[WebElement]:
        """
        Gets a general input field within a form structure on the page.

        Selector: form > section > div > div > span > input

        Returns:
            The WebElement for the input field, or None if not found.
        """
        selectors: List[Tuple[By, str]] = [
            (By.CSS_SELECTOR, "form > section > div > div > span > input")
        ]
        element = self._wait_for_element(selectors)
        if element:
            logger.info("Successfully located main form input.")
        return element

    @property
    def bottom_cta_email_input(self) -> Optional[WebElement]:
        """
        Gets the email input field in the bottom Call To Action (CTA) section.

        Selector: #bottom_cta_section_user_email

        Returns:
            The WebElement for the bottom CTA email input, or None if not found.
        """
        selectors: List[Tuple[By, str]] = [
            (By.ID, "bottom_cta_section_user_email")
        ]
        element = self._wait_for_element(selectors)
        if element:
            logger.info("Successfully located bottom CTA email input.")
        return element

    @property
    def signup_success_message(self) -> Optional[WebElement]:
        """
        Gets the signup success message element.

        Uses primary selector [data-testid='signup-success-message'] with fallback.

        Returns:
            The WebElement for the success message, or None if not found.
        """
        selectors: List[Tuple[By, str]] = [
            (By.CSS_SELECTOR, "[data-testid='signup-success-message']"),
            (By.CSS_SELECTOR, ".signup-success-class") # Fallback class
        ]
        element = self._wait_for_element(selectors)
        if element:
            logger.info("Successfully located signup success message.")
        return element

    @property
    def header_navigation_menu(self) -> Optional[WebElement]:
        """
        Gets the main header navigation menu element.

        Selector: nav.HeaderMenu-nav

        Returns:
            The WebElement for the header navigation menu, or None if not found.
        """
        selectors: List[Tuple[By, str]] = [
            (By.CSS_SELECTOR, "nav.HeaderMenu-nav")
        ]
        element = self._wait_for_element(selectors)
        if element:
            logger.info("Successfully located header navigation menu.")
        return element

    # --- Interaction Methods ---

    def enter_hero_email(self, email: str) -> None:
        """
        Enters an email address into the hero section's email input field.

        Args:
            email: The email address to enter.
        """
        email_input = self.hero_email_input
        if email_input:
            try:
                email_input.clear()
                email_input.send_keys(email)
                logger.info(f"Entered email '{email}' into hero email input.")
            except Exception as e:
                logger.error(f"Failed to enter email '{email}' into hero email input: {e}")
                raise
        else:
            logger.error("Hero email input not found, cannot enter email.")
            raise NoSuchElementException("Hero email input not found.")

    def click_hero_signup_button(self) -> None:
        """
        Clicks the signup button in the hero section.
        """
        signup_button = self.hero_signup_button
        if signup_button:
            try:
                signup_button.click()
                logger.info("Clicked hero signup button.")
            except Exception as e:
                logger.error(f"Failed to click hero signup button: {e}")
                raise
        else:
            logger.error("Hero signup button not found, cannot click.")
            raise NoSuchElementException("Hero signup button not found.")

    # Potential actions for other elements if they were interactive
    # e.g., entering email in bottom CTA, interacting with main form input

# Example Usage (optional, for demonstration)
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager

    driver = None
    try:
        # Setup WebDriver using webdriver-manager
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless") # Uncomment for headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(0) # Disable implicit waits as we use explicit waits

        home_page = github_com_homePage(driver, timeout=15)

        # --- Test Case Simulation ---
        print("\n--- Navigating to GitHub ---")
        home_page.navigate_to()

        # Verify navigation and basic elements presence
        print(f"\nCurrent URL: {driver.current_url}")
        print(f"Is URL on homepage? {home_page.verify_url_contains('/')}")

        print("\n--- Checking Hero Section ---")
        hero = home_page.hero_section
        if hero:
            print("Hero section found.")
            email_input = home_page.hero_email_input
            if email_input:
                print("Hero email input found.")
                # Example interaction:
                # home_page.enter_hero_email("test@example.com")
                # signup_btn = home_page.hero_signup_button
                # if signup_btn:
                #     print("Hero signup button found.")
                #     # signup_btn.click() # Uncomment to actually click
                # else:
                #     print("Hero signup button NOT found.")
            else:
                print("Hero email input NOT found.")

            signup_btn = home_page.hero_signup_button
            if signup_btn:
                 print("Hero signup button found (using fallback or primary).")
            else:
                 print("Hero signup button NOT found.")

        else:
            print("Hero section NOT found.")

        print("\n--- Checking Header Navigation ---")
        nav_menu = home_page.header_navigation_menu
        if nav_menu:
            print("Header navigation menu found.")
        else:
            print("Header navigation menu NOT found.")

        # Example of checking for a non-existent element (for error handling demo)
        # print("\n--- Checking for a non-existent element ---")
        # try:
        #     non_existent_element = home_page._wait_for_element([(By.ID, "non-existent-id")])
        #     if not non_existent_element:
        #         print("Correctly handled non-existent element.")
        # except Exception as e:
        #      print(f"An unexpected error occurred: {e}")

    except Exception as e:
        logger.critical(f"An error occurred during the example execution: {e}")
    finally:
        if driver:
            print("\n--- Closing browser ---")
            driver.quit()
            print("Browser closed.")

