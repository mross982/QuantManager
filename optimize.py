import numpy as np
import pandas as pd
import DataAccess as da
import sys
import portfolioopt as pfopt
import matplotlib.pyplot as plt
import cvxopt as opt
from cvxopt import blas, solvers
import itertools
import os
import json


class scope(object):
	TIMESERIES = {'3_months': 63, '6_months': 126, '1_year': 252, '3_years': 756}

class portfolio_optimizer(object):
	'''
	
	'''

	def main(self):

		# Use N the same way it is used in the rsi calculator, to loop over larger segments of the data i.e. 3 months
		# 6 months, 1 year, etc. all while passing the same dataframe.

		ls_acctdata = da.DataAccess.get_info_from_account(self)
		if len(ls_acctdata) > 1: # If there are multiple accounts being pulled from this data source,
			for acct in ls_acctdata: # First, optimize each account individually

				filename = acct[0] + '-' + da.DataItem.ADJUSTED_CLOSE + '.pkl'
				filename = filename.replace(' ', '')
				filepath = os.path.join(self.datafolder, filename)				

				df_data = da.DataAccess.get_dataframe(filepath, clean=True)
				outfile = os.path.join(self.datafolder, acct[0] + '_optimize.json')
				portfolio_optimizer.opt(df_data, outfile)

			df_data = da.DataAccess.get_combined_dataframe(self, clean=True) # then optimize all accounts together
			outfile = os.path.join(self.datafolder, 'Combined_optimize.json')
			portfolio_optimizer.opt(df_data, outfile)
		else:

			filename = ls_acctdata[0] + '-' + da.DataItem.ADJUSTED_CLOSE + '.pkl'
			filename = filename.replace(' ', '')
			filepath = os.path.join(self.datafolder, filename)			

			df_data = da.DataAccess.get_dataframe(filepath, clean=True)
			file = os.path.join(self.datafolder, acct[0] + '_optimize.json')
			portfolio_optimizer.opt(df_data, outfile)


	def opt(df_data, file):
		time_series = scope.TIMESERIES
		jsondata = []
		for k,v in time_series.items():
			df_data = df_data[v:]

			returns = df_data.pct_change()
			cov_mat = returns.cov()
			avg_rets = returns.mean()

			
			#***************** Minimum variance portfolio ***********************
			title = 'Minimum_variance_portfolio_%s' % k # the key is the time period i.e. 3_months
			weights = pfopt.min_var_portfolio(cov_mat)
			weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights		
			weights = weights[weights!=0]
			weights = weights.round(decimals=4)
			ret = (weights * avg_rets).sum()
			ret = ret.round(decimals=4)
			std = (weights * returns).sum(1).std()
			std = std.round(decimals=4)
			sharpe = ret / std
			sharpe = sharpe.round(decimals=4)

			w = dict(weights)
			opt = dict()
			
			opt['portfolio'] = w
			opt['title'] = title
			opt['expectedreturn'] = ret
			opt['std'] = std
			opt['sharpe'] = sharpe
			jsondata.append(opt)

			
			#********* Markowitz Portfolio with target return ************************
			target_ret = avg_rets.quantile(0.7)
			title = 'Markowitz_portfolio_target_return:%s_%s' % (round(target_ret, 4), k)
			weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret)
			weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
			weights = weights[weights!=0]
			weights = weights.round(decimals=4)
			ret = (weights * avg_rets).sum()
			ret = ret.round(decimals=4)
			std = (weights * returns).sum(1).std()
			std = std.round(decimals=4)
			sharpe = ret / std
			sharpe = sharpe.round(decimals=4)

			w = dict(weights)
			opt = dict()
			
			opt['portfolio'] = w
			opt['title'] = title
			opt['expectedreturn'] = ret
			opt['std'] = std
			opt['sharpe'] = sharpe
			jsondata.append(opt)
			
		
			#***************** Tangency Portfolio *******************************
			title = 'Tangency_portfolio_%s' % k
			weights = pfopt.tangency_portfolio(cov_mat, avg_rets)
			weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
			weights = weights[weights!=0]
			weights = weights.round(decimals=4)
			ret = (weights * avg_rets).sum()
			ret = ret.round(decimals=4)
			std = (weights * returns).sum(1).std()
			std = std.round(decimals=4)
			sharpe = ret / std
			sharpe = sharpe.round(decimals=4)
			
			w = dict(weights)
			opt = dict()
			
			opt['portfolio'] = w
			opt['title'] = title
			opt['expectedreturn'] = ret
			opt['std'] = std
			opt['sharpe'] = sharpe
			jsondata.append(opt)
			
			with open(file, 'w') as f:
				json.dump(jsondata, f)
				

	