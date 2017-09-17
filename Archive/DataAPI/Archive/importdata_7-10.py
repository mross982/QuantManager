
import os
from yahoo_finance import Share
import pickle as pkl
import datetime as dt
import copy
import sys
from dateutil.relativedelta import relativedelta
import re
import csv
import string
import QSTK.qstkutil.DataAccess as da
from os import listdir
from os.path import isfile, join

import pandas as pd
from pandas_datareader import data

def getYahooData(data_path, ls_symbols, dt_oldDate, dt_recentDate):
	'''Read data from one of the data sources
	@data_path : string for where to place the output files
	@ls_symbols: list of symbols to read from yahoo
	'''
	ls_missed_syms = []
	ls_data = []
	# utils.clean_paths(data_path)   

	# Counts how many symbols we could not get
	miss_ctr = 0
	for symbol in ls_symbols:

	    # Preserve original symbol since it might get manipulated if it starts with a "$"
	    symbol_name = symbol
	    if symbol[0] == '$':
	        symbol = '^' + symbol[1:]

	    symbol_data = list()
	    # print "Getting {0}".format(symbol)

	    try:
			print 'Getting ' + symbol + ' data from Yahoo...'
			yahoo = Share(symbol)
			print yahoo.get_price()
			print yahoo.get_historical_data('2016-05-01', '2016-05-04') 
	        


			# start = datetime.datetime(2016,1,1)

			# finData = data.DataReader(symbol, 'yahoo', start)
			# print finData.head()


			#-------------------------------------------------------	      
	        # symbol_data = Share(symbol)
	        # mylist[
	        # symbol_data.get_historical(str(dt_start), str(dt_end))
	        # ]
	        # ls_data.append(mylist)

	        # symbol_data = Share(symbol)
	        # symbol_data.get_historical(str(dt_start), str(dt_end)
	        # header = url_get.readline()
	        # symbol_data.append (url_get.readline())
	        # while (len(symbol_data[-1]) > 0):
	        #     symbol_data.append(url_get.readline())

	    except:
	        miss_ctr += 1
	        ls_missed_syms.append(symbol_name)
	        print "Unable to fetch data for stock " + str(symbol_name)

	print ls_data
	# writedata(updates)


def writedata(updates):

	print 'csv files created'

	fieldorder = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
	for items in updates:
	    for thing in items:
	        keys = thing[0].keys()
	        ticker_symbol = thing[0]
	        ticker_symbol = str(ticker_symbol['Symbol'])
	        # path = 'C:\Python27\Lib\site-packages\QSTK\QSData\Yahoo'
	    
	        with open(path + '\\' + ticker_symbol + '.csv', 'wb') as csv_file:
	            dict_writer = csv.DictWriter(csv_file, fieldnames = fieldorder, restval = 'nan', extrasaction='ignore')
	            dict_writer.writeheader()
	            dict_writer.writerows(thing)


	#     try:
	#         params = urllib.urlencode ({'a':0, 'b':1, 'c':2000, 'd':_now.month-1, 'e':_now.day, 'f':_now.year, 's': symbol})
	#         url = "http://ichart.finance.yahoo.com/table.csv?%s" % params
	#         url_get = urllib2.urlopen(url)
	        
	#         header = url_get.readline()
	#         symbol_data.append (url_get.readline())
	#         while (len(symbol_data[-1]) > 0):
	#             symbol_data.append(url_get.readline())

	#         # The last element is going to be the string of length zero. 
	#         # We don't want to write that to file.
	#         symbol_data.pop(-1)
	#         #now writing data to file
	#         f = open (data_path + symbol_name + ".csv", 'w')

	#         #Writing the header
	#         f.write (header)

	#         while (len(symbol_data) > 0):
	#             f.write (symbol_data.pop(0))

	#         f.close()

	#     except urllib2.HTTPError:
	#         miss_ctr += 1
	#         ls_missed_syms.append(symbol_name)
	#         print "Unable to fetch data for stock: {0} at {1}".format(symbol_name, url)
	#     except urllib2.URLError:
	#         miss_ctr += 1
	#         ls_missed_syms.append(symbol_name)
	#         print "URL Error for stock: {0} at {1}".format(symbol_name, url)

	# print "All done. Got {0} stocks. Could not get {1}".format(len(ls_symbols) - miss_ctr, miss_ctr)
	# return ls_missed_syms

def read_symbols(s_symbols_file):
	'''Read a list of symbols'''

	acctBalance = 0  
	ls_symbols = []
	ffile = open(s_symbols_file, 'r')
	for line in ffile.readlines():
		if re.search('\d', line):
			acctBalance = line
		else:
			ls_symbols.append(line.strip())
	ffile.close()
	return acctBalance, ls_symbols 

if __name__ == '__main__':

	"""
	The second argument must match one of the relative or absolute values below 

	years=0, months=0, days=0, leapdays=0, weeks=0,
	hours=0, minutes=0, seconds=0, microseconds=0,
	year=None, month=None, day=None, weekday=None,
	yearday=None, nlyearday=None,
	hour=None, minute=None, second=None, microsecond=None
	"""

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

	c_dataobj = da.DataAccess(source)

	accountpath = c_dataobj.accountdir
	datadir = c_dataobj.folderList

	accntdir = os.listdir(accountpath)

	for acctfile in accntdir:
		if acctfile in c_dataobj.accountfiles: 
			acctpath = os.path.join(accountpath, acctfile)
			account_balance, ls_symbols = read_symbols(acctpath)

	try:
		st_recentdate
	except NameError:
		recent_date = dt.date.today()
	else:
		recent_date = dt.date.today() # This will have to be changed--------------********

	try:
		st_olddate
		print 'passed date differential ' + st_olddate
	except NameError:
		old_date = recent_date - relativedelta(years=1)
	else:
		old_date = recent_date - relativedelta(st_olddate)  # passing a string of 'years=1' does not appear to work.

	if c_dataobj.source == 'Yahoo':
		getYahooData(c_dataobj.rootdir, ls_symbols, old_date, recent_date)
	else:
		print 'no source match?'
	

# import urllib2
# from BeautifulSoup import BeautifulSoup as bs

# def get_historical_data(name, number_of_days):
#     data = []
#     url = "https://finance.yahoo.com/quote/" + name + "/history/"
#     rows = bs(urllib2.urlopen(url).read()).findAll('table')[1].tbody.findAll('tr')

#     for each_row in rows:
#         divs = each_row.findAll('td')
#         if divs[1].span.text  != 'Dividend': #Ignore this row in the table
#             #I'm only interested in 'Open' price; For other values, play with divs[1 - 5]
#             data.append({'Date': divs[0].span.text, 'Open': float(divs[1].span.text.replace(',',''))})

#     return data[:number_of_days]

# #Test
# for i in get_historical_data('amzn', 5):
#     print i