import os

import pandas as pd

SECTOR_LIST = [
	'IT하드웨어/반도체', 
	'반도체 소재',
	'반도체 장비',
	'디스플레이'
	'디스플레이 소재'
	'디스플레이 장비'
	'이차전지',
	'이차전지 소재',
	'이차전지 장비',
	'IT소프트웨어',
	'AI',
	'게임',
	'통신',
	'바이오/헬스케어',
	'금융',
	'자동차',
	'자동차 부품',
	'정유/화학/가스',
	'철강/비철금속',
	'조선/기계/중공업',
	'운송/항공/물류',
	'건설/건자재',
	'필수소비재',
	'유통/소매',
	'의류',
	'화장품',
	'미용기기',
	'엔터테인먼트',
	'미디어',
	'유틸리티',
	'방위산업',
	'신재생에너지',
	'지주회사',
]

def create_directories(date):
	dir_list = [
		os.path.join(os.getcwd(), 'data', 'stocks'),
		os.path.join(os.getcwd(), 'data', 'financial_highlight', date),
		os.path.join(os.getcwd(), 'data', 'financial_highlight', 'recent'),
		os.path.join(os.getcwd(), 'data', 'price'),
		os.path.join(os.getcwd(), 'data', 'summary'),
		os.path.join(os.getcwd(), 'data', 'screen_results'),
	]
	for dir_ in dir_list:
		if not os.path.exists(dir_):
			os.makedirs(dir_)


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
