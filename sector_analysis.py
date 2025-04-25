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

from libs.utils import filter_by_market_cap
from libs.utils import get_code_list
from libs.utils import SECTOR_LIST


def get_price_info(
		df,
		code_list,
		name_list,
		marcap_list,
		interval=240,
	):
	df_ = df[-interval:]
	contents = []
	for k, code in enumerate(code_list):
		name = name_list[k]
		marcap = marcap_list[k]
		price_list = list(df[code])
		price_recent = price_list[-1]
		price_max = max(price_list)
		price_min = min(price_list)

		change_from_max = round((price_recent - price_max) / price_max * 100.0, 2)
		change_from_min = round((price_recent - price_min) / price_min * 100.0, 2)

		contents.append([
			code, name, marcap,
			price_max, price_min,
			change_from_max, change_from_min,
		])

	columns = [
		'Code', 'Name', 'Marcap',
		'PriceMax', 'PriceMin', 
		'ChangeFromMax', 'ChangeFromMin'
	]
	df = pd.DataFrame(contents, columns=columns)
	return df


def analysis_by_sector(
		df_sector,
		df_info,
	):
	df_info["Code"] = df_info["Code"].astype(str).str.zfill(6)
	sector_list = SECTOR_LIST
	contents = []
	for sector in sector_list:
		condition = (df_sector['Sector'] == sector)
		df_ = df_sector[condition]
		code_list = get_code_list(df_)

		condition = df_info['Code'].isin(code_list)
		df_sliced = df_info[condition]

		change_from_max = list(df_sliced['ChangeFromMax'])
		tmp_list = [val for val in change_from_max if not np.isnan(val)]
		mean_max = sum(tmp_list) / len(tmp_list)

		change_from_min = list(df_sliced['ChangeFromMin'])
		tmp_list = [val for val in change_from_min if not np.isnan(val)]
		mean_min = sum(tmp_list) / len(tmp_list)

		contents.append([
			sector, mean_max, mean_min
		])
	
	df = pd.DataFrame(contents, columns=['Sector', 'MeanMax', 'MeanMin'])
	df = df.sort_values(by=['MeanMin'], ascending=False)
	print (tabulate(df, headers='keys', showindex=True))

	fig, ax = plt.subplots(figsize=(18, 8)) 

	x = np.arange(len(df))
	width = 0.35 

	rects1 = ax.bar(x - width/2, df['MeanMin'], width, label='52주 최저가 대비 상승률', color='lightcoral')
	rects2 = ax.bar(x + width/2, df['MeanMax'], width, label='52주 최고가 대비 하락률', color='skyblue')

	ax.set_title('섹터별 52주 최저가 대비 상승률 & 52주 최고가 대비 하락률', fontsize=16)
	ax.set_xticks(x) 
	ax.set_xticklabels(df['Sector'], rotation=90, ha='center', fontsize=10) # x축 레이블 설정 및 회전
	ax.legend() 

	ax.yaxis.grid(True, linestyle='--', alpha=0.7)

	fig.tight_layout()
	plt.savefig('tmp.png')


def analysis_by_individual_stocks(
		df,
		method,
		prefix,
		threshold_marcap=5000,
		num_plot=50,
	):
	df["Code"] = df["Code"].astype(str).str.zfill(6)
	condition = (df['Marcap'] > threshold_marcap-1)
	df = df[condition]
	if method == 'largest':
		df = df.sort_values(by=['ChangeFromMin'], ascending=False)[:num_plot]
	if method == 'smallest':
		condition = (df['ChangeFromMin'] < 100.0)
		df = df[condition]
		df = df.sort_values(by=['ChangeFromMax'], ascending=True)[:num_plot]
	print (tabulate(df, headers='keys', showindex=True))

	fig, ax = plt.subplots(figsize=(18, 8)) 

	x = np.arange(len(df))
	width = 0.35 

	rects1 = ax.bar(x - width/2, df['ChangeFromMin'], width, label='52주 최저가 대비 상승률', color='lightcoral')
	rects2 = ax.bar(x + width/2, df['ChangeFromMax'], width, label='52주 최고가 대비 하락률', color='skyblue')

	ax.set_title('종목별 52주 최저가 대비 상승률 & 52주 최고가 대비 하락률', fontsize=16)
	ax.set_xticks(x) 
	ax.set_xticklabels(df['Name'], rotation=90, ha='center', fontsize=10) # x축 레이블 설정 및 회전
	ax.legend() 

	ax.yaxis.grid(True, linestyle='--', alpha=0.7)

	fig.tight_layout()
	plt.savefig(prefix+'.png')


def main(args):
	now = datetime.datetime.now()
	before = '-'.join([
		str(now.year-1), str(now.month), str(now.day)
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

	code_list = get_code_list(df_sector)
	name_list = list(df_sector['Name'])
	marcap_list = list(df_sector['Marcap'])
	df_info = get_price_info(
		df=df_price,
		code_list=code_list,
		name_list=name_list,
		marcap_list=marcap_list,
		interval=240,
	)
	analysis_by_sector(
		df_sector=df_sector,
		df_info=df_info,
	)
	analysis_by_individual_stocks(
		df=df_info,
		method='largest',
		prefix='tmp1',
	)
	analysis_by_individual_stocks(
		df=df_info,
		method='smallest',
		prefix='tmp2',
	)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--update_price", action="store_true")

	parser.add_argument("--market_cap_threshold", type=int, default=500)
	parser.add_argument("--sleep_interval", type=float, default=0.5)
	args = parser.parse_args()

	main(args)
