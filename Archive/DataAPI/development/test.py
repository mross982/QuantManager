import pandas as pd
import pandas_datareader.data as web
import datetime
from yahoo_finance import Share

def apiTest1():
	stocks = ['ORCL', 'TSLA', 'IBM','YELP', 'MSFT']
	ls_key = 'Adj Close'
	start = datetime.datetime(2014,1,1)
	end = datetime.datetime(2014,3,28)    
	f = web.DataReader(stocks, 'yahoo',start,end)


	cleanData = f.ix[ls_key]
	dataFrame = pd.DataFrame(cleanData)

	print(dataFrame[:5])

def apiTest2():
	yahoo = Share('APPL')
	print(yahoo.get_price())
	print(yahoo.get_historical('2016-05-01', '2016-05-04'))

if __name__ == '__main__':
	apiTest2()