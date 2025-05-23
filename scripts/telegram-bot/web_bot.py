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

    
class SelenimumElement:
    def __init__(self, element: WebElement):
        self.element = element
        self.text = element.text
        self.parent = element.parent
        self.tag_name = element.tag_name
        self.id = element.get_attribute("id")
        self.class_name = element.get_attribute("class")
        self.name = element.get_attribute("name")
        self.value = element.get_attribute("value")

    def find_element(self, by: By, value: str, timeout=10):
        try:
            element = WebDriverWait(self.element, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return SelenimumElement(element)
        except TimeoutException:
            raise Exception(f"Element not found: {value}")

    def find_elements(self, *args, **kwargs):
        return self.element.find_elements(*args, **kwargs)

    def send_keys(self, *args, **kwargs):
        return self.element.send_keys(*args, **kwargs)

    def click(self):
        return self.element.click()

    def get_classes(self):
        return self.element.get_attribute("class").split()

    def exasecute_script(self, script, *args):
        self.element.text
        return self.element.execute_script(script, *args)

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

        find_and_click_button(self.driver, "LOGIN")
        time.sleep(5)

    def stop(self):
        if self.driver:
            self.driver.quit()

    def find_element(self, by: By, value: str, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return SelenimumElement(element)
        except TimeoutException:
            raise Exception(f"Element not found: {value}")

    def find_elements(self, by: By, value: str, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(by, value)) > 0
            )
            elements = self.driver.find_elements(by, value)
            return [SelenimumElement(el) for el in elements]
        except TimeoutException:
            return []


def find_and_click_button(element: WebElement, button_text):
    buttons = element.find_elements(By.TAG_NAME, "button")
    for button in buttons:
        if button.text == button_text:
            button.click()
            return
    raise Exception(f"Button with text '{button_text}' not found")


main_cntrl = MainController()
def main():
    try:
        # 1. Go to the login page
        main_cntrl.start(URL, USERNAME, PASSWORD)
        main_cntrl.login()

        find_and_click_button(main_cntrl.driver, "Futures")
        time.sleep(4)


        # app = main_cntrl.find_element(By.ID, "app")
        # main_window = app.find_element(By.CLASS_NAME, "v-main__wrap")
        delivery_page = main_cntrl.find_element(
            By.CLASS_NAME, "delivery-page"
        )

        # Fid invited me button
        divs = delivery_page.find_elements(By.TAG_NAME, "div")
        invited_me_tab = None
        for div in divs:
            # print(div.text)
            if div.text == "Invited me":
                invited_me_tab = div
                break
        if invited_me_tab is None:
            raise Exception("Invited me Tab not found")
        # Scroll element into view before clicking
        main_cntrl.driver.execute_script(
            "arguments[0].scrollIntoView(true);", invited_me_tab
        )
        time.sleep(1)  # Small pause to allow scrolling to complete
        invited_me_tab.click()
        list_box = delivery_page.find_element(By.CLASS_NAME, "list-box")
        # find_and_click_button(list_box, "INITIATE FOLLOW")

        main_cntrl.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        find_and_click_button(list_box, "CONFIRM TO FOLLOW THE ORDER")
        find_and_click_button(list_box, "CONFIRM")

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