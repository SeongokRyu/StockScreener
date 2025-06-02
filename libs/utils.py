import os

import numpy as np
import pandas as pd


SECTOR_LIST = [
	'IT하드웨어/반도체', '반도체 소재', '반도체 장비', '가전제품',
	'디스플레이 패널', '디스플레이 소재', '디스플레이 장비',
	'이차전지 배터리', '이차전지 소재', '이차전지 장비',
	'IT소프트웨어', 'AI', '게임', '통신',
	'보험', '은행', '증권', '창업투자/VC', '기타금융',
	'자동차', '자동차 부품',
	'정유/화학/가스', '철강/비철금속',
	'조선/기계/중공업', '방위산업', '로봇',
	'신재생에너지', '원자력', '전력기기',
	'운송/항공/물류', '여행', '호텔/카지노',
	'건설', '건자재', '홈리빙/가구',
	'음식료', '유통', '필수소비재', '소매판매', '의류',
	'바이오/제약/신약개발', '헬스케어', '진단기기/의료기기', 
	'화장품', '미용기기', 
	'엔터테인먼트', '미디어',
	'유틸리티',
	'지주회사',
	'기타',
]

def convert_sector_eng_to_kor(sector_eng):
	dict_ = {
		'Education': '교육',
		'Thrifts & Mogage Finance': '저축은행',
		'Software': 'IT소프트웨어',
		'Automobiles': '자동차', 
		'Leisure Equipment & Products': '여행/레저/카지노',
		'Textiles,Apparel': '의류/섬유', 
		'Auto Components': '자동차부품',
		'Real Estate': '부동산',
		'Multiline Retail': '백화점/리테일',
		'Pharmaceuticals': '제약/바이오',
		'Airlines': '항공',
		'Electtronic Equipment & Instruments': '전자/기계 장비',
		'Game Software': '게임/소프트웨어',
		'Machinery': '기계',
		'Beverages': '음료/주류',
		'Consumer Finance': '소매금융',
		'Building Products': '건축자재',
		'Security system equipment': '보안',
		'Personal Products': '화장품/개인소비재',
		'Industrial Conglomerates': '지주회사/복합회사',
		'Commercial Banks': '은행',
		'Metal & Mining': '철강/비철금속',
		'Hotel & Leisure': '호텔/레져',
		'Commercial Services & Supplies': '상업서비스',
		'Internet Retail': '전자상거래',
		'Trading Companies & Distributors': '상사',
		'Containers & Packaging': '포장/패키징',
		'Construction & Engineering': '건설',
		'Display and Display accessory': '디스플레이/장비/부품',
		'Electrical Equipment': '전력기기/전선',
		'Insurance': '보험',
		'Marine': '해운',
		'Transportation Infrastructure': '운송인프라',
		'Health Care Equipment & Supplies': '헬스케어',
		'IT Services': 'IT서비스',
		'Shipbuilding': '조선',
		'Capital Markets': '증권',
		'Construction Materials': '건자재',
		'Paper & Forest Products': '종이/목재',
		'Household Products': '가정용품',
		'Diversified Financial Services': '기타금융',
		'Internet Services': 'IT미디어',
		'Media': '미디어/엔터',
		'Eletric Utilities': '전력기기',
		'Wireless Telecommunication Services': '무선통신',
		'Gas Utility': '가스/유틸리티',
		'Food Products': '음식',
		'Semiconductors & Semiconductor Equipment': '반도체/반도체장비',
		'Chemicals': '화학',
		'Office Electronics': '컴퓨터/주변기기',
		'Mobile phone and Mobile accessory': '스마트폰/부품',
		'Biotechnology': '바이오텍',
		'Energy Equipment & service': '에너지장비/서비스',
		'Commuications Equipment': '통신장비',
		'Household Durables': '가정용 기기/용품',
		'Oil, Gas & consumable Fuels': '석유와가스',
		'Distributors': '판매/소매업체',
		'Computers & Peripherals': '컴퓨터/주변기기',
		'Tobacco': '담배',
		'Road & Rail': '도로/철도 운송',
	}
	return dict_[sector_eng]


def str2bool(v):
	if v.lower() in ['yes', 'true', 't', 'y', '1']:
		return True
	elif v.lower() in ['no', 'false', 'f', 'n', '0']:
		return False
	else:
		raise argparse.ArgumentTypeError('Boolean value expected')


def get_before_date(
		now,
	):
	before = '-'.join([
		str(now.year-1), str(now.month), str(now.day)
	])
	today = '-'.join([
		str(now.year), str(now.month), str(now.day)
	])

	return before, today


def get_code_list(df):
	df["Code"] = df["Code"].astype(str).str.zfill(6)
	code_list = list(df["Code"])
	return code_list


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


def filter_by_market_cap(df, threshold=1000, divide=True):
	if divide:
		df["Marcap"] = df["Marcap"].astype(int) // 100000000
	else:
		df["Marcap"] = df["Marcap"].astype(int)
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


def edit_stocks_and_price(
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


def add_change_column(
		df_stocks,
		df_change,
		column_name,
	):
	code_list = get_code_list(df_stocks)
	df_change = df_change[['Date',]+code_list]
	change_list = list(df_change.iloc[-1])[1:]

	df_stocks[column_name] = change_list
	return df_stocks
