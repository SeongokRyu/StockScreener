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

from libs.update import update_price

from libs.calculator import calc_price_change

from libs.utils import filter_by_market_cap
from libs.utils import get_code_list
from libs.utils import SECTOR_LIST


def change_analysis_by_sector(
		df_sector,
		df_change,
		date,
		interval,
	):
	sector_list = SECTOR_LIST
	code_list = get_code_list(df_sector)
	df_change = df_change[['Date',]+code_list]
	change_list = list(df_change.iloc[-1])[1:]

	df_sector['Change'] = change_list
	contents = []
	for sector in sector_list:
		condition = (df_sector['Sector'] == sector)
		df_ = df_sector[condition]

		if len(df_) > 0:
			change_list = list(df_['Change'])
			val_to_sum = [val for val in change_list if not np.isnan(val)]
			mean_change = sum(val_to_sum) / len(val_to_sum)
			mean_change = round(float(mean_change), 2)
			
			num_pos = sum(value >= 0.0 for value in change_list)
			num_neg = len(change_list) - num_pos
			ratio = round(float(num_pos) / len(change_list) * 100.0, 2)

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


def show_stocks_in_sector(df_analysis):


def main(args):
	now = datetime.datetime.now()
	before = '-'.join([
		str(now.year-1), str(now.month-1), str(now.day)
	])
	today = '-'.join([
		str(now.year), str(now.month), str(now.day)
	])

	sector_path = os.path.join(os.getcwd(), 'data', 'stocks_sector.csv')
	df_sector = pd.read_csv(sector_path)

	df_sector = filter_by_market_cap(
		df=df_sector, threshold=args.market_cap_threshold
	)

	if args.update_price:
		print ("Update price -- Start")
		st = time.time()
		update_price(
			df=df_sector,
			date=today,
			before=before
		)
		et = time.time()
		print (round(et-st, 2), "(s)")

	price_path = os.path.join(os.getcwd(), 'data', 'price', 'recent.csv')
	df_price = pd.read_csv(price_path)

	interval_dict = {
		'daily': 1,
		'weekly': 5,
		'monthly': 20,
		'yearly': 240,
	}
	for key in interval_dict.keys():
		interval = interval_dict[key]
		df_change = calc_price_change(df=df_price, interval=interval)
		df_analysis = change_analysis_by_sector(
			df_sector=df_sector, 
			df_change=df_change, 
			date=today,
			interval=key,
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
		print (key)
		print (tabulate(df_analysis, headers='keys', showindex=True))

		tabulate_stocks_in_sector()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--update_price", action="store_true")

	parser.add_argument("--market_cap_threshold", type=int, default=500)
	parser.add_argument("--sleep_interval", type=float, default=0.5)
	args = parser.parse_args()

	main(args)
