import requests
import pandas as pd
from fake_useragent import UserAgent


def get_seller_name(seller_id: int, headers) -> str:
    try:
        responce = requests.get(f"https://www.wildberries.ru/webapi/seller/data/short/{seller_id}", headers=headers).json()
        return responce
    except Exception as e:
        print(e)


def parse_sellers(file_sellers: str) -> pd.DataFrame:
    df = pd.DataFrame(data={
        "link": [],
        "revenues": []
    })

    ua = UserAgent()
    headers = requests.utils.default_headers()

    headers.update(
        {
            'User-Agent': ua.random,
        }
    )

    from_ = 0
    before = 1000000

    for seller_id in range(from_, before):
        current_seller = get_seller_name(seller_id=seller_id, headers=headers)

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

    df.to_csv(file_sellers, index=False)

    return df