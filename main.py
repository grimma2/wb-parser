from parser_utils.parse_contacts import get_email_ip, get_contacts_ooo
from parser_utils.fetch_last_rev import fetch_revenues
from parser_utils.parser_names_increment import parse_sellers

from selenium import webdriver

import pandas as pd

from multiprocessing import Process


CONFIG = (
    ('sellers_0k_50k.csv', 'ooos_0k_50k.csv', 'ips_0k_50k.csv', '/home/anama2/wb-parser/pdf_0k_50k', 0, 50000, {'login': '', 'password': '', 'host': ''}),
    ('sellers_50k_100k.csv', 'ooos_50k_100k.csv', 'ips_50k_100k.csv', '/home/anama2/wb-parser/pdf_50k_100k', 0, 100000, {'login': '', 'password': '', 'host': ''}),
    ('sellers_100k_150k.csv', 'ooos_100k_150k.csv', 'ips_100k_150k.csv', '/home/anama2/wb-parser/pdf_100k_150k', 0, 150000, {'login': '', 'password': '', 'host': ''}),
    ('sellers_0k_50k.csv', 'ooos_150k_200k.csv', 'ips_150k_200k.csv', '/home/anama2/wb-parser/pdf_150k_200k', 0, 200000, {'login': '', 'password': '', 'host': ''})
)
OOO_text = 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ'
IP_text = 'ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ'
# можно менять для получения больших данных
# !!! после каждого запуска, предыдущий файл в переменной file_sellers перезаписывается


def parse_process(file_sellers, file_ooos, file_ips, downloads_folder, from_, before, proxy):
    sellers = parse_sellers(file_sellers, from_, before, proxy=proxy).fillna('')

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

    try:
        done_ooos = pd.read_csv(file_ooos)
        done_ips = pd.read_csv(file_ips)
    except Exception:
        from_df = {'id': [], 'link': [], 'ogrn': [], 'ogrnip': [], 'isUnknown': [], 'fineName': [], 'trademark': [], 'name': [], 'legalAddress': []}
        pd.DataFrame(from_df).to_csv(file_ips)
        pd.DataFrame(from_df).to_csv(file_ooos)
        done_ooos = pd.read_csv(file_ooos)
        done_ips = pd.read_csv(file_ips)

    proxy_server = {
        'proxy': {
            'https': f'http://{proxy["login"]}:{proxy["password"]}@{proxy["host"]}'
        }
    }
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": downloads_folder}
    options.add_argument('prefs', prefs)

    get_email_ip(IPs[len(done_ips):], webdriver.Chrome(seleniumwire_options=proxy_server, options=options), file_ips=file_ips, downloads_folder=downloads_folder)
    get_contacts_ooo(
        sellers=OOOs[len(done_ooos):],
        driver=webdriver.Chrome(seleniumwire_options=proxy_server, options=options),
        file_ooos=file_ooos
    )

    ooos_with_contacts = pd.read_csv(file_ooos)
    ips_with_contacts = pd.read_csv(file_ips)
    sellers_with_contacts = pd.concat([ooos_with_contacts, ips_with_contacts])
    sellers_with_contacts.to_csv(file_sellers, index=False)
    sellers = fetch_revenues(sellers_with_contacts)
    sellers.drop_duplicates().drop(columns=['link', 'id', 'isUnknown']).to_csv(file_sellers, index=False)


def main():
    for process_args in CONFIG:
        p = Process(target=parse_process, args=process_args)
        p.start()
        p.join()


if __name__ == '__main__':
    main()