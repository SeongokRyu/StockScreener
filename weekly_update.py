import os
import time
import datetime
import argparse

import numpy as np
import pandas as pd
from tabulate import tabulate

import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False 
import seaborn as sns

from libs.update import canonical_update

from libs.calculator import calc_price_change

from libs.utils import convert_sector_eng_to_kor
from libs.utils import filter_by_market_cap
from libs.utils import get_code_list
from libs.utils import SECTOR_LIST


def change_analysis_by_sector(
		df_stocks,
		df_change,
		date,
		interval,
		use_fics=False,
	):
	sector_list = SECTOR_LIST
	if use_fics:
		sector_list = list(set(df_stocks['Sector']))
	code_list = get_code_list(df_stocks)
	df_change = df_change[['Date',]+code_list]
	change_list = list(df_change.iloc[-1])[1:]

	df_stocks['Change'] = change_list
	contents = []
	for sector in sector_list:
		condition = (df_stocks['Sector'] == sector)
		df_ = df_stocks[condition]

		if len(df_) > 0:
			change_list = list(df_['Change'])
			val_to_sum = [val for val in change_list if not np.isnan(val)]
			mean_change = sum(val_to_sum) / len(val_to_sum)
			mean_change = round(float(mean_change), 2)
			
			num_pos = sum(value >= 0.0 for value in change_list)
			num_neg = len(change_list) - num_pos
			ratio = round(float(num_pos) / len(change_list) * 100.0, 2)

			if use_fics:
				sector = convert_sector_eng_to_kor(sector)
			contents.append([sector, ratio, mean_change, num_pos, num_neg])
	
	df_analysis = pd.DataFrame(contents, columns=['Sector', 'Ratio', 'MeanChange', 'NumPos', 'NumNeg'])
	df_analysis = df_analysis.sort_values(by=['Ratio'], ascending=False)
	analysis_path = os.path.join(os.getcwd(), 'data', 'sector_change', date+'_'+interval+'.csv')
	df_analysis.to_csv(analysis_path, index=False)
	return df_analysis


def plot_analysis_by_ratio(
		df,
		date,
		interval,
	):
	df = df.sort_values(by='Ratio', ascending=False)

	plt.figure(figsize=(12, 7))
	ax = sns.barplot(x='Sector', y='Ratio', data=df, palette='RdYlBu')
	ax.axhline(y=50.0, color='black', linestyle='--', linewidth=1.5)

	if interval == 'daily':
		plt.title(date + ' -- 일간 섹터별 상승 종목 비율', fontsize=16)
	elif interval == 'weekly': 
		plt.title(date + ' -- 지난 5거래일 (주간) 섹터별 상승 종목 비율', fontsize=16)
	elif interval == 'monthly': 
		plt.title(date + ' -- 지난 20거래일 (월간) 섹터별 상승 종목 비율', fontsize=16)
	elif interval == 'yearly': 
		plt.title(date + ' -- 지난 240거래일 (연간) 섹터별 상승 종목 비율', fontsize=16)
	plt.ylabel('상승 종목 비율 (%)', fontsize=12)

	plt.ylim(0, 105)
	plt.xticks(rotation=45, ha='right')
	plt.tight_layout()

	fig_path = os.path.join(os.getcwd(), 'data', 'sector_change', date+'_'+interval+'_ratio.png')
	plt.savefig(fig_path)
	return


def plot_analysis_by_change(
		df,
		date,
		interval,
	):
	df = df.sort_values(by='MeanChange', ascending=False)

	plt.figure(figsize=(12, 7))
	ax = sns.barplot(x='Sector', y='MeanChange', data=df, palette='RdYlBu')

	if interval == 'daily':
		plt.title(date + ' -- 일간 섹터별 평균 주가상승률', fontsize=16)
	elif interval == 'weekly': 
		plt.title(date + ' -- 지난 5거래일 (주간) 섹터별 평균 주가상승률', fontsize=16)
	elif interval == 'monthly': 
		plt.title(date + ' -- 지난 20거래일 (월간) 섹터별 평균 주가상승률', fontsize=16)
	elif interval == 'yearly': 
		plt.title(date + ' -- 지난 240거래일 (연간) 섹터별 평균 주가상승률', fontsize=16)
	plt.ylabel('평균 주가상승률 (%)', fontsize=12)

	#plt.ylim(0, 105)
	plt.xticks(rotation=45, ha='right')
	plt.tight_layout()

	fig_path = os.path.join(os.getcwd(), 'data', 'sector_change', date+'_'+interval+'_change.png')
	plt.savefig(fig_path)
	return


