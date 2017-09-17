
from yahoo_finance import Share
import csv
from pprint import pprint
import sys
import os
import re
import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint

def read_symbols(s_symbols_file):
    '''Read a list of symbols'''
  
    acctBalance = 0  
    ls_symbols = []
    ffile = open(s_symbols_file, 'r')
    for line in ffile.readlines():
    	if re.search('\d', line):
    		acctBalance = line
    	else:
	        str_line = str(line)
	        if str_line.strip(): 
	            ls_symbols.append(str_line.strip())
    ffile.close()
    return acctBalance, ls_symbols 

def daily_update(ls_symbols, start_date, end_date):

	updates = []
	for sec in ls_symbols:
		try:
			print 'Getting ' + sec + ' data from Yahoo...'
			security = Share(sec)
			tick = [
			security.get_historical(str(start_date), str(end_date))
			]
			updates.append(tick)
		except:
		    print 'No data for ' + sec
		    pass

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

def makedir(path):
	try:
		os.makedirs(path)
	except:
		if not os.path.isdir(path):
			raise


# gives the opening price of the previous trading day
# print yahoo.get_open()
# gives the last price of the previous trading day
# yahoo.refresh()
# print yahoo.get_price()
# print yahoo.get_trade_datetime()

if __name__ == '__main__':

	end_date = datetime.date.today()
	start_date = end_date - relativedelta(years=1)

	script_dir = os.path.dirname(__file__)
	rel_path = "accounts\\"

	if len(sys.argv) == 1:
		for file in glob.glob(os.path.join(script_dir, rel_path, '*')):
			print filename
			account_Balance, ls_symbols = read_symbols(filename)
			daily_update(ls_symbols, start_date, end_date)
	else: 
		filename = sys.argv[1]
		account_Balance, ls_symbols = read_symbols(os.path.join(script_dir, rel_path, filename))
		print 'Account Balance is', account_Balance
		daily_update(ls_symbols, start_date, end_date)