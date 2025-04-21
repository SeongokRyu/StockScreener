import os

import pandas as pd


def create_directories(date):
	dir_list = [
		os.path.join(os.getcwd(), 'data', 'stocks'),
		os.path.join(os.getcwd(), 'data', 'financial_highlight', date),
		os.path.join(os.getcwd(), 'data', 'price'),
		os.path.join(os.getcwd(), 'data', 'summary'),
		os.path.join(os.getcwd(), 'data', 'screen_results'),
	]
	for dir_ in dir_list:
		if not os.path.exists(dir_):
			os.makedirs(dir_)


def save_df(df, dir_, filename):
	csv_path = os.path.join(dir_, filename+'.csv')
	df.to_csv(csv_path, index=False)


def read_df(dir_, filename):
	csv_path = os.path.join(os.getcwd(), 'data', filename+'.csv')
	df = pd.read_csv(csv_path)
	return df


def filter_by_market_cap(df, threshold=1000):
	df["Marcap"] = df["Marcap"].astype(int) // 100000000
	condition = (df["Marcap"] >= threshold)
	df = df[condition]
	return df


def clean_stock_list(df):
	# 보통주만 선택
	df["Code"] = df["Code"].astype(str).str.zfill(6)
	df = df[df["Code"].str.endswith("0")].reset_index(drop=True)

	# SPAC | 관리종목 제거
	mask = ~df["Dept"].fillna("").str.contains(r"(SPAC|관리종목)", case=False)
	df = df[mask].reset_index(drop=True)
	return df