def tabulate_stocks_in_specific_sector(
		df_stocks,
		sector,
		max_num_stocks,
	):
	condition = (df_stocks['Sector'] == sector)
	df_ = df_stocks[condition]
	df_['Sector'] = [sector for _ in range(len(df_))]

	if len(df_) == 0:
		return

	columns = [
		'Name',
		'Sector',
		'Change',
		'Amount',
		'Marcap',
	]
	df_ = df_.sort_values(by=['Change'], ascending=False)
	df_ = df_[columns]
	df_["Amount"] = df_["Amount"].astype(int) // 100000000
	df_["Marcap"] = df_["Marcap"].astype(int) // 100000000
	df_ = df_[:max_num_stocks]

	rename_dict = {
		'Name': '종목',
		'Sector': '섹터',
		'Change': '등락율 (%)',
		'Amount': '거래대금 (억 원)',
		'Marcap': '시가총액 (억 원)',
	}
	df_ = df_.rename(columns=rename_dict)
	print ("")
	print (tabulate(df_, headers='keys', showindex=True))


def edit_(
		df_stocks,
		df_price,
	):
	code_stocks = get_code_list(df_stocks)
	df_stocks['Code'] = code_stocks
	code_price = list(df_price.columns)[1:]
	code_common = list(set(code_stocks) & set(code_price))

	condition = (df_stocks['Code'].isin(code_common))
	#df_stocks = df_stocks[condition].sort_values(by=['Code']).reset_index()
	df_stocks = df_stocks[condition].sort_values(by=['Code'])

	code_common = list(df_stocks['Code'])
	df_price = df_price[['Date',] + code_common]
	return df_stocks, df_price


def main(args):
	now = datetime.datetime.now()
	before = '-'.join([str(now.year-1), str(now.month-1), str(now.day)])
	today = '-'.join([str(now.year), str(now.month), str(now.day)])

	if args.update_list or args.update_price or args.update_highlight:
		canonical_update(
			before=before,
			today=today,
			update_list=args.update_list,
			update_price=args.update_price,
			update_highlight=args.update_highlight,
			market_cap_threshold=args.market_cap_threshold,
			sleep_interval=args.sleep_interval,
		)

	stocks_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')
	if args.use_fics:
		stocks_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_fics.csv')
	df_stocks = pd.read_csv(stocks_path)
	df_stocks = filter_by_market_cap(
		df=df_stocks, 
		threshold=args.market_cap_threshold,
		divide=False,
	)

	price_path = os.path.join(os.getcwd(), 'data', 'price', 'recent.csv')
	df_price = pd.read_csv(price_path)


	df_stocks, df_price = edit_(
		df_stocks=df_stocks,
		df_price=df_price,
	)

	interval_dict = {
		'daily': 1,
		'weekly': 5,
		'monthly': 20,
		#'yearly': 240,
	}
	for key in interval_dict.keys():
		interval = interval_dict[key]
		df_change = calc_price_change(df=df_price, interval=interval)
		df_analysis = change_analysis_by_sector(
			df_stocks=df_stocks, 
			df_change=df_change, 
			date=today,
			interval=key,
			use_fics=args.use_fics,
		)

		plot_analysis_by_ratio(
			df=df_analysis,
			date=today,
			interval=key,
		)
		plot_analysis_by_change(
			df=df_analysis,
			date=today,
			interval=key,
		)
		print (key.upper())
		print (tabulate(df_analysis, headers='keys', showindex=True))

	
		if key == 'weekly':
			df_analysis = df_analysis.sort_values(by=['MeanChange'], ascending=False)
			for k in range(args.num_sectors):
				sector = df_analysis.iloc[k]['Sector']
				tabulate_stocks_in_specific_sector(
					df_stocks=df_stocks,
					sector=sector,
					max_num_stocks=args.max_num_stocks,
				)

	#for sector in list(set(df_stocks['Sector'])):
	#	print (sector)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
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
