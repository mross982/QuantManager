
import os
from yahoo_finance import Share
import pickle as pkl
import datetime as dt
import copy
import sys
from dateutil.relativedelta import relativedelta
import re
import csv
import QSTK.qstkutil.DataAccess as da

def downloadData(self, data_path, ls_symbols, dt_start, dt_end):
	'''Read data from one of the data sources
	@data_path : string for where to place the output files
	@ls_symbols: list of symbols to read from yahoo
	'''
	# Create path if it doesn't exist
	if not (os.access(data_path, os.F_OK)):
	    os.makedirs(data_path)

	ls_missed_syms = []
	ls_data = []
	# utils.clean_paths(data_path)   

	_now = datetime.datetime.now()
	# Counts how many symbols we could not get
	miss_ctr = 0
	for symbol in ls_symbols:
	    # Preserve original symbol since it might
	    # get manipulated if it starts with a "$"
	    symbol_name = symbol
	    if symbol[0] == '$':
	        symbol = '^' + symbol[1:]

	    symbol_data = list()
	    # print "Getting {0}".format(symbol)

	    try:
	        print 'Getting ' + symbol + ' data from Yahoo...'
	        symbol_data = Share(symbol_name)
	        symbol_data.get_historical(str(start_date), str(end_date))
	        os.exit(0)

	        header = url_get.readline()
	        symbol_data.append (url_get.readline())
	        while (len(symbol_data[-1]) > 0):
	            symbol_data.append(url_get.readline())



	    except:
	        miss_ctr += 1
	        ls_missed_syms.append(symbol_name)
	        print "Unable to fetch data for stock " + str(symbol_name)

	writedata(updates)


	def writedata(updates):

		print 'csv files created'

		fieldorder = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
		for items in updates:
		    for thing in items:
		        keys = thing[0].keys()
		        ticker_symbol = thing[0]
		        ticker_symbol = str(ticker_symbol['Symbol'])
		        path = 'C:\Python27\Lib\site-packages\QSTK\QSData\Yahoo'
		    
		        with open(path + '\\' + ticker_symbol + '.csv', 'wb') as csv_file:
		            dict_writer = csv.DictWriter(csv_file, fieldnames = fieldorder, restval = 'nan', extrasaction='ignore')
		            dict_writer.writeheader()
		            dict_writer.writerows(thing)


		    try:
		        params = urllib.urlencode ({'a':0, 'b':1, 'c':2000, 'd':_now.month-1, 'e':_now.day, 'f':_now.year, 's': symbol})
		        url = "http://ichart.finance.yahoo.com/table.csv?%s" % params
		        url_get = urllib2.urlopen(url)
		        
		        header = url_get.readline()
		        symbol_data.append (url_get.readline())
		        while (len(symbol_data[-1]) > 0):
		            symbol_data.append(url_get.readline())

		        # The last element is going to be the string of length zero. 
		        # We don't want to write that to file.
		        symbol_data.pop(-1)
		        #now writing data to file
		        f = open (data_path + symbol_name + ".csv", 'w')

		        #Writing the header
		        f.write (header)

		        while (len(symbol_data) > 0):
		            f.write (symbol_data.pop(0))

		        f.close()

		    except urllib2.HTTPError:
		        miss_ctr += 1
		        ls_missed_syms.append(symbol_name)
		        print "Unable to fetch data for stock: {0} at {1}".format(symbol_name, url)
		    except urllib2.URLError:
		        miss_ctr += 1
		        ls_missed_syms.append(symbol_name)
		        print "URL Error for stock: {0} at {1}".format(symbol_name, url)

		print "All done. Got {0} stocks. Could not get {1}".format(len(ls_symbols) - miss_ctr, miss_ctr)
		return ls_missed_syms

if __name__ == '__main__':

	c_dataobj = da.DataAccess('Yahoo')
	print c_dataobj.rootdir