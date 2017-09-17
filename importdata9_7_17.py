
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

class DateRange(object):
	NOW = dt.datetime.now() #maybe different class for time ranges
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
		if c_dataobj.source == da.DataSource.GOOGLE:
			self.today = DateRange.TODAY
			self.dataTimeStart = DateRange.r1YEAR
		elif c_dataobj.source == da.DataSource.YAHOO:
			self.today = DateRange.TODAY
			self.dataTimeStart = DateRange.r1YEAR


	def getGoogleData(self, data_path, ls_acctdata, datatype):
		'''
		
		'''
		items = [da.DataItem.CLOSE, da.DataItem.VOLUME]
		for acct in ls_acctdata:
			ls_symbols = acct[2:]
			account = str(acct[0])
			d_path = data_path

			for item in items:
				path = os.path.join(d_path, da.DataSource.GOOGLE, account + '-' + item + '.pkl')
				df = web.DataReader(ls_symbols, 'google', start=self.dataTimeStart)
				stock_data = df.to_frame()
				df.to_pickle(path)
				path = ''

			# if df.isnull().values.any() == True: # potential sanity check for any NaN values
			# 	raise ValueError('there are missing data in this set')

			# need a way to detect symbol warning, capture the symbol, then attempt to recapture the data

	def getYahooData(self, data_path, ls_acctdata, datatype):
			'''

			'''
			items = [da.DataItem.ADJUSTED_CLOSE]
			symbols = []

			for acct in ls_acctdata:
				ls_symbols = acct[2:]
				# if datatype == da.DataType.MUTUAL_FUND:
				# 	for x in ls_symbols:
				# 		symbols += x.keys()
				# else:
				symbols = ls_symbols
				account = str(acct[0])
				d_path = data_path

				for item in items:
					filename = account + '-' + item + '.pkl'
					filename = filename.replace(' ', '')
					path = os.path.join(d_path, da.DataSource.YAHOO, filename)
					df = web.DataReader(symbols, 'yahoo', start=self.dataTimeStart)[item]			
					df.to_pickle(path)
					path = ''
		

if __name__ == '__main__':

	if len(sys.argv)>1:
		c_dataobj = da.DataAccess(sys.argv[1])
	else:
		c_dataobj = da.DataAccess(da.DataSource.YAHOO)

	if c_dataobj.source == da.DataSource.GOOGLE:
		API = API()
		ls_acctdata = c_dataobj.get_info_from_account(c_dataobj.accountfiles) 
		# if len(ls_acctdata) > 0:
		# 	print('account data is good')
		# 	print(ls_acctdata[0])
		# print(ls_acctdata)
		API.getGoogleData(c_dataobj.datadir, ls_acctdata, c_dataobj.accounttype)

	elif c_dataobj.source == da.DataSource.YAHOO:
		API = API()
		ls_acctdata = c_dataobj.get_info_from_account(c_dataobj.accountfiles) 
		API.getYahooData(c_dataobj.datadir, ls_acctdata, c_dataobj.accounttype)

	
	elif c_dataobj.source == da.DataSource.CRYPTOCOMPARE:
		API = API()
		today = DateRange.TODAY
		dataTimeStart = DateRange.r1YEAR
		ls_acctfiles = c_dataobj.accountfiles
		ls_acctdata = c_dataobj.get_info_from_account(ls_acctfiles) # ls_accotdata contains lists where [0] = account, [1] = balance, [2:] = symbols
		

	else:
		print('no source match?')
	