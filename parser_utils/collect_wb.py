from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    StaleElementReferenceException, NoSuchElementException, TimeoutException
)

from parser_utils.read_pdf import get_email_from_file

import time


def check_captcha_ooo(driver, service) -> webdriver.Chrome:
    # была для изменения юзер агента и прокси
    try:
        print('captcha block')
        driver.find_element(By.ID, 'challenge-form')
        print('find captcha')
        options = webdriver.ChromeOptions()

        #options.add_argument(f'--proxy-server=http://{new_proxy}')
        #print(str(rp.get_random_proxy()).split()[0])

        return webdriver.Chrome(service=service, options=options)
    except NoSuchElementException:
        return


def get_contacts_ooo(sellers: list[dict], service) -> dict:
    URL = 'https://zachestnyibiznes.ru/company/ul/'
    driver = webdriver.Chrome(service=service)

    for seller in sellers:
        search_value = str(seller['ogrn']).replace('.0', '')

        if not search_value:
            sellers.remove(seller)
            continue

        contact_blocks = (By.XPATH, "//span[starts-with(@id, 'contact')]")

        driver.get(URL + search_value)

        #if (result_driver := check_captcha_ooo(driver, service)):
        #    driver = result_driver

        try:
            time.sleep(150)
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(contact_blocks))
        except TimeoutException:
            sellers.remove(seller)
            continue

        click_blocks = driver.find_elements(*contact_blocks)
        click_blocks[0].click()
        click_blocks = driver.find_elements(*contact_blocks)
        seller['phone'] = click_blocks[0].text
        predicted_emails = [contact.text for contact in click_blocks if '@' in contact.text]
        seller['email'] = predicted_emails[0] if predicted_emails else ''

    return sellers


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

        # для того, чтобы соеденить всё в 1 датафрейм
        seller['email'] = ''
        seller['phone'] = ''

        inputEl = driver.find_element(By.CLASS_NAME, 'field-data').find_element(By.TAG_NAME, 'input')
        inputEl.clear()
        inputEl.send_keys(search_value)
        inputEl.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException,)).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")))
        time.sleep(.75)
        button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")
        button.click()

    return sellers
