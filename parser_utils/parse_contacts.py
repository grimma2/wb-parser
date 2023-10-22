import glob

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    StaleElementReferenceException, NoSuchElementException, TimeoutException
)

from parser_utils.read_pdf import get_email_from_file
from fake_useragent import UserAgent

import pandas as pd

import time


def get_finetuned_driver(service) -> webdriver.Chrome:
    ua = UserAgent()

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    options.add_experimental_option("useAutomationExtension", False) 
    options.add_argument(f'--user-agent={ua.random}')

    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    '''
    })

    return driver


def get_contacts_ooo(sellers: list[dict], service) -> dict:
    URL = 'https://zachestnyibiznes.ru/company/ul/'
    driver = get_finetuned_driver(service=service)
    count = 1
    keys = {key: [] for key in sellers[0]}
    keys.update({'phone': [], 'email': []})

    parsed_pf = pd.DataFrame(keys)

    for seller in sellers:
        print(count)
        count += 1
        search_value = str(seller['ogrn']).replace('.0', '')

        if not search_value:
            parsed_pf.loc[len(parsed_pf)] = seller
            continue

        driver.get(URL + search_value)

        contact_blocks = (By.XPATH, "//span[starts-with(@id, 'contact')]")

        while True:
            try:
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//form[@id='challenge-form']")))
                previous = pd.read_csv(r'C:\Users\anama\OneDrive\Документы\GitHub\wb-parser\parser_utils\ooo_with_contact.csv')
                pd.concat([previous, parsed_pf]).to_csv(r'C:\Users\anama\OneDrive\Документы\GitHub\wb-parser\parser_utils\ooo_with_contact.csv', index=False)
                time.sleep(600)
                driver.get(URL + search_value)
            except Exception as e:
                print(e)
                break

        try:
            WebDriverWait(driver, .2).until(EC.presence_of_element_located((By.XPATH, "//p[@id='cf-spinner-allow-5-secs']")))
            time.sleep(7)
        except Exception:
            pass

        """         try:
            WebDriverWait(
                driver, 2
            ).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'aa-Panel') and contains(@class, 'position-fx')]")))

            see_block = driver.find_element(By.XPATH, "//div[contains(@class, 'aa-Panel') and contains(@class, 'position-fx')]")
            see_block.find_element(By.XPATH, "//section[@data-autocomplete-source-id='ul']").click()
            WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located(contact_blocks))
        except (TimeoutException, NoSuchElementException):
            search_input = driver.find_element(By.ID, "autocomplete-0-input")
            search_input.clear()
            parsed_pf.loc[len(parsed_pf)] = seller
            continue """

        try:
            WebDriverWait(driver, 1).until(EC.presence_of_element_located(contact_blocks))
        except Exception:
            parsed_pf.loc[len(parsed_pf)] = seller
            continue

        click_blocks = driver.find_elements(*contact_blocks)
        time.sleep(1)
        click_blocks[0].click()
        click_blocks = driver.find_elements(*contact_blocks)

        seller['phone'] = click_blocks[0].text
        predicted_emails = [contact.text for contact in click_blocks if '@' in contact.text]
        seller['email'] = predicted_emails[0] if predicted_emails else ''
        
        print(seller)
        parsed_pf.loc[len(parsed_pf)] = seller


def get_email_ip(sellers: list[dict], service):
    driver = webdriver.Chrome(service=service)
    driver.get('https://egrul.nalog.ru/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'field-data')))

    for seller in sellers:
        search_value = str(seller['ogrn']).replace('.0', '') or str(seller['ogrnip']).replace('.0', '')
        print(seller['name'], search_value)
        
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
        # time.sleep(2)

        try:
            WebDriverWait(driver, 1, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException,)).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")))
            time.sleep(1)
            button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")
        except Exception:
            continue

        print(button.text)
        button.click()
        time.sleep(.5)
        print('after click')
        try:
            email = get_email_from_file(
                pdf_file_path=glob.glob(r"C:\Users\anama\Downloads\*.pdf")[0], 
                text_file_path="pdf_files/current_pdf_file.txt"
            )
        except IndexError:
            print('exception')
            sellers.remove(seller)
            continue

        seller['email'] = email

    return sellers


"//form[@id='frmCaptcha']"
"//input[@id='captcha']"
"//img[@alt='Необходимо включить загрузку картинок в браузере']"