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


def get_seller_name(seller_id: int) -> str:
    try:
      responce = requests.get(f"https://www.wildberries.ru/webapi/seller/data/short/{seller_id}", headers=headers).json()
      return responce
    except Exception as e:
      print(e)

df = pd.DataFrame(data={
    "link": [],
})

from_ = 600000
before = 1000000

for seller_id in range(from_, before):
    print(seller_id)
    current_seller = get_seller_name(seller_id=seller_id)

    if current_seller is None:
        continue
    if "name" not in current_seller.keys():
        continue
    if current_seller["name"] == "Продавец":
        continue
    row = {
        **current_seller,
        "link": [f"https://www.wildberries.ru/webapi/seller/data/short/{seller_id}"]
    }
    df = pd.concat([df, pd.DataFrame(data=row)], ignore_index=True)

df.to_csv('sellers_400k.csv', index=False)
