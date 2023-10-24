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

from PIL import Image, ImageMath
import requests
from dataclasses import dataclass

import time


class ColorsRemover:

    def __init__(self, image, colors: tuple[tuple]) -> None:
        for cl in colors:
            image = self.color_to_alpha(image, cl)

        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image.convert('RGB'), mask=image)
        background.save('parser_utils\converted.png')

    def difference1(self, source, color):
        """When source is bigger than color"""
        return (source - color) / (255.0 - color)

    def difference2(self, source, color):
        """When color is bigger than source"""
        return (color - source) / color


    def color_to_alpha(self, image, color=None):
        image = image.convert('RGBA')
        width, height = image.size

        color = list(map(float, color))
        img_bands = [band.convert("F") for band in image.split()]

        # Find the maximum difference rate between source and color. I had to use two
        # difference functions because ImageMath.eval only evaluates the expression
        # once.
        alpha = ImageMath.eval(
            """float(
                max(
                    max(
                        max(
                            difference1(red_band, cred_band),
                            difference1(green_band, cgreen_band)
                        ),
                        difference1(blue_band, cblue_band)
                    ),
                    max(
                        max(
                            difference2(red_band, cred_band),
                            difference2(green_band, cgreen_band)
                        ),
                        difference2(blue_band, cblue_band)
                    )
                )
            )""",
            difference1=self.difference1,
            difference2=self.difference2,
            red_band = img_bands[0],
            green_band = img_bands[1],
            blue_band = img_bands[2],
            cred_band = color[0],
            cgreen_band = color[1],
            cblue_band = color[2]
        )

        # Calculate the new image colors after the removal of the selected color
        new_bands = [
            ImageMath.eval(
                "convert((image - color) / alpha + color, 'L')",
                image = img_bands[i],
                color = color[i],
                alpha = alpha
            )
            for i in range(3)
        ]

        # Add the new alpha band
        new_bands.append(ImageMath.eval(
            "convert(alpha_band * alpha, 'L')",
            alpha = alpha,
            alpha_band = img_bands[3]
        ))

        return Image.merge('RGBA', new_bands)


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


def get_contacts_ooo(sellers: list[dict], service, file_ooos) -> dict:
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
                previous = pd.read_csv(file_ooos)
                pd.concat([previous, parsed_pf]).to_csv(file_ooos, index=False)
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


class CaptchaBreakerIP:

    def validate_output(self, captcha_text):
        print(captcha_text)
        if len(captcha_text) != 6:
            return

        for let in captcha_text:
            try:
                int(let)
            except Exception:
                return
            
        return True


    def prepare_image(self, driver: webdriver.Chrome, url, file_ips):
        rm_colors = (
            (134,169,203,255), (123,134,167,255),
            (188,212,232,255), (183,175,196,255),
            (104,180,229,255), (143,151,148,255),
            (192,188,188,255)
        )

        try:
            WebDriverWait(driver, .1).until(EC.presence_of_element_located((By.ID, "uniDialogFrame")))
            time.sleep(120)
            return
        except Exception as e:
            print('this')
            print(e)
            return

        driver.switch_to.frame(driver.find_element(By.ID, "uniDialogFrame"))
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//img[@alt='Необходимо включить загрузку картинок в браузере']")))
        img = driver.find_element(By.XPATH, "//img[@alt='Необходимо включить загрузку картинок в браузере']")
        img_url = img.get_attribute('src')

        opened_image = Image.open(requests.get(img_url, stream=True).raw)
        ColorsRemover(image=opened_image, colors=rm_colors)
        captcha_text = self.read_image()

        if not self.validate_output(captcha_text):
            driver.find_element(By.XPATH, "//a[text()='Обновить картинку с цифрами']").click()
            print('not valid')
            driver.switch_to.default_content()
            raise Exception()

        print(captcha_text)
        input_block = driver.find_element(By.ID, "captcha")
        input_block.click()

        for letter in captcha_text:
            time.sleep(1)
            input_block.send_keys(letter)

        time.sleep(2)
        driver.find_element(By.ID, "btnOk").click()
        driver.switch_to.default_content()
        time.sleep(10)


    def read_image(self) -> str:
        url = "https://app.nanonets.com/api/v2/OCR/FullText"

        files = [
            ('file', ('converted', open('parser_utils\converted.png','rb'),'application/pdf'))
        ]

        headers = {}

        response = requests.request("POST", url, headers=headers, files=files, auth=requests.auth.HTTPBasicAuth('66f0b9f2-719f-11ee-8978-ca68d4a478c6', ''))
        time.sleep(3)

        try:
            return response.json()['results'][0]['page_data'][0]['words'][0]['text']
        except IndexError:
            return


def get_email_ip(sellers: list[dict], service, file_ips):
    URL = 'https://egrul.nalog.ru/'
    driver = get_finetuned_driver(service=service)
    driver.get(URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'field-data')))

    for seller in sellers:
        search_value = str(seller['ogrn']).replace('.0', '') or str(seller['ogrnip']).replace('.0', '')
        
        if not search_value:
            sellers.remove(seller)
            continue

        # для того, чтобы соеденить всё в 1 датафрейм
        seller['email'] = ''
        seller['phone'] = ''

        try:
            WebDriverWait(driver, .1).until(EC.presence_of_element_located((By.ID, "uniDialogFrame")))
            time.sleep(120)
            return
        except Exception as e:
            pass

        inputEl = driver.find_element(By.CLASS_NAME, 'field-data').find_element(By.TAG_NAME, 'input')
        try:
            inputEl.clear()
            inputEl.send_keys(search_value)
            inputEl.send_keys(Keys.ENTER)
        except Exception:
            sellers.remove(seller)
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
            sellers.remove(seller)
            continue
        time.sleep(1.3)

        try:
            email = get_email_from_file(
                pdf_file_path=glob.glob(r"C:\Users\anama\Downloads\*.pdf")[-1], 
                text_file_path="pdf_files/current_pdf_file.txt"
            )
        except IndexError:
            sellers.remove(seller)
            continue

        seller['email'] = email

        previous = pd.read_csv(file_ips)
        news = pd.DataFrame(data={key: [value] for key, value in seller.items()})
        concated = pd.concat([previous, news], ignore_index=True)
        concated.to_csv(file_ips, index=False)
        print('after all', seller['email'])

    return sellers
