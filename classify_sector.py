import os
import time
import argparse

import pandas as pd

from libs.llm import sector_analysis_input
from libs.llm import run_gemini

from libs.utils import SECTOR_LIST


def curate_answer(answer_list):
	contents = []
	for answer in answer_list:
		lines = answer.split('\n')
		for l in lines:
			if '<sep>' in l:
				splitted = l.split('<sep>')
				code = splitted[0].split('-')[-1].strip()
				name = splitted[1].strip()
				sector = splitted[2].strip()
				contents.append([
					code, name, sector
				])
	df = pd.DataFrame(contents, columns=['Code', 'Name', 'Sector'])
	return df


def merge_stocks_and_sector(
		df_stocks,
		df_sector,
	):
	df_stocks["Code"] = df_stocks["Code"].astype(str).str.zfill(6)
	df_sector["Code"] = df_sector["Code"].astype(str).str.zfill(6)

	code_list = list(df_stocks["Code"])
	marcap_list = list(df_stocks["Marcap"])
	
	condition = df_sector['Code'].isin(code_list)
	df_merged = df_sector[condition]
	df_merged["Marcap"] = marcap_list
	return df_merged


def main(args):
	sector_list = SECTOR_LIST
	stocks_path = os.path.join(os.getcwd(), 'data', 'stocks', 'recent_clean.csv')
	df_stocks = pd.read_csv(stocks_path)

	df_stocks["Code"] = df_stocks["Code"].astype(str).str.zfill(6)
	code_list = df_stocks["Code"]
	name_list = df_stocks["Name"]
	inp_list = list(zip(code_list, name_list))

	num_unit = args.num_unit
	num_jobs = len(inp_list) // num_unit
	if len(inp_list) % num_unit > 0:
		num_jobs += 1

	answer_list = []
	for idx in range(num_jobs):
		start = idx * num_unit
		end = (idx+1) * num_unit
		if (idx+1) == num_jobs:
			end = len(inp_list)
		print (start, "~", end)

		gemini_input = sector_analysis_input(
			sector_list=SECTOR_LIST, 
			inp_list=inp_list[start:end],
		)
		answer = run_gemini(
			contents=gemini_input,
			api_key=args.api_key,
		)
		print (answer)
		answer_list.append(answer)
		time.sleep(args.sleep_interval)

	df_sector = curate_answer(answer_list)

	df_merged = merge_stocks_and_sector(
		df_stocks=df_stocks,
		df_sector=df_sector,
	)

	sector_path = os.path.join(os.getcwd(), 'data', 'stocks_sector.csv')
	df_merged.to_csv(sector_path, index=False)
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--api_key", type=str, required=True)

	parser.add_argument("--update_list", action="store_true")

	parser.add_argument("--market_cap_threshold", type=int, default=500)
	parser.add_argument("--num_unit", type=int, default=50)
	parser.add_argument("--sleep_interval", type=float, default=1.0)
	args = parser.parse_args()

	main(args)
