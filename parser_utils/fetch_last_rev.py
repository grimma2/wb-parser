import pandas as pd
import requests
from fake_useragent import UserAgent


def add_sellers():
    no_contacts = pd.read_csv('no_contacts_sellers.csv').sample(n=30000)
    raw_sellers = pd.read_csv('raw_sellers.csv')

    df = pd.DataFrame({key: [] for key in raw_sellers.keys()})

    for i, seller in no_contacts.iterrows():
        if seller['id'] not in raw_sellers['id'].unique():
            df.loc[len(df)] = seller.to_dict()

    pd.concat([raw_sellers, df], ignore_index=True).to_csv('raw_sellers2.csv', index=False)


def fetch_revenues(sellers_path, save_path) -> pd.DataFrame:
    sellers = pd.read_csv(sellers_path)
    ua = UserAgent()
    HEADERS = {
        'User-Agent': ua.random
    }

    URL = r'https://calc.stat4market.app/analysis/sales/suppliers/getSummary'
    sellers['revenues_last_30'] = [0] * len(sellers)
    new_sellers = pd.DataFrame({key: [] for key in sellers.keys()})


    for i, seller in enumerate(sellers['id']):
        print(i)
        params = {'supplier_id': str(seller).replace('.0', '')}

    try:
        r = requests.get(
            URL, params=params, headers=HEADERS
        ).json()
        r = r['data']['SummaryFinance']['OrdersAmount']
    except Exception as e:
        print(e)
        pass

        new_seller = {'id': seller}
        try:
            new_seller['revenues_last_30'] = float(f'{r}.0')
        except ValueError:
            new_seller['revenues_last_30'] = 0.0

        new_sellers.loc[i] = new_seller

        new_sellers.to_csv(save_path, index=False)


if __name__ == '__main__':
    #add_sellers()
    fetch_revenues(pd.read_csv('raw_sellers2.csv')).to_csv('whole_wb.csv')