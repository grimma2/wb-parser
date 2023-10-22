import pandas as pd


d1 = pd.read_csv('sellers_2.csv')
d2 = pd.read_csv('sellers_3.csv')
d3 = pd.read_csv('sellers_400k.csv')
d4 = pd.read_csv('sellers_true.csv')

pd.concat([d1, d2, d3, d4], ignore_index=True).to_csv('sellers.csv', index=False)