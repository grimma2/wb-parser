from parser_utils.parse_contacts import get_email_ip, get_contacts_ooo
from parser_utils.fetch_last_rev import fetch_revenues
from parser_utils.parser_names_increment import parse_sellers
from parser_utils.parse_names_ozon import ozon_parser

import sys

from selenium import webdriver

import pandas as pd


OOO_text = 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ'
IP_text = 'ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ'
# два значения, которые перебирают всех продавцов на wb
# можно менять для получения больших данных
# !!! после каждого запуска, предыдущий файл в переменной file_sellers перезаписывается

def wb_parser():
    FROM = 200000
    BEFORE = 400000
    seller_with_no_contacts = 'parser_utils/no_contacts_sellers.csv'
    sellers_with_contacts = 'parser_utils/raw_sellers.csv'
    sellers_with_revenues = 'parser_utils/sellers_with_revenues.csv'
    downloads_folder = r'C:\Users\anama\Downloads' # передать папку, в которую у вас устанавливаются файлы мз браузера

    sellers = parse_sellers(seller_with_no_contacts, FROM, BEFORE).fillna('')

    OOOs = []
    IPs = []

    for _, row in sellers.iterrows():

        if 'name' not in row.keys():
            IPs.append(row.to_dict())
        elif 'ООО' in row['name'].upper() or OOO_text in row['name'].upper():
            OOOs.append(row.to_dict())
        elif 'ИП' in row['name'].upper() or IP_text in row['name'].upper():
            IPs.append(row.to_dict())
        else:
            IPs.append(row.to_dict())

    get_email_ip(
        sellers=IPs,
        service=webdriver.ChromeService(executable_path='chromedriver.exe'), 
        file_with_contacts=sellers_with_contacts, 
        downloads_folder=downloads_folder
    )
    get_contacts_ooo(
        sellers=OOOs,
        service=webdriver.ChromeService(executable_path='chromedriver.exe'),
        file_with_contacts=sellers_with_contacts,
    )

    sellers = fetch_revenues(pd.read_csv(sellers_with_contacts))
    sellers.drop_duplicates().drop(columns=['link', 'id', 'isUnknown']).to_csv(sellers_with_revenues, index=False)


def main(parse):
    if parse == 'ozon':
        ozon_parser()
    elif parse == 'wb':
        wb_parser()


if __name__ == '__main__':
    main(parse=sys.argv[1])