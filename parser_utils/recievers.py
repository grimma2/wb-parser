import pandas as pd


contacts = pd.read_csv(r'C:\Users\anama\OneDrive\Документы\GitHub\wb-parser\parser_utils\ooo_with_contact.csv')
revenues = pd.read_csv(r'C:\Users\anama\OneDrive\Документы\GitHub\wb-parser\parser_utils\sellers_with_revenue.csv')


a = {key: [] for key in contacts.keys()}
a['revenues'] = []
result = pd.DataFrame(a)
count = 1
for _, row in contacts.iterrows():
    print(count)
    count += 1
    try:
        this_row = revenues.loc[revenues['id'] == row['id']]
    except:
        continue

    if this_row['revenues'].empty:
        continue

    this_row = this_row.to_dict()
    this_row = {key: list(value.values())[0] for key, value in this_row.items()}
    this_row['phone'] = row['phone']
    this_row['email'] = row['email']
    result.loc[len(result)] = this_row


result.to_csv('test_ooos.csv')