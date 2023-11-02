from parser_utils.parse_contacts import get_email_ip, get_contacts_ooo
from parser_utils.fetch_last_rev import fetch_revenues
from parser_utils.parser_names_increment import parse_sellers

from selenium import webdriver

import pandas as pd


OOO_text = 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ'
IP_text = 'ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ'

def main():
    file_sellers = '<your_csv_file>'
    file_ooos = '<your_csv_file>'
    file_ips = '<your_csv_file>'

    sellers = parse_sellers(file_sellers).fillna('')

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

    done_ooos = pd.read_csv(file_ooos)
    done_ips = pd.read_csv(file_ips)

    get_email_ip(IPs[len(done_ips):], webdriver.ChromeService(executable_path='chromedriver.exe'), file_ips=file_ips)
    get_contacts_ooo(
        sellers=OOOs[len(done_ooos):],
        service=webdriver.ChromeService(executable_path='chromedriver.exe'),
        file_ooos=file_ooos
    )

    ooos_with_contacts = pd.read_csv(file_ooos)
    ips_with_contacts = pd.read_csv(file_ips)
    sellers_with_contacts = pd.concat([ooos_with_contacts, ips_with_contacts])
    sellers_with_contacts.to_csv('sellers.csv')
    sellers = fetch_revenues(sellers_with_contacts)
    sellers.drop_duplicates().drop(columns=['link', 'id', 'isUnknown']).to_csv('sellers.csv', index=False)


if __name__ == '__main__':
    main()