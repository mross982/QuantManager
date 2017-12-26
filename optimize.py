import numpy as np
import pandas as pd
import DataAccess as da
import DataUtil as du
import sys
import portfolioopt as pfopt
import matplotlib.pyplot as plt
import cvxopt as opt
from cvxopt import blas, solvers
import itertools
import os
import json
from pprint import pprint
import collections
import math


class scope(object):

	TIMESERIES = [('6_months', 126), ('1_year', 252), ('all_years', 'nan')]

class normalize(object):

	ANNUALIZE = 252

class portfolio_optimizer(object):

	def main(self):
		'''
		@summary: start function to optimize a portfolio. takes a data object and returns a json file of the optimized data

		'''
		print('Optimizing portfolio')
		ls_acctdata = da.DataAccess.get_info_from_account(self)
		
		if len(ls_acctdata) > 1: # seperate data objects with multiple accounts to also create a combined optimization
			combofile = True
		else:
			combofile = False
		
		for acct in ls_acctdata: # First, optimize each account individually

			filename = acct[0] + '-' + da.DataItem.ADJUSTED_CLOSE + '.pkl' # from account in the ls_acct data
			filename = filename.replace(' ', '')
			filepath = os.path.join(self.datafolder, filename)				
			df_data = da.DataAccess.get_dataframe(filepath, clean=True) # get all close data in a dataframe
			outfilename = acct[0] + '_optimized'
			outfilepath = os.path.join(self.datafolder, outfilename)
			portfolio_optimizer.main_opt(df_data, acct[0], outfilepath)

		if combofile == True:
			outfilename = 'combined_optimized'
			outfilepath = os.path.join(self.datafolder, outfilename)
			df_data = da.DataAccess.get_combined_dataframe(self, clean=True) # then optimize all accounts together
			acct = 'combined'
			portfolio_optimizer.main_opt(df_data, acct, outfilepath)

	def main_opt(df_data, acct, filepath):
		df = pd.DataFrame()
		all_days = len(df_data)
		if all_days >= 252:
			annualize = normalize.ANNUALIZE
		else:
			annualize = all_days

		timeseries = collections.OrderedDict(scope.TIMESERIES)

		for k, v in timeseries.items():
			data = df_data.copy()
			if k != 'all_years': # 'all years' data is passed as is
				seg_data = data.iloc[-v:] # slice the data into the timeframes described in scope.TIMESERIES
			else:
				v = all_days # when all years is selected, sets the v to len(df_data)
				seg_data = df_data # create a new variable to match the variable created when sliced.

			returns = du.returnize0(seg_data) # get daily returns from dataframe
			seg_data = df_data # reset the seg_data variable to the original full df_data
			avg_rets = returns.mean() # get mean of all daily returns
			target_ret = round(avg_rets.quantile(0.7), 4)  # get the target return
			weights, exp_return, std_dev = portfolio_optimizer.target_opt( returns, target_ret ) # optimize

			# convert returns & risk into an annual timeframe if greater than 1 year of data.
			port_exp_return = exp_return * annualize
			port_std_dev = std_dev * math.sqrt(annualize)
			port_target_ret = target_ret * annualize
				
			port_sharpe = exp_return / std_dev 

			ls_bool = avg_rets.index.isin(weights.index) # returns a list of boolean values where it matches symbols in weights.index
			 # filters the average return series by the boolean values,
			# annualizes the values, then returns a series of just the optimized symbols.		
			
			indv_std = returns.std() # returns a series of the std dev of each fund.
			# ls_bool = indv_std.index.isin(Data['Symbols']) # the bool is always in the same order

			indv_ret = avg_rets[ls_bool] * annualize
			indv_std = indv_std[ls_bool] * math.sqrt(annualize) # filters the std dev seriese by the bool values, annualizes
			# these values, then returns a series of just the optimized symbols

			for x in range(len(weights)):
				df = df.append({'Symbols':weights.index[x], 'Weights':weights.values[x],
					'Exp_Return': indv_ret.values[x], 'Std_Deviation': indv_std.values[x], 
					'Sharpe': indv_ret.values[x]/indv_std.values[x]}, ignore_index=True)
			
			title = '%s_%s_target_opt' % (acct, k)
			df_newrow = {'Symbols': title, 'Weights': 1.0, 'Exp_Return': port_exp_return, 
				'Std_Deviation': port_std_dev, 'Sharpe': port_sharpe}

			cols = ['Symbols', 'Weights', 'Exp_Return', 'Std_Deviation', "Sharpe"]
			df = df[cols]

			df = df.append(df_newrow, ignore_index=True)
			
		df.to_pickle(filepath + '.pkl')
		# df.to_csv(filepath + '.csv')


	def target_opt(df_daily_returns, target_ret=None):
		#********* Markowitz Portfolio with target return ************************
		cov_mat = df_daily_returns.cov()
		avg_rets = df_daily_returns.mean()

		if target_ret == None:
			target_ret = avg_rets.quantile(0.7)

		weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret) # returns a df series of weights
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
		weights = weights[weights!=0] # remove any weights of 0
		weights = weights.round(decimals=4) # clean up weight values by rounding

		ret = (weights * avg_rets).sum() # float of the portfolio average daily return

		# p = np.asmatrix(avg_rets) # this is where the error is occurring
		# w = np.asmatrix(weights)
		# C = np.asmatrix(np.cov(df_daily_returns))
		# sigma = np.sqrt(w * C * w.T)  #standard deviation
		#***********************************************************************************************
		# C is covariance matrix of the returns NOTE: if it used the simple std dev std(array(ret_vec).T*w)
		# the result would be slightly different as it would not take covariances into account.!

		std = (weights * df_daily_returns).sum(1).std() # float of the portfolio standard deviation

		return weights, ret, std


	def tangency_opt(df_daily_returns):

		cov_mat = df_daily_returns.cov()
		avg_rets = df_daily_returns.mean()
		
		weights = pfopt.tangency_portfolio(cov_mat, avg_rets)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
		weights = weights[weights!=0]
		weights = weights.round(decimals=4)
		ret = (weights * avg_rets).sum()
		ret = ret.round(decimals=4)
		std = (weights * df_daily_returns).sum(1).std()
		std = std.round(decimals=4)

		return weights, ret, std
		

	def min_variance(df_daily_returns):
		#***************** Minimum variance portfolio ***********************
		
		cov_mat = df_daily_returns.cov()
		avg_rets = df_daily_returns.mean()

		weights = pfopt.min_var_portfolio(cov_mat)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights		
		weights = weights[weights!=0]
		weights = weights.round(decimals=4)
		ret = (weights * avg_rets).sum()
		ret = ret.round(decimals=4)
		std = (weights * df_daily_returns).sum(1).std()
		std = std.round(decimals=4)

		return weights, ret, std