import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException

import time
import os

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
URL = os.getenv("URL")

# Set up the WebDriver (adjust path to chromedriver if needed)
from selenium.webdriver.chrome.options import Options

    
class SeleniumElement:
    """
    A wrapper class for Selenium WebElement to provide additional functionalities.
    """
    def __init__(self, driver:webdriver.Chrome,  element: WebElement):
        self.driver = driver
        self.element = element
        self.text = element.text
        self.parent = element.parent
        self.tag_name = element.tag_name
        self.id = element.get_attribute("id")
        self.class_name = element.get_attribute("class")
        self.name = element.get_attribute("name")
        self.value = element.get_attribute("value")

    def find_element(self, by: By, value: str, timeout: int = 10) -> 'SeleniumElement':
        """
        Finds a child element within this element.

        Args:
            by: The By strategy (e.g., By.ID, By.XPATH).
            value: The selector string for the element.
            timeout: Maximum time to wait for the element to be present.

        Returns:
            A SeleniumElement object if found.

        Raises:
            Exception: If the element is not found within the timeout.
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return SeleniumElement(self.driver, element)
        except TimeoutException:
            raise Exception(f"Child element not found: {value} within parent {self.tag_name} (ID: {self.id})")

    def find_elements(self, by: By, value: str) -> list['SeleniumElement']:
        """
        Finds all child elements within this element.

        Args:
            by: The By strategy (e.g., By.ID, By.XPATH).
            value: The selector string for the elements.

        Returns:
            A list of SeleniumElement objects.
        """
        elements = self.element.find_elements(by, value)
        return [SeleniumElement(self.driver, el) for el in elements]

    def send_keys(self, *args, **kwargs):
        """Sends keys to the wrapped WebElement."""
        return self.element.send_keys(*args, **kwargs)

    def click(self, timeout:int=5) -> None:
        """Performs a standard click on the wrapped WebElement."""
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(self.element))        
        return self.element.click()

    def get_classes(self) -> list[str]:
        """Returns a list of class names of the element."""
        class_attribute = self.element.get_attribute("class")
        return class_attribute.split() if class_attribute else []

    def execute_script(self, script: str, *args):
        """
        Executes a JavaScript script in the context of the wrapped WebElement.
        Note: This requires access to the WebDriver instance.
        """
        # This method typically requires the driver, not just the element.
        # It's usually better to call driver.execute_script directly.
        # However, if you want to execute script *on* this element,
        # you'd need the driver instance passed here or stored.
        # For simplicity, this method might be better placed in MainController
        # or require the driver as an argument.
        # For now, it will use the element's internal execute_script if it exists,
        # but a direct driver.execute_script is more common.
        raise NotImplementedError("execute_script on WebElement directly is not common for general JS. "
                                  "Consider using driver.execute_script and passing self.element as argument.")

    def get_button(self, button_text)-> 'SeleniumElement':
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if button.text == button_text:
                return SeleniumElement(self.driver, button)
        raise Exception(f"Button with text '{button_text}' not found")

    def robust_click(self, timeout: int = 10) -> bool:
        """
        Attempts to click this WebElement using various robust strategies.
        This method handles ElementClickInterceptedException by trying
        to scroll the element into view and then using JavaScript click as fallback.

        Args:
            driver: The Selenium WebDriver instance, required for scrolling and JavaScript execution.
            timeout: Maximum time to wait for the element to be clickable.

        Returns:
            True if the click was successful, False otherwise.
        """
        print(f"\nAttempting to robustly click element: <{self.tag_name}> (ID: '{self.id}', Class: '{self.class_name}', Text: '{self.text.strip()}')")
        try:
            # Strategy 1: Wait for element to be clickable using WebDriverWait
            print("Strategy 1: Waiting for element to be clickable...")
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(self.element))
            self.element.click()
            print("Successfully clicked using WebDriverWait.")
            return True
        except ElementClickInterceptedException:
            print("ElementClickInterceptedException caught. Trying alternative strategies.")
            try:
                # Strategy 2: Scroll into view and then click
                print("Strategy 2: Scrolling element into view and clicking...")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", self.element)
                time.sleep(0.5) # Give a small moment for scroll to complete
                self.element.click()
                print("Successfully clicked after scrolling into view.")
                return True
            except ElementClickInterceptedException:
                print("ElementClickInterceptedException after scroll. Trying JavaScript click.")
                # Strategy 3: Click using JavaScript
                try:
                    self.driver.execute_script("arguments[0].click();", self.element)
                    print("Successfully clicked using JavaScript.")
                    return True
                except Exception as e:
                    print(f"Failed to click with JavaScript: {e}")
                    return False
            except TimeoutException:
                print(f"Timeout waiting for element to be clickable after scroll.")
                return False
            except Exception as e:
                print(f"An unexpected error occurred during click attempt (Strategy 2/3): {e}")
                return False
        except TimeoutException:
            print(f"Timeout waiting for element to be clickable.")
            return False
        except NoSuchElementException:
            print(f"Element not found during robust click attempt.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during robust click attempt (Strategy 1): {e}")
            return False

class MainController:
    def __init__(self, driver=None):
        self.driver = None

    def start(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        chromedriver_path = "/home/vagos/.cache/selenium/chromedriver/linux64/131.0.6778.264/chromedriver"
        self.driver = webdriver.Chrome(
            service=Service(chromedriver_path), options=options
        )
        self.driver.get(self.url)
        self.driver.implicitly_wait(3)

    def login(self):
        username_input = self.find_element(By.XPATH, "//input[@type='text']")
        password_input = self.find_element(By.XPATH, "//input[@type='password']")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        self.get_button("LOGIN").click()
        time.sleep(5)

    def stop(self):
        if self.driver:
            self.driver.quit()

    def find_element(self, by: By, value: str, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return SeleniumElement(self.driver, element)
        except TimeoutException:
            raise Exception(f"Element not found: {value}")

    def find_elements(self, by: By, value: str, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(by, value)) > 0
            )
            elements = self.driver.find_elements(by, value)
            return [SeleniumElement(self.driver, el) for el in elements]
        except TimeoutException:
            return []

    def get_button(self, button_text)-> SeleniumElement:
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if button.text == button_text:
                return SeleniumElement(self.driver, button)
        raise Exception(f"Button with text '{button_text}' not found")

    def scroll_to_element(self, element: SeleniumElement):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element.element)
        time.sleep(0.5)  # Small pause to allow scrolling to complete

def main():
    try:
        main_cntrl = MainController()
        # 1. Go to the login page
        main_cntrl.start(URL, USERNAME, PASSWORD)
        main_cntrl.login()

        main_cntrl.get_button("Futures").click()
        # time.sleep(4)

        delivery_page = main_cntrl.find_element(
            By.CLASS_NAME, "delivery-page"
        )

        # Find invited me button
        time.sleep(1)
        divs = delivery_page.find_elements(By.TAG_NAME, "div")
        invited_me_tab = None
        for div in divs:
            # print(div.text)
            if div.text == "Invited me":
                invited_me_tab = div
                break
        if invited_me_tab is None:
            raise Exception("Invited me Tab not found")
        main_cntrl.scroll_to_element(invited_me_tab)
        invited_me_tab.click()
        list_box = delivery_page.find_element(By.CLASS_NAME, "list-box")

        list_box.get_button(
            "CONFIRM TO FOLLOW THE ORDER"
        ).robust_click()
        
        time.sleep(2)

        list_box.get_button(
            "CONFIRM"
        ).robust_click()

    finally:
        main_cntrl.stop()


if __name__ == "__main__":
    main()
# This script automates the login process to a website using Selenium WebDriver.
# It fills in the username and password, submits the form, and navigates to a specific tab.
# Make sure to adjust the XPATH and other selectors according to the actual HTML structure of the page.
# Note: The script uses headless mode for Chrome, which means it won't open a visible browser window.
# You can remove the headless option if you want to see the browser actions.
# <span class="v-btn__content"><span data-v-18dc93bb="" class="font-primary-12">Confirm to follow the order</span></span>