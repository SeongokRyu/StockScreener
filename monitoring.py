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


def main(args):
	save_dir = os.path.join(os.getcwd(), 'data', 'macd')
	if not os.path.exists(save_dir):
		os.makedirs(save_dir)

	stocks_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')
	df_stocks = pd.read_csv(stocks_path)

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

	date_list = list(df_price['Date'])
	price_list = df_price[args.code_]
	macd_df = calculate_macd_indicators(
		date_list=date_list,
		price_list=price_list, 
		short_window=12, 
		long_window=26, 
		signal_window=9
	)
	macd_df['Prev_MACD'] = macd_df['MACD'].shift(1)
	macd_df['Prev_Histogram'] = macd_df['Histogram'].shift(1)

	example_macd_thresh = (macd_df['Price'].mean() * args.macd_threshold) if not macd_df['Price'].empty else 0.05 # 예시: 평균 주가의 0.1%
	example_hist_thresh = (macd_df['Price'].mean() * args.hist_threshold) if not macd_df['Price'].empty else 0.01 # 예시: 평균 주가의 0.05%

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
	csv_path = os.path.join(save_dir, args.code_+'.csv',)
	macd_df.to_csv(csv_path, index=False)

	print (tabulate(macd_df[-120:], headers='keys', showindex=True))


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--code_", type=str, default=None)
	parser.add_argument("--macd_threshold", type=str, default=0.001)
	parser.add_argument("--hist_threshold", type=str, default=0.0001)
	args = parser.parse_args()

	main(args)
