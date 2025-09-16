# Imports
import logging
from typing import List, Optional, Union
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class github_com_homePage:
    """
    Page Object Model for the GitHub Homepage.

    This class encapsulates the elements and interactions on the GitHub homepage
    (https://github.com). It's designed to be used with Selenium WebDriver.
    """

    URL = "https://github.com"

    def __init__(self, driver: WebDriver, timeout: int = 10):
        """
        Initializes the GitHub Homepage Page Object.

        Args:
            driver: The Selenium WebDriver instance.
            timeout: The maximum time in seconds to wait for elements.
        """
        if not isinstance(driver, WebDriver):
            raise TypeError("driver must be an instance of WebDriver")
        self.driver = driver
        self.timeout = timeout
        logger.info(f"Initialized github_com_homePage for URL: {self.URL}")

    # --- Navigation ---

    def navigate_to(self) -> None:
        """
        Navigates the browser to the GitHub homepage URL.
        """
        try:
            logger.info(f"Navigating to {self.URL}")
            self.driver.get(self.URL)
        except Exception as e:
            logger.error(f"Failed to navigate to {self.URL}: {e}")
            raise

    # --- Element Selectors and Methods ---

    # Primary Email Input (Hero Section)
    def _get_hero_email_input(self) -> WebElement:
        """
        Finds the hero user email input element.

        Uses primary ID selector, with CSS and generic form input as fallbacks.
        """
        primary_selector = (By.ID, "hero_user_email")
        fallback_selectors = [
            (By.CSS_SELECTOR, "css:#hero_user_email"), # Redundant but listed
            (By.ID, "hero_user_email"),               # Redundant but listed
            (By.CSS_SELECTOR, "form > section > div > div > span > input") # Generic fallback
        ]
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(primary_selector)
            )
        except TimeoutException:
            logger.warning(f"Primary selector for hero_user_email not found. Trying fallbacks.")
            for selector_type, selector_value in fallback_selectors:
                try:
                    return WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                except TimeoutException:
                    continue # Try next fallback
            logger.error("All selectors for hero_user_email failed.")
            raise NoSuchElementException("Could not find hero user email input element.")

    def enter_hero_email(self, email: str) -> None:
        """
        Enters an email address into the hero section's email input field.

        Args:
            email: The email address to enter.
        """
        try:
            email_input = self._get_hero_email_input()
            email_input.clear()
            email_input.send_keys(email)
            logger.info(f"Entered email '{email[:3]}...' into hero email field.")
        except NoSuchElementException:
            logger.error("Failed to enter email: hero email input not found.")
            raise
        except Exception as e:
            logger.error(f"An error occurred while entering email: {e}")
            raise

    # Hero Section Container
    def _get_hero_section(self) -> WebElement:
        """
        Finds the main hero section element.

        Uses ID selector, with specific CSS class as fallback.
        """
        primary_selector = (By.ID, "hero")
        fallback_selector = (By.CSS_SELECTOR, "section.Primer_Brand__Hero-module__Hero___EM3jf.Primer_Brand__Hero-module__Hero--align-center___HUXm3.lp-IntroHero-hero")
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(primary_selector)
            )
        except TimeoutException:
            logger.warning(f"Primary selector '#hero' for hero section not found. Trying fallback CSS selector.")
            try:
                return WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located(fallback_selector)
                )
            except TimeoutException:
                logger.error("Both selectors for hero section failed.")
                raise NoSuchElementException("Could not find the hero section element.")

    def is_hero_section_displayed(self) -> bool:
        """
        Checks if the hero section is displayed on the page.

        Returns:
            True if the hero section is displayed, False otherwise.
        """
        try:
            hero_section = self._get_hero_section()
            return hero_section.is_displayed()
        except NoSuchElementException:
            return False
        except Exception as e:
            logger.error(f"Error checking hero section display: {e}")
            return False

    # Signup Success Message
    def _get_signup_success_message(self) -> WebElement:
        """
        Finds the signup success message element.

        Uses data-testid and class selectors.
        """
        primary_selector = (By.CSS_SELECTOR, "[data-testid='signup-success-message']")
        fallback_selector = (By.CSS_SELECTOR, ".signup-success-class")
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.visibility_of_element_located(primary_selector)
            )
        except TimeoutException:
            logger.warning(f"Primary selector for signup success message not found. Trying fallback.")
            try:
                return WebDriverWait(self.driver, self.timeout).until(
                    EC.visibility_of_element_located(fallback_selector)
                )
            except TimeoutException:
                logger.error("Both selectors for signup success message failed.")
                raise NoSuchElementException("Could not find the signup success message element.")

    def get_signup_success_message_text(self) -> str:
        """
        Gets the text content of the signup success message.

        Returns:
            The text of the success message.
        """
        try:
            success_message = self._get_signup_success_message()
            return success_message.text
        except NoSuchElementException:
            logger.error("Could not get signup success message text: element not found.")
            return ""
        except Exception as e:
            logger.error(f"Error getting signup success message text: {e}")
            return ""

    # Main Navigation Menu
    def _get_main_nav(self) -> WebElement:
        """
        Finds the main navigation menu element.
        """
        selector = (By.CSS_SELECTOR, "nav.HeaderMenu-nav")
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(selector)
            )
        except TimeoutException:
            logger.error("Main navigation menu 'nav.HeaderMenu-nav' not found.")
            raise NoSuchElementException("Could not find the main navigation menu element.")

    def is_main_nav_displayed(self) -> bool:
        """
        Checks if the main navigation menu is displayed.

        Returns:
            True if the main navigation menu is displayed, False otherwise.
        """
        try:
            nav_element = self._get_main_nav()
            return nav_element.is_displayed()
        except NoSuchElementException:
            return False
        except Exception as e:
            logger.error(f"Error checking main nav display: {e}")
            return False

    # Primary Signup/CTA Button (Hero Section)
    def _get_hero_signup_button(self) -> WebElement:
        """
        Finds the primary signup button in the hero section.

        Uses a combination of selectors.
        """
        primary_selector = (By.CSS_SELECTOR, "#hero_user_email + button")
        fallback_selectors = [
            (By.CSS_SELECTOR, "button[data-testid='hero-signup-button']"),
            (By.CSS_SELECTOR, ".hero-signup-button-css")
        ]
        try:
            # First, try the selector directly related to hero_user_email
            return WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(primary_selector)
            )
        except TimeoutException:
            logger.warning("Primary hero signup button selector '#hero_user_email + button' not found. Trying fallbacks.")
            for selector_type, selector_value in fallback_selectors:
                try:
                    return WebDriverWait(self.driver, self.timeout).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                except TimeoutException:
                    continue # Try next fallback
            logger.error("All selectors for hero signup button failed.")
            raise NoSuchElementException("Could not find the hero signup button element.")

    def click_hero_signup_button(self) -> None:
        """
        Clicks the primary signup button in the hero section.
        """
        try:
            button = self._get_hero_signup_button()
            button.click()
            logger.info("Clicked the hero signup button.")
        except NoSuchElementException:
            logger.error("Failed to click hero signup button: button not found.")
            raise
        except Exception as e:
            logger.error(f"An error occurred while clicking the hero signup button: {e}")
            raise

    # Generic Primary CTA Button (Possibly not in hero)
    def _get_primary_cta_button(self) -> WebElement:
        """
        Finds a generic primary CTA button on the page.
        This selector seems broad and might target the hero signup button or another.
        """
        selector = (By.CSS_SELECTOR, "button.btn.btn-mktg.btn-primary.mb-3.js-navigation-target")
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(selector)
            )
        except TimeoutException:
            logger.error(f"Primary CTA button selector '{selector[1]}' not found.")
            raise NoSuchElementException("Could not find the primary CTA button.")

    def click_primary_cta_button(self) -> None:
        """
        Clicks the generic primary CTA button.
        """
        try:
            button = self._get_primary_cta_button()
            button.click()
            logger.info("Clicked the primary CTA button.")
        except NoSuchElementException:
            logger.error("Failed to click primary CTA button: button not found.")
            raise
        except Exception as e:
            logger.error(f"An error occurred while clicking the primary CTA button: {e}")
            raise

    # Bottom CTA Section Email Input
    def _get_bottom_cta_email_input(self) -> WebElement:
        """
        Finds the email input field in the bottom CTA section.
        """
        selector = (By.ID, "#bottom_cta_section_user_email") # Note: ID selectors don't usually need '#' prefix with By.ID
        # Correcting selector for By.ID
        correct_selector = (By.ID, "bottom_cta_section_user_email")
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(correct_selector)
            )
        except TimeoutException:
            logger.error(f"Bottom CTA email input selector '{correct_selector[1]}' not found.")
            raise NoSuchElementException("Could not find the bottom CTA email input element.")

    def enter_bottom_cta_email(self, email: str) -> None:
        """
        Enters an email address into the bottom CTA section's email input field.

        Args:
            email: The email address to enter.
        """
        try:
            email_input = self._get_bottom_cta_email_input()
            email_input.clear()
            email_input.send_keys(email)
            logger.info(f"Entered email '{email[:3]}...' into bottom CTA email field.")
        except NoSuchElementException:
            logger.error("Failed to enter email: bottom CTA email input not found.")
            raise
        except Exception as e:
            logger.error(f"An error occurred while entering email in bottom CTA: {e}")
            raise

    # --- Placeholder for 'window' related actions ---
    # The selector "window" is not a standard Selenium element.
    # It might imply page-level operations like scrolling, getting dimensions, etc.
    # If specific actions are needed, they would be implemented here.
    # For now, we'll acknowledge it without a specific element method.
    def get_page_title(self) -> str:
        """
        Gets the title of the current page.
        """
        try:
            title = self.driver.title
            logger.info(f"Page title is: '{title}'")
            return title
        except Exception as e:
            logger.error(f"Could not get page title: {e}")
            return ""

