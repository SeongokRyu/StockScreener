import os
import time
import datetime
import argparse
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from tabulate import tabulate

from libs.calculator import get_ratio
from libs.calculator import get_growth

from libs.utils import filter_by_market_cap
from libs.utils import create_directories


def summarize_per_stock(
		df,
		price,
	):

	fy_per = get_ratio(df, row_idx=18, column_idx=4, price=price)
	fy_pbr = get_ratio(df, row_idx=19, column_idx=4, price=price)
	fy_roe = df.iloc[17].iloc[4]
	if not np.isnan(fy_roe):
		fy_roe = round(float(fy_roe), 2)

	fy_sales_growth = get_growth(df, row_idx=0, column_idx1=3, column_idx2=4)
	fy_op_growth = get_growth(df, row_idx=1, column_idx1=3, column_idx2=4)
	fy_net_growth = get_growth(df, row_idx=3, column_idx1=3, column_idx2=4)

	eps = df.iloc[18].iloc[3]
	dps = df.iloc[20].iloc[3]

	div_yield = np.nan
	if not np.isnan(dps):
		div_yield = (float(dps) / price) * 100.0
		div_yield = round(div_yield, 2)

	div_payout = np.nan
	if not np.isnan(eps) and not np.isnan(dps):
		div_payout = (float(dps) / float(eps)) * 100.0
		div_payout = round(div_payout, 2)

	results = [
		fy_per, fy_pbr, fy_roe, 
		fy_sales_growth, fy_op_growth, fy_net_growth,
		div_yield, div_payout,
	]
	return results


def create_summary(
		df_stocks,
		df_price,
		date,
	):
	'''
	Results: [
		Forward Year: PER, PBR, ROE, Sales Growth, OpIncome Growth, NetIncome Growth
		Forward Quarter: Sales Growth, OpIncome Growth, NetIncome Growth
		Previous: Dividend Yield, Dividend Payour Ratio
	]
	'''

	df_stocks["Code"] = df_stocks["Code"].astype(str).str.zfill(6)
	code_list = df_stocks["Code"]
	name_list = df_stocks["Name"]
	marcap_list = df_stocks["Marcap"]
	summary_list = []
	for k in range(len(df_stocks)):
		try:
			code = code_list[k]
			name = name_list[k]
			marcap = int(marcap_list[k])
			price = df_price[code].iloc[0]
			print (code, ", ", name, ": Create summary")

			highlight_path = os.path.join(os.getcwd(), 'data', 'financial_highlight', 'recent', code+'.csv')
			if not os.path.exists(highlight_path):
				print (code, ", ", name, ": Financial highlight does not exist")
				continue
			df_highlight = pd.read_csv(highlight_path)

			summary = [
				date, code, name, marcap, int(price), 
				df_highlight.iloc[0].iloc[3], df_highlight.iloc[1].iloc[3], df_highlight.iloc[2].iloc[3],
				df_highlight.iloc[0].iloc[4], df_highlight.iloc[1].iloc[4], df_highlight.iloc[2].iloc[4],
			]
			result = summarize_per_stock(
				df=df_highlight, price=price
			)
			summary += result
			summary_list.append(summary)
		except:
			print (code, ", ", name, ": Error occured when executing summary")

	columns = [
		'Date', 'Code', 'Name', 'MarketCap', 'Price',
		'Sales (2024)', 'OpIncome (2024)', 'NetIncome (2024)',
		'Sales (2025)', 'OpIncome (2025)', 'NetIncome (2025)',
		'FY-PER', 'FY-PBR', 'FY-ROE',
		'FY-SalesGrowth', 'FY-OpGrowth', 'FY-NetGrowth',
		'DivYield', 'DivPayout',
	]
	df_summary = pd.DataFrame(summary_list, columns=columns)

	df_summary = df_summary.dropna(subset=['FY-PER', 'FY-PBR'])
	summary_path = os.path.join(os.getcwd(), 'data', 'summary', date+'.csv')
	df_summary.to_csv(summary_path, index=False)
	print (tabulate(df_summary, headers='keys', showindex=True))
	return df_summary


def screen_summary(df):
	return 


def main(args):
	now = datetime.datetime.now()
	today = '-'.join([
		str(now.year), str(now.month), str(now.day)
	])

	create_directories(date=today)

	stocks_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')
	df_stocks = pd.read_csv(stocks_path)
	df_stocks = filter_by_market_cap(
		df=df_stocks,
		threshold=args.market_cap_threshold
	)

	price_path = os.path.join(os.getcwd(), 'data', 'price', 'recent.csv')
	df_price = pd.read_csv(price_path)

	df_summary = create_summary(
		df_stocks=df_stocks,
		df_price=df_price,
		date=today,
	)	

	screen_summary(
		df=df_summary,
	)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--update_list", action="store_true")
	parser.add_argument("--update_price", action="store_true")
	parser.add_argument("--update_highlight", action="store_true")

	parser.add_argument("--market_cap_threshold", type=int, default=500)
	args = parser.parse_args()

	main(args)
