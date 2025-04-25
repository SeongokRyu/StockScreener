import numpy as np
import pandas as pd


def calc_price_change(
		df,
		interval
	):
	p1 = np.asarray(df.iloc[-1])[1:]
	if interval > len(df):
		p0 = np.asarray(df.iloc[0])[1:]
	else:
		p0 = np.asarray(df.iloc[-1-interval])[1:]
	change = ((p1 - p0)/p0*100.0)
	
	columns = list(df.columns)
	new = ['Change']
	new += [round(val, 2) for val in change] 
	df_ = pd.DataFrame([new], columns=columns)
	return df_


def get_ratio(
		df,
		row_idx,
		column_idx,
		price,
	):
	value = df.iloc[row_idx].iloc[column_idx]

	if not np.isnan(value):
		ratio = price / value
		ratio = round(ratio, 2)
		return ratio
	else:
		return np.nan


def get_growth(
		df,
		row_idx,
		column_idx1,
		column_idx2,
	):
	value_before = df.iloc[row_idx].iloc[column_idx1]
	value_after = df.iloc[row_idx].iloc[column_idx2]

	if np.isnan(value_before) or np.isnan(value_after):
		return np.nan
	else:
		growth = (value_after - value_before) / value_before * 100.0
		growth = round(growth, 2)
		return growth

