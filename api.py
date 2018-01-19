
import os
import pickle as pkl
import datetime as dt
import json
import time
import copy
import sys
import re
import string
import DataAccess as da
from os import listdir
from os.path import isfile, join
import pandas as pd
import pandas_datareader as pdr
import pandas_datareader.data as web
from pandas_datareader._utils import RemoteDataError
import requests
import datetime


class API(object):
	'''
	@Summary: this class contains functions that receive a data path, list of symbols and time frame which is then used 
	download financial data in both csv and pkl formats.
	'''
	def __init__(self):
		if c_dataobj.source == da.DataSource.STOCK:
			self.today = da.apiDateRange.TODAY
			self.dataTimeStart = da.apiDateRange.r1YEAR
		elif c_dataobj.source == da.DataSource.FUND:
			self.today = da.apiDateRange.TODAY
			self.dataTimeStart = da.apiDateRange.r1YEAR


	def get_MF_close(self):
		'''
		@Summary: takes a list of FUND symbols, retrieves adjusted close prices, then saves in the datafolder.
		called from main.py
		'''

		print('Downloading fund data via API...')

		ls_acctdata = da.DataAccess.get_info_from_account(self)
		
		data_path = self.datafolder
		symbols = []
		for acct in ls_acctdata:
			ls_symbols = acct[2:]
			# symbols = ls_symbols
			item = da.DataItem.ADJUSTED_CLOSE
			account = str(acct[0])
			d_path = data_path
			filename = account + '-' + item + '.pkl'
			filename = filename.replace(' ', '')
			path = os.path.join(d_path, filename)

			df = API.getYahooData(ls_symbols, item)

			df.to_pickle(path)
			path = ''


	def getGoogleData(ls_symbols, item=da.DataItem.CLOSE):
		'''
		API that gets stock and bond information then returns a dataframe
		'''
		df = web.DataReader(ls_symbols, 'google', start=da.apiDateRange.r5YEAR)[item]
		# df = web.DataReader(ls_symbols, 'google', start=DateRange.r5YEAR)[item]
		df = df.sort_index()
		return df


	def getYahooData(ls_symbols, item=da.DataItem.ADJUSTED_CLOSE):
		'''
		API that gets fund information from the Yahoo servers.
		'''
		
		df = web.DataReader(ls_symbols, 'yahoo', start=da.apiDateRange.r5YEAR)[item]
		# error handling SymbolWarning: is done through pandas_datareader\yahoo\daily.py package
		df = df.sort_index()	
		return df

	def get_crypto_close(self):
		'''
		ls of symbols, comparison symbol,
		'''
		print('Downloading crypto data via API...')

		ls_files = ['coins', 'tokens']
		ls_tickers = []
		comparison_symbol = 'BTC'
		limit=1
		all_data = True
		aggregate=1
		exchange=''
		item = 'close'

		for file in ls_files:
			filename = file + 'mktcap.pkl'
			datapath = os.path.join(self.cryptodatafolder, filename)
			print(datapath)
			df_data = da.DataAccess.get_dataframe(datapath, clean=False) # get data frame
			ls_tick = df_data['Ticker'].tolist() # create a second dataframe reference to just the ticker column
			ls_tickers.extend(ls_tick)

		for ticker in ls_tickers:

			url = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&limit={}&aggregate={}'\
				.format(ticker.upper(), comparison_symbol.upper(), limit, aggregate)
		
			if exchange:
				url += '&e={}'.format(exchange)
			if all_data:
				url += '&allData=true'
			page = requests.get(url)
			data = page.json()['Data']
			df = pd.DataFrame(data)
			df['timestamp'] = [datetime.datetime.fromtimestamp(d) for d in df.time]
			df_data = df['close']
			print(df_data)
			sys.exit(0)
			# start here: need to combine the series's into a dataframe and use ticker as the column head.

	# filepath = self.cryptodatafolder
	# file = filename + filename_addition + '.pkl'
	# savepath = os.path.join(out_filepath, file)
	# index_plot(self, dfx, savepath)