# --- Example Usage (for demonstration/testing the POM itself) ---
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager

    logger.info("Setting up WebDriver for example usage.")
    driver = None
    try:
        # Setup Chrome WebDriver using webdriver-manager
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window() # Maximize window for better element visibility

        home_page = github_com_homePage(driver, timeout=15)

        # Example 1: Navigate and check hero section
        home_page.navigate_to()
        print(f"Navigated to: {home_page.URL}")
        print(f"Is hero section displayed? {home_page.is_hero_section_displayed()}")

        # Example 2: Enter email into hero field (if found)
        try:
            home_page.enter_hero_email("testuser@example.com")
            # In a real scenario, you'd interact with the button next
            # home_page.click_hero_signup_button()
        except NoSuchElementException:
            print("Could not interact with hero email field as it was not found.")
        except Exception as e:
            print(f"An error occurred interacting with hero email: {e}")

        # Example 3: Check navigation menu
        print(f"Is main nav displayed? {home_page.is_main_nav_displayed()}")

        # Example 4: Click primary CTA button (if found)
        try:
            # This might click the same button as click_hero_signup_button depending on selectors
            # home_page.click_primary_cta_button()
            pass # Uncomment if you want to test clicking this specific button
        except NoSuchElementException:
            print("Could not click primary CTA button as it was not found.")
        except Exception as e:
            print(f"An error occurred clicking primary CTA button: {e}")

        # Example 5: Enter email into bottom CTA field (if found)
        try:
            home_page.enter_bottom_cta_email("bottomuser@example.com")
        except NoSuchElementException:
            print("Could not interact with bottom CTA email field as it was not found.")
        except Exception as e:
            print(f"An error occurred interacting with bottom CTA email: {e}")

        # Example 6: Get page title
        print(f"Page title: {home_page.get_page_title()}")

    except Exception as e:
        logger.error(f"An error occurred during example execution: {e}")
    finally:
        if driver:
            logger.info("Closing WebDriver.")
            driver.quit()

