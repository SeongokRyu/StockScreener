import os
import pandas as pd

from libs.utils import get_code_list

clean_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')
df_stocks = pd.read_csv(clean_path)

sector_path = os.path.join(os.getcwd(), 'data', 'stocks_sector.csv')
df_sector = pd.read_csv(sector_path)

code_stocks = get_code_list(df_stocks)
code_sector = get_code_list(df_sector)
code_merged = list(set(code_stocks) & set(code_sector))

df_stocks = df_stocks[df_stocks['Code'].isin(code_merged)].sort_values(by=['Code'])
df_sector = df_sector[df_sector['Code'].isin(code_merged)].sort_values(by=['Code'])

sector_list = df_sector['Sector']
df_stocks['Sector'] = sector_list

print (df_stocks)
print ("ASDFSAD")
print (df_sector)
