import requests
import pandas as pd
from fake_useragent import UserAgent


ua = UserAgent()


headers = requests.utils.default_headers()

headers.update(
    {
        'User-Agent': ua.random,
    }
)
fetch_url = r'https://catalog.wb.ru/sellers/catalog?TestGroup=test_group_60&curr=rub&dest=-1257786&spp=29&supplier='

def fetch_revenue(seller_id):
    try:
        products = requests.get(url=fetch_url + str(seller_id), headers=headers).json()['data']['products']
    except Exception as e:
        print(e)
        return

    if len(products) == 0:
        return

    return (
        sum([product['feedbacks'] * (product['salePriceU'] / 100) for product in products])
    )


def get_seller_name(seller_id: int) -> str:
    try:
      responce = requests.get(f"https://www.wildberries.ru/webapi/seller/data/short/{seller_id}", headers=headers).json()
      return responce
    except Exception as e:
      print(e)

df = pd.DataFrame(data={
    "link": [],
    "revenues": []
})

from_ = 115000
before = 120000

for seller_id in range(from_, before):
    print(seller_id)
    current_seller = get_seller_name(seller_id=seller_id)

    if current_seller is None:
        continue
    if "name" not in current_seller.keys():
        continue
    if current_seller["name"] == "Продавец":
        continue

    parsed_rev = fetch_revenue(seller_id=seller_id)

    if not parsed_rev:
        continue

    row = {
        **current_seller,
        'revenue': parsed_rev,
        "link": [f"https://www.wildberries.ru/webapi/seller/data/short/{seller_id}"]
    }
    df = pd.concat([df, pd.DataFrame(data=row)], ignore_index=True)

df.to_csv('sellers_with_revenue_2.csv', index=False)