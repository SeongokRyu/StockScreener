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

from libs.utils import create_directories
from libs.utils import clean_stock_list
from libs.utils import filter_by_market_cap


def update_stock_list(date):
	market_list = ['KOSPI', 'KOSDAQ']
	df_list = [get_stock_list(market) for market in market_list]
	df_market = pd.concat(df_list)

	market_path = os.path.join(os.getcwd(), 'data', 'stocks', date+'_all.csv')
	df_market.to_csv(market_path, index=False)
	market_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_all.csv')
	df_market.to_csv(market_path, index=False)

	df_clean = filter_stock_list(df_market)
	clean_path = os.path.join(os.getcwd(), 'data', 'stocks', date+'_clean.csv')
	df_clean.to_csv(clean_path, index=False)
	clean_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')
	df_clean.to_csv(clean_path, index=False)


def update_financial_highlight(
		df,
		date,
		interval=0.5,
	):
	df["Code"] = df["Code"].astype(str).str.zfill(6)
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
			highlight_path = os.path.join(
				os.getcwd(), 'data', 'financial_highlight', 'recent', code+'.csv'
			)
			highlight.to_csv(highlight_path, index=True)
		except:
			fics = ""
			fics_list.append(fics)

		print (code, "\t", name, " -- Financial highlight updated")
		time.sleep(interval)

	df["FICS"] = fics_list
	fics_path = os.path.join(os.getcwd(), 'data', 'stocks', date+'_fics.csv')
	df.to_csv(fics_path, index=False)
	fics_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_fics.csv')
	df.to_csv(fics_path, index=False)


def update_price(
		df,
		date,
	):
	df["Code"] = df["Code"].astype(str).str.zfill(6)
	code_list = list(df["Code"])
	inp = ','.join(code_list)

	df_price = fdr.DataReader(inp, date) 
	price_path = os.path.join(os.getcwd(), 'data', 'price', date+'.csv')
	df_price.to_csv(price_path)
	price_path = os.path.join(os.getcwd(), 'data', 'price', 'recent.csv')
	df_price.to_csv(price_path)


def main(args):
	now = datetime.datetime.now()
	today = '-'.join([
		str(now.year), str(now.month), str(now.day)
	])

	create_directories(date=today)

	if args.update_list:
		update_stock_list(today)

	clean_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')
	df_stocks = pd.read_csv(clean_path)
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
			df=df_stocks, date=today, interval=args.sleep_interval,
		)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--update_list", action="store_true")
	parser.add_argument("--update_price", action="store_true")
	parser.add_argument("--update_highlight", action="store_true")

	parser.add_argument("--market_cap_threshold", type=int, default=500)
	parser.add_argument("--sleep_interval", type=float, default=0.5)
	args = parser.parse_args()

	main(args)
