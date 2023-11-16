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


def get_contacts_ooo(sellers: list[dict], service, file_with_contacts) -> dict:
    URL = 'https://zachestnyibiznes.ru/company/ul/'
    in_contacts = pd.read_csv(file_with_contacts)
    driver = webdriver.Chrome(service=service)
    sellers = list(filter(lambda seller: seller['id'] not in in_contacts['id'].values, sellers))
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
                previous = pd.read_csv(file_with_contacts)
                pd.concat([previous, parsed_pf]).to_csv(file_with_contacts, index=False)
                parsed_pf = pd.DataFrame(keys)
                time.sleep(600)
                driver.get(URL + search_value)
                time.sleep(2)
            except Exception as e:
                break

        try:
            WebDriverWait(driver, .2).until(EC.presence_of_element_located((By.XPATH, "//p[@id='cf-spinner-allow-5-secs']")))
            time.sleep(7)
        except Exception:
            pass

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
        
        print(seller['name'], seller['email'], seller['phone'])
        parsed_pf.loc[len(parsed_pf)] = seller


def get_email_ip(sellers: list[dict], service, file_with_contacts, downloads_folder):
    URL = 'https://egrul.nalog.ru/'
    in_contacts = pd.read_csv(file_with_contacts)
    driver = webdriver.Chrome(service=service)
    sellers = list(filter(lambda seller: seller['id'] not in in_contacts['id'].values, sellers))
    driver.get(URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'field-data')))

    for seller in sellers:
        search_value = str(seller['ogrn']).replace('.0', '') or str(seller['ogrnip']).replace('.0', '')
        
        if not search_value:
            continue

        # для того, чтобы соеденить всё в 1 датафрейм
        seller['email'] = ''
        seller['phone'] = ''

        try:
            WebDriverWait(driver, .1).until(EC.presence_of_element_located((By.ID, "uniDialogFrame")))
            time.sleep(120)
            driver.get(URL)
            continue
        except Exception as e:
            pass

        inputEl = driver.find_element(By.CLASS_NAME, 'field-data').find_element(By.TAG_NAME, 'input')
        try:
            inputEl.clear()
            inputEl.send_keys(search_value)
            inputEl.send_keys(Keys.ENTER)
        except Exception:
            continue

        try:
            WebDriverWait(driver, .7, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException,)).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")))
            time.sleep(1.2)
            button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")
        except Exception:
            continue

        try:
            button.click()
        except Exception as e:
            continue
        time.sleep(1.3)

        try:
            email = get_email_from_file(
                pdf_file_path=glob.glob(rf"{downloads_folder}/*.pdf")[-1], 
                text_file_path="pdf_files/current_pdf_file.txt"
            )
        except IndexError:
            continue

        seller['email'] = email

        in_contacts.loc[len(in_contacts)] = seller
        in_contacts.to_csv(file_with_contacts, index=False)

    return sellers


def get_ip_detail(ogrn: str, driver, downloads_folder) -> str:
    URL = 'https://egrul.nalog.ru/'
    driver.get(URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'field-data')))

    while True:
        try:
            WebDriverWait(driver, .1).until(EC.presence_of_element_located((By.ID, "uniDialogFrame")))
            time.sleep(100)
            driver.get(URL)
        except Exception as e:
            break

    inputEl = driver.find_element(By.CLASS_NAME, 'field-data').find_element(By.TAG_NAME, 'input')
    try:
        inputEl.clear()
        inputEl.send_keys(ogrn)
        inputEl.send_keys(Keys.ENTER)
    except Exception:
        return ''

    try:
        WebDriverWait(driver, .7, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException,)).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")))
        time.sleep(.5)
        button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-with-icon') and contains(@class, 'btn-excerpt') and contains(@class, 'op-excerpt')]")
    except Exception:
        return ''

    try:
        button.click()
        print('download start')
    except Exception as e:
        print(e)
        return ''

    try:
        email = get_email_from_file(
            pdf_file_path=glob.glob(rf"{downloads_folder}/*.pdf")[-1], 
            text_file_path="pdf_files/current_pdf_file.txt"
        )
    except IndexError:
        return ''

    return email


def get_ooo_detail(ogrn: str, driver):
    URL = 'https://zachestnyibiznes.ru/company/ul/'

    driver.get(URL + ogrn)

    contact_blocks = (By.XPATH, "//span[starts-with(@id, 'contact')]")
    seller = {'email': '', 'phone': ''}

    while True:
        try:
            WebDriverWait(driver, .5).until(EC.presence_of_element_located((By.XPATH, "//form[@id='challenge-form']")))
            return seller
        except Exception as e:
            break

    try:
        WebDriverWait(driver, .2).until(EC.presence_of_element_located((By.XPATH, "//p[@id='cf-spinner-allow-5-secs']")))
        time.sleep(7)
    except Exception:
        pass

    try:
        WebDriverWait(driver, .5).until(EC.presence_of_element_located(contact_blocks))
    except Exception:
        return seller

    click_blocks = driver.find_elements(*contact_blocks)
    click_blocks[0].click()
    click_blocks = driver.find_elements(*contact_blocks)

    seller['phone'] = click_blocks[0].text
    predicted_emails = [contact.text for contact in click_blocks if '@' in contact.text]
    seller['email'] = predicted_emails[0] if predicted_emails else ''
    
    print(seller['email'], seller['phone'])
    return seller