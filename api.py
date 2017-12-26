
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

class DateRange(object):
	'''
	this sets date time frames for pulling data via API
	'''
	NOW = dt.datetime.now()
	TODAY = dt.date.today()
	r1DAY = (dt.date.today() + dt.timedelta(days=-1)).strftime('%m/%d/%Y')
	r1WEEK = (dt.date.today() + dt.timedelta(weeks=-1)).strftime('%m/%d/%Y')
	r1MONTH = (dt.date.today() + dt.timedelta(weeks=-4.3)).strftime('%m/%d/%Y')
	r3MONTH = (dt.date.today() + dt.timedelta(weeks=-13)).strftime('%m/%d/%Y')
	r6MONTH = (dt.date.today() + dt.timedelta(weeks=-26)).strftime('%m/%d/%Y')
	r1YEAR = dt.date.today() + dt.timedelta(weeks=-52)
	r2YEAR = (dt.date.today() + dt.timedelta(weeks=-104)).strftime('%m/%d/%Y')
	r3YEAR = (dt.date.today() + dt.timedelta(weeks=-156)).strftime('%m/%d/%Y')
	r5YEAR = (dt.date.today() + dt.timedelta(weeks=-260)).strftime('%m/%d/%Y')
	r10YEAR = (dt.date.today() + dt.timedelta(weeks=-520)).strftime('%m/%d/%Y')


class API(object):
	'''
	@Summary: this class contains functions that receive a data path, list of symbols and time frame which is then used 
	download financial data in both csv and pkl formats.
	'''
	def __init__(self):
		if c_dataobj.source == da.DataSource.STOCK:
			self.today = DateRange.TODAY
			self.dataTimeStart = DateRange.r1YEAR
		elif c_dataobj.source == da.DataSource.FUND:
			self.today = DateRange.TODAY
			self.dataTimeStart = DateRange.r1YEAR


	def get_MF_close(self):
		'''
		@Summary: takes a list of FUND symbols, retrieves adjusted close prices, then saves in the datafolder.
		called from main.py
		'''

		print('downloading data')

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
		df = web.DataReader(ls_symbols, 'google', start=DateRange.r5YEAR)[item]
		# df = web.DataReader(ls_symbols, 'google', start=DateRange.r5YEAR)[item]
		df = df.sort_index()
		return df


	def getYahooData(ls_symbols, item=da.DataItem.ADJUSTED_CLOSE):
		'''
		API that gets fund information from the Yahoo servers.
		'''
		
		df = web.DataReader(ls_symbols, 'yahoo', start=DateRange.r5YEAR)[item]
		# error handling SymbolWarning: is done through pandas_datareader\yahoo\daily.py package
		df = df.sort_index()	
		return df
