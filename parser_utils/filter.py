from selenium import webdriver
import time

options = webdriver.ChromeOptions()
prefs = {"download.default_directory" : r"C:\Users\anama\OneDrive\Документы\GitHub\wb-parser\parser_utils\test_folder"}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=webdriver.ChromeService(executable_path='chromedriver.exe'), options=options)
driver.get('https://egrul.nalog.ru/')
time.sleep(100)