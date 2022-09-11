from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import Data.const as CONST


def find_elements(driver, how, what):
    WebDriverWait(driver, CONST.DELAY, ignored_exceptions=CONST.IGNORED_EXCEPTION) \
        .until(EC.presence_of_element_located((how, what)))
    elements = driver.find_elements(how, what)
    return elements


def find_element(driver, how, what):
    WebDriverWait(driver, CONST.DELAY, ignored_exceptions=CONST.IGNORED_EXCEPTION) \
        .until(EC.presence_of_element_located((how, what)))
    element = driver.find_element(how, what)
    return element
