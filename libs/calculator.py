import numpy as np


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

