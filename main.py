from parser_utils.parse_contacts import get_email_ip, get_contacts_ooo

from selenium import webdriver

import pandas as pd


OOO_text = 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ'
IP_text = 'ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ'

def main():

    sellers = pd.read_csv('sellers.csv').fillna('').loc[:100000]
    print('a')

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
    print('b')

    done_ooos = pd.read_csv(r'C:\Users\anama\OneDrive\Документы\GitHub\wb-parser\parser_utils\ooo_with_contact.csv')
    # первая и вторая строчка парсят данные с разных сайтов
    #new_IPs = get_email_ip(IPs, webdriver.ChromeService(executable_path='chromedriver.exe'))
    get_contacts_ooo(
        sellers=OOOs[len(done_ooos):],
        service=webdriver.ChromeService(executable_path='chromedriver.exe')
    )


if __name__ == '__main__':
    main()