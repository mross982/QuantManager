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
# import pandas_datareader as pdr
# import pandas_datareader.data as web

# Yahoo Fix
from pandas_datareader import data as pdr
import fix_yahoo_finance

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


class Account_Info(object):
	'''
	captures the account data from dataAccess and returns a list of account names, list of account balances, and 
	list of account tickers.
	'''

	def get_info(self):

		acctnames = []
		acctBalances = []
		acctsyms = []

		ls_acctdata = c_dataobj.get_info_from_account(c_dataobj.accountfiles)
		for acct in ls_acctdata:
			acctnames.append(acct[0])
			acctBalances.append(acct[1])
			acctsyms.append(acct[2:])
		return acctnames, acctBalances, acctsyms


class Price_API(object):
	'''
	@Summary: this class contains functions that receive a data path, list of symbols and time frame which is then used 
	download financial data and save as pickle file.
	'''
	def __init__(self):
		if c_dataobj.source == da.DataSource.GOOGLE:
			self.today = DateRange.TODAY
			self.dataTimeStart = DateRange.r1YEAR
		elif c_dataobj.source == da.DataSource.YAHOO:
			self.today = DateRange.TODAY
			self.dataTimeStart = DateRange.r1YEAR

	def accountNames(self):
		'''
		takes the list of account data and returns just the account name
		'''
		acctnames = []
		ls_acctdata = c_dataobj.get_info_from_account(c_dataobj.accountfiles)
		for acct in ls_acctdata:
			acctnames.append(acct[0])
		return acctnames

	def accountBalances(ls_acctdata):
		'''
		takes the list of account data and returns just the account balance
		'''
		balances = []
		ls_acctdata = c_dataobj.get_info_from_account(c_dataobj.accountfiles)
		for acct in ls_acctdata:
			balances.append(acct[1])
		return balances

	def accountSymbols(ls_acctdata):
		'''
		takes the list of account data and returns a list of tickers
		'''
		syms = []
		ls_acctdata = c_dataobj.get_info_from_account(c_dataobj.accountfiles)
		for acct in ls_acctdata:
			syms.append(acct[2:])
		return syms

	def getGoogleData(self, ls_acctnames, ls_tickers, st_datapath):
		'''
		API that pulls pricing data from google mainly for stocks and bonds
		'''
		items = [da.DataItem.CLOSE]

		accts = dict(zip(ls_acctnames, ls_tickers))
	
		for acct in accts:
			for item in items:
				filename = acct + '-' + item + '.pkl'
				filename = filename.replace(' ', '')
				path = os.path.join(st_datapath, filename)
				df = web.DataReader(accts[acct], 'google', start=self.dataTimeStart)[item]			
				df.to_pickle(path)
				path = ''


	def getYahooData(self, ls_acctnames, ls_tickers, st_datapath):
			'''
			API that pulls pricing data from yahoo for funds. 
			'''
			items = [da.DataItem.ADJUSTED_CLOSE]
			
			accts = dict(zip(ls_acctnames, ls_tickers))
	
			for acct in accts:
				for item in items:
					filename = acct + '-' + item + '.pkl'
					filename = filename.replace(' ', '')
					path = os.path.join(st_datapath, filename)
					# df = web.DataReader(accts[acct], 'yahoo', start=self.dataTimeStart)[item]			
					df = pdr.get_data_yahoo(accts[acct], start=self.dataTimeStart)[item]
					df.to_pickle(path)
					path = ''
		

if __name__ == '__main__':

	if len(sys.argv)>1:
		c_dataobj = da.DataAccess(sys.argv[1])
	else:
		c_dataobj = da.DataAccess(da.DataSource.YAHOO)

	if c_dataobj.source == da.DataSource.GOOGLE:
		API = Price_API()
		API.getGoogleData(API.accountNames(), API.accountSymbols(), c_dataobj.datafolder)

	elif c_dataobj.source == da.DataSource.YAHOO:
		Info = Account_Info()
		name, balance, tickers = Info.get_info()
		print(name)
		print(balance)
		print(tickers)
		# API = Price_API()
		# API.getYahooData(API.accountNames(), API.accountSymbols(), c_dataobj.datafolder)

	
	elif c_dataobj.source == da.DataSource.CRYPTOCOMPARE:
		API = Price_API()
		today = DateRange.TODAY
		dataTimeStart = DateRange.r1YEAR
		ls_acctfiles = c_dataobj.accountfiles
		# self, st_acctname, ls_tickers, datatype
		ls_acctdata = c_dataobj.get_info_from_account(ls_acctfiles) # ls_accotdata contains lists where [0] = account, [1] = balance, [2:] = symbols
		

	else:
		print('no source match?')
	