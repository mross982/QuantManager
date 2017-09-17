
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


	# def getYahooData(self, data_path, ls_symbols):
	# 	# utils.clean_paths(data_path) 

	# 	for symbol in ls_symbols:

	# 		# Preserve original symbol since it might get manipulated if it starts with a "$"
	# 		symbol_name = symbol
	# 		if symbol[0] == '$':
	# 			symbol = '^' + symbol[1:]

	# 		symbol_data = []
	# 		ls_missed_syms = []
	# 		print 'Getting ' + symbol + ' data from Yahoo...'
	# 		try:
	# 			url = 'https://finance.yahoo.com/quote/' + str(symbol) + '/history/'
	# 			rows =bs(urllib2.urlopen(url).read()).findAll('table')[1].tbody.findAll('tr')
	# 			for each_row in rows:
	# 				divs = each_row.findAll('td')
	# 				if divs[1].span.text != 'Dividend':
	# 					symbol_data.append({'Date': divs[0].span.text, 'Open': float(divs[1].span.text.replace(',','')),
	# 						'High': float(divs[2].span.text.replace(',','')), 'Low': float(divs[3].span.text.replace(',','')),
	# 						'Close': float(divs[4].span.text.replace(',','')), 'Volume': float(divs[6].span.text.replace(',','')),
	# 						'Adj Close': float(divs[5].span.text.replace(',',''))})

	# 					# df = pd.DataFrame.from_records(map(json.loads, symbol_data))
	# 					# print df.head()
	# 		except:
	# 			miss_ctr += 1
	# 			ls_missed_syms.append(symbol_name)
	# 			print 'Unable to fetch data for stock ' + symbol_name

	# 	if len(ls_missed_syms) > 0:
	# 		pass
			# do something to rerun the symbols list
		# df = pd.DataFrame.from_records(map(json.loads, symbol_data))
		# print df.head()
	# def writeDataCSV(updates):

	# 	print 'csv files created'

	# 	fieldorder = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
	# 	for items in updates:
	# 		for thing in items:
	# 			keys = thing[0].keys()
	# 			ticker_symbol = thing[0]
	# 			ticker_symbol = str(ticker_symbol['Symbol'])
	# 		# path = 'C:\Python27\Lib\site-packages\QSTK\QSData\Yahoo'
			
	# 			with open(path + '\\' + ticker_symbol + '.csv', 'wb') as csv_file:
	# 				dict_writer = csv.DictWriter(csv_file, fieldnames = fieldorder, restval = 'nan', extrasaction='ignore')
	# 				dict_writer.writeheader()
	# 				dict_writer.writerows(thing)



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

	
	#----Remember sys.argv[0] is the script itself
	# if len(sys.argv) > 3:
	# 	source = sys.argv[1]
	# 	st_olddate = sys.argv[2]
	# 	st_recentdate = sys.argv[3]
	# elif len(sys.argv) > 2:
	# 	source = sys.argv[1]
	# 	st_olddate = sys.argv[2]
	# else:
	# 	source = sys.argv[1]

		# for x in range(len(sys.argv)):
		# 	if x == 0:
		# 		pass
		# 	else:
				# source = sys.argv[x]

	if len(sys.argv)>1:
		c_dataobj = da.DataAccess(sys.argv[1])
	else:
		c_dataobj = da.DataAccess(da.DataSource.GOOGLE)

	# if c_dataobj.source == da.DataSource.YAHOO:
	# 	API = API()
	# 	today = DateRange.TODAY
	# 	dataTimeStart = DateRange.r1YEAR
	# 	ls_acctfiles = c_dataobj.accountFiles
	# 	ls_acctdata = c_dataobj.get_info_from_account(ls_acctfiles) # ls_accotdata contains lists where [0] = account, [1] = balance, [2:] = symbols
		
	# 	if len(ls_accotdata) == 1:
	# 		ls_symbols = ls_acctdata
	# 	else:
	# 		for acct in ls_acctdata:
	# 			ls_symbols = acct[2:]
	# 			ls_data = API.getGoogleData(c_dataobj.rootdir, ls_symbols, dataTimeStart, today)


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
	