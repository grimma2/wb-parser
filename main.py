from parser_utils.collect_wb import get_email_ip, get_contacts_ooo
from parser_utils.recievers import read_pdfs

from selenium import webdriver

import pandas as pd


OOO_text = 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ'
IP_text = 'ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ'

def main():
    sellers = pd.read_csv('sellers_true.csv').fillna('')

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
            pass

    # первая и вторая строчка парсят данные с разных сайтов
    #new_IPs = get_email_ip(IPs, webdriver.ChromeService(executable_path='chromedriver.exe'))
    #IPs_with_email = read_pdfs(IPs=new_IPs)
    new_OOOs = get_contacts_ooo(OOOs, webdriver.ChromeService(executable_path='chromedriver.exe'))
    pd.concat(new_OOOs, ignore_index=True).to_csv('final_sellers.csv')

if __name__ == '__main__':
    main()