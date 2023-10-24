import pandas as pd


list_k = ['link','id','fineName','ogrn','ogrnip','isUnknown','trademark','legalAddress','name','phone','email','revenues']
a = {key: [] for key in list_k}
pd.DataFrame.from_dict(a).to_csv('ips_with_contacts.csv', index=False)
