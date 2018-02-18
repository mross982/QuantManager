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
import string



class sp500(object):

	index = {'sp500_market': ['Market', 'Equally Weighted Market'], 'sp500_sectors': ['Market', 'Consumer Discretionary',
	'Consumer Staples', 'Energy', 'Financials', 'Health Care', 'Industrials', 'Materials', 'Real Estate', 'Technology', 'Utilities'],
	'sp500_Caps': ['Large Cap', 'Mid Cap', 'Small Cap'], 'sp500_style': ['Growth', 'Value'], 'sp500_volitility': ['Volitility Index']}

	# crypto = {'Coins_Tokens': ['']}


def get_returns_and_sort(df_data):
	'''
	@summary: Takes a dataframe of closing prices, converts to 0 based returns, then reorders the columns where the greatest
	overall returns are the furthest to the left which subsequently will be listed first in the diagram's legend.
	'''
	ls_syms = df_data.columns.tolist()
	npa = df_data.values
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
	return df

		
def create_plots(self, verbose=False):
	print('Creating images...')

	ls_acctdata = da.DataAccess.get_info_from_account(self)

	for acct in ls_acctdata:
		acctname = acct[0] # get account name
		if verbose == True:
			print(acctname)
		filename = acctname + '-' + da.DataItem.ADJUSTED_CLOSE + '.pkl'
		filename = filename.replace(' ', '')
		datapath = os.path.join(self.datafolder, filename) 
		df_data = da.DataAccess.get_dataframe(datapath, clean=True) # get data frame

		for k, v in da.imgScope.TIMESERIES.items():
			filename_addition = k
			if verbose == True:
				print('efficient frontier ' + filename_addition)
			df = df_data.copy()
			if k != '_all_years': # 'all years' data is passed as is
				df = df.iloc[-v:] # slice the data into the timeframes described in scope.TIMESERIES
				efficient_frontier(self, df, acctname, filename_addition)
			else:
				efficient_frontier(self, df, acctname, filename_addition)
			
		for k, v in da.imgScope.TIMESERIES.items():
			filename_addition = k
			if verbose == True:
				print('returns ' + filename_addition)
			df = df_data.copy()
			if k != '_all_years': # 'all years' data is passed as is
				df = df.iloc[-v:] # slice the data into the timeframes described in scope.TIMESERIES
				returns(self, df, acctname, filename_addition)
			else:
				returns(self, df, acctname, filename_addition)


def returns(self, df_data, acct, filename_addition):
	
	if len(df_data.columns) > 20: # When there are numerous funds in an account, get unique optimized symbols and
		# chart those.
		ls_syms = da.DataAccess.get_opt_syms(self, acct)
		df_data = df_data[ls_syms]
		print('worked if you see this')
		# sys.exit(0)
	
	df = get_returns_and_sort(df_data)
	
	ls_syms = df.columns.tolist()
	ls_index = df.index.tolist()

	np_array = df.values

	out_filepath = os.path.join(self.fundimagefolder, acct + '_returns' + filename_addition + '.png')
	
	f = plt.figure(num=None, figsize=(12, 6), dpi=80, facecolor='w', edgecolor='k')
	plt.clf()
	plt.plot(ls_index, np_array)
	plt.legend(ls_syms, loc='upper left')
	plt.ylabel('Adjusted Close')
	plt.xlabel('Date')
	# plt.show()
	f.savefig(out_filepath)
	plt.close('all')


