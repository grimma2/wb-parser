import pandas as pd

import requests
from fake_useragent import UserAgent


ua = UserAgent()

URL = r'https://catalog.wb.ru/sellers/catalog?TestGroup=test_group_60&curr=rub&dest=-1257786&spp=29&supplier='
HEADERS = requests.utils.default_headers()
HEADERS.update({'User-Agent': ua.random})
sellers = pd.read_csv('sellers.csv')


sellers['revenues'] = [None] * len(sellers)

count = 1
for i, row in sellers.iterrows():
    print(count)
    count += 1
    seller_id = str(row['id']).replace('.0', '')
    try:
        products = requests.get(url=URL + seller_id, headers=HEADERS).json()['data']['products']
    except Exception as e:
        sellers = sellers.drop(i)
        print(e)
        continue

    if len(products) == 0:
        sellers = sellers.drop(i)
        continue

    sellers['revenues'][i] = (
        sum([product['feedbacks'] * (product['salePriceU'] / 100) for product in products])
    )

sellers.to_csv('sellers_with_revenue.csv', index=False)
