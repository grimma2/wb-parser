from parser_utils.parse_contacts import get_email_ip, get_contacts_ooo

from selenium import webdriver

import pandas as pd


OOO_text = 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ'
IP_text = 'ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ'

def main():
    file_sellers = r'C:\Users\anama\OneDrive\Документы\GitHub\wb-parser\parser_utils\sellers_with_revenue.csv'
    file_ooos = r'C:\Users\anama\OneDrive\Документы\GitHub\wb-parser\parser_utils\test_ooos.csv'
    file_ips = r'C:\Users\anama\OneDrive\Документы\GitHub\wb-parser\parser_utils\ips_with_contacts.csv'

    sellers = pd.read_csv(file_sellers).fillna('')

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

    # первая и вторая строчка парсят данные с разных сайтов
    new_IPs = get_email_ip(IPs[len(done_ips):], webdriver.ChromeService(executable_path='chromedriver.exe'), file_ips=file_ips)
    try:
        pd.DataFrame.from_records(new_IPs).to_csv(file_ips)
    except Exception as e:
        print(e)
        print(new_IPs)

    """     get_contacts_ooo(
        sellers=OOOs[len(done_ooos):],
        service=webdriver.ChromeService(executable_path='chromedriver.exe'),
        file_ooos=file_ooos
    ) """


if __name__ == '__main__':
    main()