def efficient_frontier(self, df_data, acct, filename_addition):
	'''
	could be improved by instead of just dividing expected return by 20, divide some ratio of exp. return / std. dev
	to compensate for steep frontiers.
	'''
	df_all = du.get_risk_ret(df_data) # get np arrays of the exp return and st. dev of each fund

	df_eff = du.get_frontier(df_data) # get twenty efficient portfolios 

	df_eff_port = du.get_frontier_portfolios(df_data) # get four defined efficient porfolios

	y_arr_d = df_all.iloc[:,0:1].values # all funds expected returns
	x_arr_d = df_all.iloc[:,1:2].values # all funds std deviations

	y_arr_e = df_eff.iloc[:,0:1].values # efficient portfolio graph expected return
	x_arr_e = df_eff.iloc[:,1:2].values # efficient portfolio graph std deviation

	titles = df_eff_port.iloc[:,0:1].values # all first column i.e. portfolio names
	y_arr_e_port = df_eff_port.iloc[:,1:2].values # efficient portfolios expected return
	x_arr_e_port = df_eff_port.iloc[:,2:3].values # efficient portfolios std deviation

	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.scatter(x_arr_d, y_arr_d, c='b') # blue scatter plots for all funds
	ax1.plot(x_arr_e, y_arr_e, c='r') # red line plot for the efficient frotier
	ax1.scatter(x_arr_e_port, y_arr_e_port, c='r') # red scatter plots for the four portfolios.

	plt.xlabel('Risk')
	plt.ylabel('Returns')


	for label, x, y in zip(titles, x_arr_e_port, y_arr_e_port):
		plt.annotate(label, xy = (x, y), xytext = (20, -20),
			textcoords = 'offset points', ha = 'right', va = 'top',
			bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
			arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

	filepath = os.path.join(self.fundimagefolder, acct + '_eff_frontier' + filename_addition + '.png')
	# plt.show()
	plt.savefig(filepath)
	plt.close('all')


#************************************ SP 500 sectors *******************************************************************

def index_plots(self): # charts the sectors themselves
	
	print('Creating S&P 500 sector plot...')
	# index_dir = self.indexdir
	out_filepath = self.indeximagefolder
	filepath = os.path.join(self.datafolder, '$sp500_index.pkl') 
	df_data = da.DataAccess.get_dataframe(filepath, clean=False)

	for k, v in da.imgScope.TIMESERIES.items():
		filename_addition = k
		df = df_data.copy()
		if k != '_all_years': # 'all years' data is passed as is
			df = df.iloc[-v:] # slice the data into the timeframes described in scope.TIMESERIES
			for filename, columns in sp500.index.items():
				dfx = df[columns]
				filepath = self.indeximagefolder
				file = filename + filename_addition + '.png'
				savepath = os.path.join(out_filepath, file)
				index_plot(self, dfx, savepath)
		else:
			for filename, columns in sp500.index.items():
				filepath = self.indeximagefolder
				file = filename + filename_addition + '.png'
				savepath = os.path.join(filepath, file)
				dfx = df[columns]
				index_plot(self, dfx, savepath)


def index_plot(self, df_data, out_filepath):

	df = get_returns_and_sort(df_data)
	
	ls_syms = df.columns.tolist()
	ls_index = df.index.tolist()

	np_array = df.values

	# x = ls_syms.index(index_name) # find the index in the dataframe where the market (VOO) lies
	# market_vec = np_array[:,x:(x+1)] # create a numpy array of just the market column
	# component_vec = np_array # all other (including market) columns in a single array
	
	fig = plt.figure(num=None, figsize=(12, 6), dpi=80, facecolor='w', edgecolor='k')
	ax1 = fig.add_subplot(111)
	ax1.plot(ls_index, np_array, linewidth=1) # scatter plots for all funds
	# ax1.plot(ls_index, market_vec, 'bs', linewidth=1) # blue square plot to highlight the market index

	plt.legend(ls_syms, loc='upper left')
	plt.xlabel('Date')
	plt.ylabel('Adjusted Close')
	# plt.show()
	fig.savefig(out_filepath)
	plt.close('all')

	# sector_component_returns(self, df, out_filepath, filename_addition)


def sector_component_returns(self, df, out_filepath, filename_addition): # charts the stocks within each sector
	'''
	@Summary: Takes a dataframe of index close prices, converts to .change(), converts to .mean(), then averages the mean
	across all stocks into a single series. This is done in a loop across all sectors and the result is a dataframe of price
	changes across all sectors which is then plotted. 
	'''
	datafolder = self.datafolder
	datafolder = os.path.join(datafolder, 'sp500_sectors_data')
	datafiles = list()
	dfilesmatch = list()
	for file in os.listdir(datafolder):
		datafiles.append(file) #create a list of files from the sp500_sectors_data folder

	for file in datafiles: 
		file = file[:-13] # remove the '_contents.pkl' of each file name
		file = file.replace('_', ' ')
		dfilesmatch.append(file) # create a second list of these files that has been edited to match sector names.

	ls_sectors = df.columns.tolist()
	# ls_index = df.index.tolist()

	for sector in ls_sectors:
		for s in dfilesmatch:
			if sector.lower() == s:
				i = dfilesmatch.index(s)
				file = datafiles[i]
				datafile = os.path.join(datafolder, file)
				df_data = da.DataAccess.get_dataframe(datafile, clean=True)
				df_market = df[sector]
				if filename_addition != '_all_years':
					x = da.imgScope.TIMESERIES[filename_addition]
					df_data = df_data.iloc[-x:]
					df_market = df_market.iloc[-x:]
				
				df_data = get_returns_and_sort(df_data)
				
				sector_component_chart(df_market, df_data, sector, out_filepath, filename_addition)
			elif sector == 'Technology':
				pass #combine the telecommunication and information technology


def sector_component_chart(df_market, df_stocks, sector, out_filepath, filename_addition):

	out_filepath = os.path.join(out_filepath, sector + '_comp_returns' + filename_addition + '.png')
	ls_syms = df_stocks.columns.tolist()
	ls_index = df_market.index.tolist()
	market_vec = df_market.values
	component_vec = df_stocks.values
	
	fig = plt.figure(num=None, figsize=(12, 6), dpi=80, facecolor='w', edgecolor='k')
	ax1 = fig.add_subplot(111)
	ax1.plot(ls_index, component_vec, linewidth=1) # line plots for all funds
	ax1.plot(ls_index, market_vec, 'bs', linewidth=1) # red line plot for the market index

	plt.legend(ls_syms[:5], loc='upper left')
	plt.xlabel('Date')
	plt.ylabel('Adjusted Close')
	# plt.show()
	fig.savefig(out_filepath)
	plt.close('all')