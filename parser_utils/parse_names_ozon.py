from selenium import webdriver
from fake_useragent import UserAgent
import requests
import pandas as pd
import time

from .parse_contacts import get_ip_detail, get_ooo_detail


def ozon_parser():
    OZON_FILE = 'parser_utils/ozon_db.csv'

    FROM = 1
    BEFORE = 1000000

    NAME_URL = r'https://api.moneyplace.io/v1/seller/'
    REVENUES_URL = r'https://api.moneyplace.io/statistic/seller/charts/'
    REVENUES_PARAMS = {'nop': '0', 'period': 'month', 'type': 'fbo'}
    DOWNLOADS_FOLDER = r'C:\Users\anama\Downloads'
    HEADERS = {'Authorization': 'Bearer 0cde1f96cedbbc25c1952ca7c927bcf62e03a5a8', 'User-Agent': UserAgent().random}
    sellers_data_state = pd.read_csv(OZON_FILE)

    for seller_id in range(FROM, BEFORE):
        print(seller_id)
        if float(seller_id) in sellers_data_state['id']:
            continue

        seller_name = requests.get(f'{NAME_URL}{seller_id}', headers=HEADERS).json()
        time.sleep(0.01)
        seller_revenues = requests.get(f'{REVENUES_URL}{seller_id}', params=REVENUES_PARAMS, headers=HEADERS).json()

        if seller_name.get('id'):
            seller_data = {
                'id': seller_name['id'],
                'name': seller_name['name'],
                'ogrn': seller_name.get('ogrn', 0),
            }

            if seller_data['ogrn']:
                driver = webdriver.Chrome(service=webdriver.ChromeService(executable_path='chromedriver.exe'))
                if 'ИП' in seller_name['name']:
                    seller_data['email'] = get_ip_detail(str(seller_data['ogrn']), driver, DOWNLOADS_FOLDER)
                else:
                    seller_data.update(get_ooo_detail(str(seller_data['ogrn']), driver))

            seller_data['revenues_last_30'] = sum([int(product['total_sum']) for product in seller_revenues]) if type(seller_revenues) == list else 0
            print(f'revenues: {seller_data["revenues_last_30"]}')

            sellers_data_state.loc[len(sellers_data_state)] = seller_data
            sellers_data_state.to_csv(OZON_FILE, index=False)
        elif seller_name.get('name') == 'Unauthorized':
            print('Unauthtorized!')
            break
        else:
            print(f'seller_name code: {seller_name}, seller_revenues code: {seller_revenues}')
