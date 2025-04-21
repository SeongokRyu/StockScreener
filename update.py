import os
import time
import datetime
import argparse
import warnings
warnings.filterwarnings('ignore')

import pandas as pd

import FinanceDataReader as fdr

from libs.scrapper import get_stock_list
from libs.scrapper import fetch_fics_and_highlight

from libs.utils import read_df
from libs.utils import save_df
from libs.utils import create_directories
from libs.utils import clean_stock_list
from libs.utils import filter_by_market_cap


def update_stock_list():
	market_list = ['KOSPI', 'KOSDAQ']
	df_list = [get_stock_list(market) for market in market_list]
	df_market = pd.concat(df_list)

	market_path = os.path.join(os.getcwd(), 'data', 'stocks_all.csv')
	save_df(market_path, index=False)

	df_clean = filter_stock_list(df_market)
	clean_path = os.path.join(os.getcwd(), 'data', 'stocks_clean.csv')
	save_df(clean_path, index=False)


def update_financial_highlight(
		df,
		date,
	):
	df["Code"] = df["Code"].astype(str).str.zfill(6)
	df = df[:5]
	code_list = list(df["Code"])
	name_list = list(df["Name"])
	fics_list = []
	for idx in range(len(df)):
		code = code_list[idx]
		name = name_list[idx]
		try:
			fics, highlight = fetch_fics_and_highlight(code)
			fics_list.append(fics)
			highlight_path = os.path.join(
				os.getcwd(), 'data', 'financial_highlight', date, code+'.csv'
			)
			highlight.to_csv(highlight_path, index=True)
		except:
			fics = ""
			fics_list.append(fics)

		print (code, "\t", name, " -- Financial highlight updated")
		time.sleep(0.3)

	df["FICS"] = fics_list
	save_df(df, "stocks_tmp")


def update_price(
		df,
		date,
	):
	df["Code"] = df["Code"].astype(str).str.zfill(6)
	df = df[:5]
	code_list = list(df["Code"])
	inp = ','.join(code_list)

	df_price = fdr.DataReader(inp, date) 
	df_price.to_csv(os.path.join(
		os.getcwd(), 'data', 'price', date, 'stock_price.csv'
	))


def main(args):
	now = datetime.datetime.now()
	today = '-'.join([
		str(now.year), str(now.month), str(now.day)
	])

	create_directories(date=today)

	if args.update_list:
		update_stock_list()

	clean_path = os.path.join(os.getcwd(), 'data', 'stocks_clean.csv')
	df_stocks = read_df(clean_path)
	df_stocks = filter_by_market_cap(
		df=df_stocks,
		threshold=args.market_cap_threshold
	)

	if args.update_price:
		update_price(
			df=df_stocks, date=today,
		)

	if args.update_highlight:
		update_financial_highlight(
			df=df_stocks, date=today
		)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--update_list", action="store_true")
	parser.add_argument("--update_price", action="store_true")
	parser.add_argument("--update_highlight", action="store_true")

	parser.add_argument("--market_cap_threshold", type=int, default=500)
	args = parser.parse_args()

	main(args)
