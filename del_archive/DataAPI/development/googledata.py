import urllib2  # works fine with Python 2.7.9 (not 3.4.+)
import json
import time
import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas_datareader as pdr
import pandas_datareader.data as wb
 
def firstAttempt(symbol, exchange):
    link = "http://finance.google.com/finance/info?client=ig&q="
    url = link+"%s:%s" % (exchange, symbol)
    u = urllib2.urlopen(url)
    content = u.read()
    data = json.loads(content[3:])
    info = data[0]
    print info
    time = str(info['lt']) # time stamp

    # t = str(info['elt'])    # time stamp
    # l = float(info['l'])    # close price (previous trading day)
    # p = float(info['el'])   # stock price in pre-market (after-hours)
    # return (t,l,p)

def pandasDataReader(ls_symbols, dt_oldDate, dt_recentDate):
    pnl = wb.DataReader(ls_symbols, 'google', dt_oldDate, dt_recentDate)
    df = pnl.to_frame()
    print df.head()

if __name__ == '__main__':

    symbols = ['AAPL']
    _now = dt.datetime.now()
    dataTimeStart = _now - relativedelta(days=5)

    pandasDataReader(symbols, dataTimeStart, _now)

#--------------------------------------------------------------------------
#     First Attempt at Google API
#---------------------------------------------------------------------------
    # t, l, p = fetchPreMarket("FB","NASDAQ")
    # print "%s\t%.2f\t%.2f\t%+.2f\t%+.2f%%" % (t, l, p, p-l,(p/l-1)*100.)

# p0 = 0
# while True:
#     t, l, p = fetchPreMarket("AAPL","NASDAQ")
#     if(p!=p0):
#         p0 = p
#         print("%s\t%.2f\t%.2f\t%+.2f\t%+.2f%%" % (t, l, p, p-l,
#                                                  (p/l-1)*100.))
#     time.sleep(60)