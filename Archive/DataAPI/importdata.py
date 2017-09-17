
import os
from yahoo_finance import Share
import pickle as pkl
import datetime as dt
import json
import time
import copy
import sys
from dateutil.relativedelta import relativedelta
import re
import csv
import string
import QSTK.qstkutil.DataAccess as da
from os import listdir
from os.path import isfile, join
import urllib2
from BeautifulSoup import BeautifulSoup as bs
import pandas as pd
import pandas_datareader as pdr
import pandas_datareader.data as wb

class DateRange(object):
	NOW = dt.datetime.now() #maybe different class for time ranges
	TODAY = dt.date.today()
	r1DAY = dt.date.today() - relativedelta(days=1)
	r1WEEK = dt.date.today() - relativedelta(weeks=1)
	r1MONTH = dt.date.today() - relativedelta(months=1)
	r3MONTH = dt.date.today() - relativedelta(months=3)
	r6MONTH = dt.date.today() - relativedelta(months=6)
	r1YEAR = dt.date.today() - relativedelta(years=1)
	r2YEAR = dt.date.today() - relativedelta(years=2)
	r3YEAR = dt.date.today() - relativedelta(years=3)
	r5YEAR = dt.date.today() - relativedelta(years=5)
	r10YEAR = dt.date.today() - relativedelta(years=10)


class API(object):
	'''
	@Summary: this class contains functions that receive a data path, list of symbols and time frame which is then used 
	download financial data in both csv and pkl formats.
	'''
	def __init__(self):
		if c_dataobj.source == da.DataSource.YAHOO:
			self.today = DateRange.TODAY
			self.dataTimeStart = DateRange.r1WEEK
		elif c_dataobj.source == da.DataSource.GOOGLE:
			self.today = DateRange.TODAY
			self.dataTimeStart = DateRange.r1YEAR
		elif c_dataobj.source == da.DataSource.GOOGLE:
			self.today = DateRange.TODAY
			self.dataTimeStart = DateRange.r1YEAR


	def getGoogleData(self, data_path, ls_symbols):
		'''
		returns dataframe with items in the order Date, Sym, Open, High, Low, Close & Volume.
		no adjusted close :(
		'''
		data_path = os.path.join(data_path, da.DataSource.GOOGLE)
		if not os.path.exists(data_path):
			os.makedirs(data_path)

		for symbol in ls_symbols:
			print 'getting ' + symbol + ' from google...'
			df = wb.DataReader(symbol, 'google', self.dataTimeStart, self.today)
			df.to_csv(os.path.join(data_path, symbol + '.csv'))
			# cachedf(symbol, df)

			# print df.isnull().values.any() # potential sanity check for any NaN values


	def cachedf(self, symbol, df):
		''' 
		Creates a pkl file in the scratch directory
		'''
		pass
		

if __name__ == '__main__':

	if len(sys.argv)>1:
		c_dataobj = da.DataAccess(sys.argv[1])
	else:
		c_dataobj = da.DataAccess(da.DataSource.GOOGLE)

	if c_dataobj.source == da.DataSource.GOOGLE:
		API = API()
		ls_acctfiles = c_dataobj.accountFiles
		ls_acctdata = c_dataobj.get_info_from_account(ls_acctfiles) # ls_accotdata contains lists where [0] = account, [1] = balance, [2:] = symbols
		scratchdirectory = c_dataobj.scratchdir

		if len(ls_acctdata) == 1:
			ls_symbols = ls_acctdata[2:]
			ls_data = API.getGoogleData(c_dataobj.datadir, ls_symbols)
		else:
			for acct in ls_acctdata:
				ls_symbols = acct[2:]
				ls_data = API.getGoogleData(c_dataobj.datadir, ls_symbols)

	
	elif c_dataobj.source == da.DataSource.CRYPTOCOMPARE:
		API = API()
		today = DateRange.TODAY
		dataTimeStart = DateRange.r1YEAR
		ls_acctfiles = c_dataobj.accountFiles
		ls_acctdata = c_dataobj.get_info_from_account(ls_acctfiles) # ls_accotdata contains lists where [0] = account, [1] = balance, [2:] = symbols
		

	else:
		print 'no source match?'
	