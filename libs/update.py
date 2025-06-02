import os
import time
import datetime
import argparse
import warnings
warnings.filterwarnings('ignore')

import pandas as pd

import FinanceDataReader as fdr

from libs.scrapper import crawling_stock_list
from libs.scrapper import fetch_fics_and_highlight

from libs.utils import create_directories
from libs.utils import clean_stock_list
from libs.utils import filter_by_market_cap
from libs.utils import get_code_list


def get_stock_list(date):
	market_list = ['KOSPI', 'KOSDAQ']
	df_list = [crawling_stock_list(market) for market in market_list]
	df_market = pd.concat(df_list)

	market_path = os.path.join(os.getcwd(), 'data', 'stocks', date+'_all.csv')
	df_market.to_csv(market_path, index=False)
	market_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_all.csv')
	df_market.to_csv(market_path, index=False)

	df_clean = clean_stock_list(df_market)
	clean_path = os.path.join(os.getcwd(), 'data', 'stocks', date+'_clean.csv')
	df_clean.to_csv(clean_path, index=False)
	clean_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')
	df_clean.to_csv(clean_path, index=False)
	

def get_price(
		df,
		today,
		before=None
	):
	df["Code"] = df["Code"].astype(str).str.zfill(6)
	code_list = list(df["Code"])
	inp = ','.join(code_list)

	df_price = None
	if before is None:
		df_price = fdr.DataReader(inp, today) 
	else:
		df_price = fdr.DataReader(inp, before, today) 

	price_path = os.path.join(os.getcwd(), 'data', 'price', today+'.csv')
	df_price.to_csv(price_path)
	price_path = os.path.join(os.getcwd(), 'data', 'price', 'recent.csv')
	df_price.to_csv(price_path)


def get_financial_highlight(
		df,
		today,
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
				os.getcwd(), 'data', 'financial_highlight', today, code+'.csv'
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
	fics_path = os.path.join(os.getcwd(), 'data', 'stocks', today+'_fics.csv')
	df.to_csv(fics_path, index=False)
	fics_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_fics.csv')
	df.to_csv(fics_path, index=False)


def add_sector_column(df_stocks):
	sector_path = os.path.join(os.getcwd(), 'data', 'stocks_sector.csv')
	df_sector = pd.read_csv(sector_path)

	code_stocks = get_code_list(df_stocks)
	code_sector = get_code_list(df_sector)
	code_merged = list(set(code_stocks) & set(code_sector))

	df_stocks['Code'] = code_stocks
	df_sector['Code'] = code_sector

	columns = [
		'Code', 'ISU_CD', 'Name', 'Market', 'Dept', 
		'Close', 'ChangeCode', 'Changes', 'ChagesRatio', 
		'Open', 'High', 'Low', 'Volume', 
		'Amount', 'Marcap', 
		'Stocks', 'MarketId',
	]
	df_stocks = df_stocks[columns]

	df_stocks = df_stocks[df_stocks['Code'].isin(code_merged)].sort_values(by=['Code']).reset_index()
	df_sector = df_sector[df_sector['Code'].isin(code_merged)].sort_values(by=['Code']).reset_index()

	df_stocks = df_stocks[columns]
	sector_list = df_sector['Sector']
	df_stocks['Sector'] = sector_list
	return df_stocks


def canonical_update(
		today,
		before,
		update_list,
		update_price,
		update_highlight,
		market_cap_threshold=500,
		sleep_interval=0.5,
	):
	create_directories(date=today)

	if update_list:
		st = time.time()
		print ("Update:: StockList -- Codes, Names, Market Cap, ...")
		get_stock_list(today)
		et = time.time()
		print ("Update:: StockList -- Time spent:", round(et-st, 2), "(s)")
		

	clean_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')
	df_stocks = pd.read_csv(clean_path)
	print (df_stocks)
	df_stocks = add_sector_column(df_stocks=df_stocks)
	df_stocks.to_csv(clean_path, index=False)

	if market_cap_threshold > 0:
		df_stocks = filter_by_market_cap(
			df=df_stocks,
			threshold=market_cap_threshold
		)

	if update_price:
		print ("Update:: Price from", before, "to", today)
		st = time.time()
		get_price(
			df=df_stocks, before=before, today=today,
		)
		et = time.time()
		print ("Update:: Price -- Time spent:", round(et-st, 2), "(s)")

	if update_highlight:
		print ("Update:: Financial highlight")
		st = time.time()
		get_financial_highlight(
			df=df_stocks, today=today, interval=sleep_interval,
		)
		et = time.time()
		print ("Update:: Financial highlight -- Time spent:", round(et-st, 2), "(s)")


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--update_list", action="store_true")
	parser.add_argument("--update_price", action="store_true")
	parser.add_argument("--update_highlight", action="store_true")

	parser.add_argument("--market_cap_threshold", type=int, default=500)
	parser.add_argument("--sleep_interval", type=float, default=0.5)
	args = parser.parse_args()

	now = datetime.datetime.now()
	before = '-'.join([str(now.year), str(now.month-1), str(now.day)])
	today = '-'.join([str(now.year), str(now.month), str(now.day)])

	canonical_update(
		before=before,
		today=today,
		update_list=args.update_list,
		update_price=args.update_price,
		update_highlight=args.update_highlight,
		market_cap_threshold=args.market_cap_threshold,
		sleep_interval=args.sleep_interval,
	)
