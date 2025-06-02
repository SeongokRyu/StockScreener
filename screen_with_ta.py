import os
import time
import argparse
import pandas as pd

from tabulate import tabulate

from libs.technical_analysis import calculate_macd_indicators
from libs.technical_analysis import categorize_trend_condition

from libs.calculator import calc_price_change

from libs.utils import add_change_column
from libs.utils import filter_by_market_cap
from libs.utils import get_code_list
from libs.utils import edit_stocks_and_price
from libs.utils import SECTOR_LIST


def screen_with_macd(
		df_stocks,
		df_price,
	):
	screened_results = []
	macd_results = []

	save_dir = os.path.join(os.getcwd(), 'data', 'macd')
	if not os.path.exists(save_dir):
		os.makedirs(save_dir)

	date_list = list(df_price['Date'])
	code_list = list(df_price.columns[1:])
	for code in code_list:
		price_list = df_price[code]
		macd_df = calculate_macd_indicators(
			date_list=date_list,
			price_list=price_list, 
			short_window=12, 
			long_window=26, 
			signal_window=9
		)
		macd_df['Prev_MACD'] = macd_df['MACD'].shift(1)
		macd_df['Prev_Histogram'] = macd_df['Histogram'].shift(1)

		example_macd_thresh = (macd_df['Price'].mean() * 0.001) if not macd_df['Price'].empty else 0.05 # 예시: 평균 주가의 0.1%
		example_hist_thresh = (macd_df['Price'].mean() * 0.0005) if not macd_df['Price'].empty else 0.01 # 예시: 평균 주가의 0.05%

		categories = []
		for i in range(len(macd_df)):
			if pd.isna(macd_df['MACD'].iloc[i]) or \
				pd.isna(macd_df['Prev_MACD'].iloc[i]) or \
				pd.isna(macd_df['Histogram'].iloc[i]) or \
				pd.isna(macd_df['Prev_Histogram'].iloc[i]
			):
				categories.append("N/A")
			else:
				category = categorize_trend_condition(
					macd_df['MACD'].iloc[i],
					macd_df['Prev_MACD'].iloc[i],
					macd_df['Histogram'].iloc[i],
					macd_df['Prev_Histogram'].iloc[i],
					macd_near_zero_thresh=example_macd_thresh,
					hist_near_zero_thresh=example_hist_thresh
				)
				categories.append(category)
		macd_df['Category'] = categories
		csv_path = os.path.join(save_dir, code+'.csv',)
		#macd_df.to_csv()

		category_pass = [
			"1. 상승 추세 / 추세 확대중",
			"2. 상승 추세 / 눌림목",
		]
		if categories[-1] in category_pass:
			screened_results.append(code)
			macd_results.append(categories[-1])

	return screened_results, macd_results
	


def main(args):
	stocks_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')

	df_stocks = pd.read_csv(stocks_path)
	df_stocks = filter_by_market_cap(
		df=df_stocks, 
		threshold=args.market_cap_threshold,
		divide=False,
	)

	price_path = os.path.join(os.getcwd(), 'data', 'price', 'recent.csv')
	df_price = pd.read_csv(price_path)

	df_stocks, df_price = edit_stocks_and_price(
		df_stocks=df_stocks,
		df_price=df_price,
	)

	df_change = calc_price_change(df=df_price, interval=1)
	df_stocks = add_change_column(
		df_stocks=df_stocks,
		df_change=df_change,
		column_name='ChagesRatio',
	)

	st = time.time()
	macd_screen_results, macd_results = screen_with_macd(
		df_stocks=df_stocks,
		df_price=df_price,
	)
	et = time.time()
	print ("Time for screening with MACD:", round(et-st, 2), "(s)")
	print ("Number of screened stocks:", len(macd_screen_results))

	df_stocks["Code"] = df_stocks["Code"].astype(str).str.zfill(6)
	condition = (df_stocks["Code"].isin(macd_screen_results))
	df_stocks = df_stocks[condition]
	
	df_stocks = df_stocks.set_index('Code')
	df_stocks = df_stocks.reindex(macd_screen_results).reset_index()
	df_stocks['MACD'] = macd_results

	sector_list = list(sorted(set(df_stocks['Sector'])))
	columns_to_print = [
		'Sector',
		'Code',
		'Name', 
		'ChagesRatio',
		'Marcap',
		'MACD',
	]

	for sector in sector_list:
		condition = (df_stocks['Sector'] == sector)
		df_ = df_stocks[condition]

		df_ = df_[columns_to_print]
		df_ = df_.sort_values(by=['ChagesRatio'])
		print (tabulate(df_, headers='keys', showindex=True))


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-b", "--before", type=str, default=None)
	parser.add_argument("-t", "--today", type=str, default=None)

	parser.add_argument("--code_", type=str, default=None)
	parser.add_argument("--update_list", action="store_true")
	parser.add_argument("--update_price", action="store_true")
	parser.add_argument("--update_highlight", action="store_true")

	parser.add_argument("--market_cap_threshold", type=int, default=1000)
	parser.add_argument("--sleep_interval", type=float, default=0.5)

	parser.add_argument("--use_fics", action="store_true")

	parser.add_argument("--num_sectors", type=int, default=10)
	parser.add_argument("--max_num_stocks", type=int, default=20)
	args = parser.parse_args()

	main(args)
