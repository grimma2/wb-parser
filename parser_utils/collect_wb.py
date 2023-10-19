from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

import time


def get_contacts_ooo(sellers: str, service) -> dict:
    driver = webdriver.Chrome(service=service)
    driver.get('https://zachestnyibiznes.ru/lp/egrul_egrip/')

    for seller in sellers:
        search_value = str(seller['ogrn']).replace('.0', '')

        if not search_value:
            sellers.remove(seller)
            continue

        input_xpath = (By.XPATH, "//input[@class='aa-Input']")
        result_xpath = (By.XPATH, "//ul[@class='aa-List'] and @role='listbox'")

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(*input_xpath))
        input_el = driver.find_element(*input_xpath)
        input_el.send_keys(search_value)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(*result_xpath))
        result = driver.find_element(*result_xpath)
        result.click()




def get_email_ip(sellers: list[dict], service):
    driver = webdriver.Chrome(service=service)
    driver.get('https://egrul.nalog.ru/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'field-data')))

    for seller in sellers:
        search_value = str(seller['ogrn']).replace('.0', '') or str(seller['ogrnip']).replace('.0', '')
        print(seller['name'])
        
        if not search_value:
            sellers.remove(seller)
            continue

        inputEl = driver.find_element(By.CLASS_NAME, 'field-data').find_element(By.TAG_NAME, 'input')
        inputEl.clear()
        inputEl.send_keys(search_value)
        inputEl.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException,)).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")))
        time.sleep(.75)
        button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")
        button.click()
        time.sleep(.5)

    return sellers
