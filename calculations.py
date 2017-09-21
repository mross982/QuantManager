import numpy as np
import pandas as pd
import DataAccess as da
import sys

def optimize(df_data):
	
	returns = df_data.pct_change()
	mean_daily_returns = returns.mean()
	cov_matrix = returns.cov()
	print(returns.head())
	'''
	Computes a Markowitz portfolio.

	Parameters
	----------
	cov_mat: pandas.DataFrame
	Covariance matrix of asset returns.
	exp_rets: pandas.Series
	Expected asset returns (often historical returns).
	target_ret: float
	Target return of portfolio.
	allow_short: bool, optional
		If 'False' construct a long-only portfolio.
		If 'True' allow shorting, i.e. negative weights.
	market_neutral: bool, optional
		If 'False' sum of weights equals one.
		If 'True' sum of weights equal zero, i.e. create a
			market neutral portfolio (implies allow_short=True).

	Returns
	-------
	weights: pandas.Series
		Optimal asset weights.
	'''


if __name__ == '__main__':

	if len(sys.argv)>1:
		c_dataobj = da.DataAccess(sys.argv[1])
	else:
		c_dataobj = da.DataAccess(da.DataSource.YAHOO)

	df_data = da.DataAccess.get_dataframe(c_dataobj)
	clean_data = da.DataAccess.clean_data(df_data)
	
	optimize(clean_data)
