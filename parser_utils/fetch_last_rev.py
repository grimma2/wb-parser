import pandas as pd
import requests
from fake_useragent import UserAgent


def fetch_revenues(sellers: pd.DataFrame) -> pd.DataFrame:
    ua = UserAgent()
    HEADERS = {
        'User-Agent': ua.random
    }

    URL = r'https://calc.stat4market.app/analysis/sales/suppliers/getSummary'
    sellers['revenues_last_30'] = [None] * len(sellers)
    new_sellers = pd.DataFrame({key: [] for key in sellers.keys()})


    for i, seller in enumerate(sellers['id']):
        params = {'supplier_id': str(seller).replace('.0', '')}

        try:
            r = requests.get(
                URL, params=params, headers=HEADERS
            ).json()
            r = r['data']['SummaryFinance']['OrdersAmount']
        except Exception as e:
            pass

        new_seller = {'id': seller}
        try:
            new_seller['revenues_last_30'] = float(f'{r}.0')
        except ValueError:
            new_seller['revenues_last_30'] = 0.0

        new_sellers.loc[i] = new_seller

    return new_sellers
