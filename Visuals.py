import numpy as np
import pandas as pd
import DataAccess as da
import DataUtil as du
import sys
import portfolioopt as pfopt
import matplotlib.pyplot as plt
from matplotlib import cm
import cvxopt as opt
from cvxopt import blas, solvers
import itertools
import os
import time
import copy


class scope(object):

	TIMESERIES = {'_6_months': 126, '_1_year': 252, '_all_years': 'nan'}

		
def create_plots(self):
	print('creating images')

	ls_acctdata = da.DataAccess.get_info_from_account(self)

	for acct in ls_acctdata:
		acctname = acct[0] # get account name
		filename = acctname + '-' + da.DataItem.ADJUSTED_CLOSE + '.pkl'
		filename = filename.replace(' ', '')
		filepath = os.path.join(self.datafolder, filename) 
		df_data = da.DataAccess.get_dataframe(filepath, clean=True) # get data frame
		out_filepath = self.imagefolder # get out file path

		for k, v in scope.TIMESERIES.items():
			filename_addition = k
			df = df_data.copy()
			if k != '_all_years': # 'all years' data is passed as is
				df = df.iloc[-v:] # slice the data into the timeframes described in scope.TIMESERIES
				efficient_frontier(df, acctname, out_filepath, filename_addition)
			else:
				efficient_frontier(df, acctname, out_filepath, filename_addition)
			
		for k, v in scope.TIMESERIES.items():
			filename_addition = k
			df = df_data.copy()
			if k != '_all_years': # 'all years' data is passed as is
				df = df.iloc[-v:] # slice the data into the timeframes described in scope.TIMESERIES
				returns(self, df, acctname, out_filepath, filename_addition)
			else:
				returns(self, df, acctname, out_filepath, filename_addition)


def returns(self, df_data, acct, out_filepath, filename_addition):
	
	if len(df_data.columns) > 20: # When there are numerous funds in an account, get unique optimized symbols and
		# chart those.
		ls_syms = da.DataAccess.get_opt_syms(self, acct)
		df_data1 = df_data[ls_syms]
		npa = df_data1.values
	else:
		ls_syms = df_data.columns.tolist()
		npa = df_data.values # converts dataframe to numpy array
	
	ls_index = df_data.index.tolist()
	ls_index.insert(0, 'tot_return')
	return_vec = npa/npa[0,:] # Divides each column by the first value in the column (i.e % returns)
	return_vec = return_vec - 1 # normalizes returns to be 0 based.
	tot_returns = npa[-1,:] / npa[0, :] # divide the last value by the first in each column to get total returns
	return_vec = np.insert(return_vec, 0, tot_returns, 0) # insert the total returns at the top of the daily returns	
	df = pd.DataFrame(return_vec, columns=ls_syms, index=ls_index) # convert back to dataframe to retain the return to symbol relationship.
	
	df = df.transpose() # Transpose the dataframe so all total return values are in one column
	
	df = df.sort_values(by=df.columns[0], ascending=False) # sort symbols by largest to smallest total returns
	
	df = df.drop(df.columns[0], axis=1) # drop the total return values from the dataframe.
	df = df.transpose() # reshape to original
	
	ls_syms = df.columns.tolist()
	ls_index = df.index.tolist()

	np_array = df.values

	out_filepath = os.path.join(out_filepath, acct + '_returns' + filename_addition + '.png')
	
	plot_returns(ls_index, ls_syms, np_array, out_filepath)


def plot_returns(ls_index, ls_syms, return_vec, filepath):
	f = plt.figure(num=None, figsize=(12, 6), dpi=80, facecolor='w', edgecolor='k')
	plt.clf()
	plt.plot(ls_index, return_vec)
	plt.legend(ls_syms, loc='upper left')
	plt.ylabel('Adjusted Close')
	plt.xlabel('Date')
	# plt.show()
	f.savefig(filepath)
	plt.close('all')


def efficient_frontier(df_data, acct, out_filepath, filename_addition):
	'''
	
	'''
	df_all = du.get_risk_ret(df_data) # get np arrays of the exp return and st. dev of each fund

	df_eff = du.get_frontier(df_data)
	
	y_arr_d = df_all.iloc[:,0:1].values # all funds expected returns
	x_arr_d = df_all.iloc[:,1:2].values # all funds std deviations

	titles = df_eff.iloc[:,0:1].values # all first column i.e. portfolio names
	y_arr_e = df_eff.iloc[:,1:2].values # efficient expected return
	x_arr_e = df_eff.iloc[:,2:3].values # efficient std deviation

	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.scatter(x_arr_d, y_arr_d, c='b')
	ax1.scatter(x_arr_e, y_arr_e, c='r')
	ax1.plot(x_arr_e, y_arr_e, c='r')

	plt.xlabel('Risk')
	plt.ylabel('Returns')


	for label, x, y in zip(titles, x_arr_e, y_arr_e):
		plt.annotate(label, xy = (x, y), xytext = (20, -20),
			textcoords = 'offset points', ha = 'right', va = 'top',
			bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
			arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

	filepath = os.path.join(out_filepath, acct + '_eff_frontier' + filename_addition + '.png')
	# plt.show()
	plt.savefig(filepath)
	plt.close('all')