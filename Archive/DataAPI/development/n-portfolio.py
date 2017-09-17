

import numpy as np
import pandas as pd
from scipy import stats
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime
import json
from bs4 import BeautifulSoup
import requests

# define some custom colours
grey = .6, .6, .6


def timestamp2date(timestamp):
    # function converts a Unix timestamp into Gregorian date
    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')

def date2timestamp(date):
    # function coverts Gregorian date in a given format to timestamp
    return datetime.strptime(date_today, '%Y-%m-%d').timestamp()

def fetchCryptoClose(fsym, tsym):
    # function fetches the close-price time-series from cryptocompare.com
    # it may ignore USDT coin (due to near-zero pricing)
    # daily sampled
    cols = ['date', 'timestamp', fsym]
    lst = ['time', 'open', 'high', 'low', 'close']
    timestamp_today = datetime.today().timestamp()
    curr_timestamp = timestamp_today

    for j in range(2):
        df = pd.DataFrame(columns=cols)
        url = "https://min-api.cryptocompare.com/data/histoday?fsym=" + fsym + \
              "&tsym=" + tsym + "&toTs=" + str(int(curr_timestamp)) + "&limit=2000"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        dic = json.loads(soup.prettify())
        for i in range(1, 2001):
            tmp = []
            for e in enumerate(lst):
                x = e[0]
                y = dic['Data'][i][e[1]]
                if(x == 0):
                    tmp.append(str(timestamp2date(y)))
                tmp.append(y)
            if(np.sum(tmp[-4::]) > 0):  # remove for USDT
                tmp = np.array(tmp)
                tmp = tmp[[0,1,4]]  # filter solely for close prices
                df.loc[len(df)] = np.array(tmp)
        # ensure a correct date format
        df.index = pd.to_datetime(df.date, format="%Y-%m-%d")
        df.drop('date', axis=1, inplace=True)
        curr_timestamp = int(df.ix[0][0])
        if(j == 0):
            df0 = df.copy()
        else:
            data = pd.concat([df, df0], axis=0)
    data.drop("timestamp", axis=1, inplace=True)

    return data  # DataFrame




    # N-Cryptocurrency Portfolio (tickers)
fsym = ['BTC', 'ETH', 'DASH', 'XMR', 'XRP', 'LTC', 'ETC', 'XEM', 'REP',
        'MAID', 'ZEC', 'STEEM', 'GNT', 'FCT', 'ICN', 'DGD',
        'WAVES', 'DCR', 'LSK', 'DOGE', 'PIVX']
# vs.
tsym = 'USD'

fsym = fsym[:2]

for e in enumerate(fsym):
    print(e[0], e[1])
    if(e[0] == 0):
        # try:
            data = fetchCryptoClose(e[1], tsym)
        # except:
        #     pass
    else:
        # try:
        data = data.join(fetchCryptoClose(e[1], tsym))
        # except:
        #     pass

# data = data.astype(float)  # ensure values to be floats

data.to_csv('data.csv')

# for symbol in data.columns:


# # save portfolio to a file (HDF5 file format)
# store = pd.HDFStore('portfolio.h5')
# store['data'] = data
# store.close()



# # read in your portfolio from a file
# df = pd.read_hdf('portfolio.h5', 'data')
# # print(df)

# # The df.columns prints a list of all ticker symbols in the data frame
# print(df.columns)

# # Here we select a few symbols to add to a new data frame for analysis
# df1 = df[['BTC', 'DASH', 'XMR']]
# # print(df1.head())

# # The problem is that not all currencies were created and traded on the same day. Therefore, the data will contain
# # NaN values for any date which no price data exists for the ticker symbol. The code below removes any data history
# # in which a non numeric value (NaN) exists for ANY ticker symbol. THerefore, it starts when the most recently created
# # coin went on the market.
# df1 = df1.dropna().drop_duplicates()
# # print(df1.head())

# # the author chose March 2017 time frame to perform the PCA (Pricipled Component Analysis) as all values must be numeric.
# # portfolio pre-processing
# dfP = df[(df.index >= "2017-03-01") & (df.index <= "2017-03-31")]
# dfP = dfP.dropna(axis=1, how='any')

# m = dfP.mean(axis=0)
# s = dfP.std(ddof=1, axis=0)

# # normalised time-series as an input for PCA
# dfPort = (dfP - m)/s

# c = np.cov(dfPort.values.T)     # covariance matrix
# co = np.corrcoef(dfP.values.T)  # correlation matrix

# tickers = list(dfP.columns)

# plt.figure(figsize=(8,8))
# plt.imshow(co, cmap="RdGy", interpolation="nearest")
# cb = plt.colorbar()
# cb.set_label("Correlation Matrix Coefficients")
# plt.title("Correlation Matrix", fontsize=14)
# plt.xticks(np.arange(len(tickers)), tickers, rotation=90)
# plt.yticks(np.arange(len(tickers)), tickers)

# # perform PCA
# w, v = np.linalg.eig(c)

# ax = plt.figure(figsize=(8,8)).gca()
# plt.imshow(v, cmap="bwr", interpolation="nearest")
# cb = plt.colorbar()
# plt.yticks(np.arange(len(tickers)), tickers)
# plt.xlabel("PC Number")
# plt.title("PCA", fontsize=14)
# # force x-tickers to be displayed as integers (not floats)
# ax.xaxis.set_major_locator(MaxNLocator(integer=True))


# # choose PC-k numbers
# k1 = -1  # the last PC column in 'v' PCA matrix
# k2 = -2  # the second last PC column

# # begin constructing bi-plot for PC(k1) and PC(k2)
# # loadings
# plt.figure(figsize=(7,7))
# plt.grid()

# # compute the distance from (0,0) point
# dist = []
# for i in range(v.shape[0]):
#     x = v[i,k1]
#     y = v[i,k2]
#     plt.plot(x, y, '.k')
#     plt.plot([0,x], [0,y], '-', color=grey)
#     d = np.sqrt(x**2 + y**2)
#     dist.append(d)

#     # check and save membership of a coin to
# # a quarter number 1, 2, 3 or 4 on the plane
# quar = []
# for i in range(v.shape[0]):
#     x = v[i,k1]
#     y = v[i,k2]
#     d = np.sqrt(x**2 + y**2)
#     if(d > np.mean(dist) + np.std(dist, ddof=1)):
#         plt.plot(x, y, '.r', markersize=10)
#         plt.plot([0,x], [0,y], '-', color=grey)
#         if((x > 0) and (y > 0)):
#             quar.append((i, 1))
#         elif((x < 0) and (y > 0)):
#             quar.append((i, 2))
#         elif((x < 0) and (y < 0)):
#             quar.append((i, 3))
#         elif((x > 0) and (y < 0)):
#             quar.append((i, 4))
#         plt.text(x, y, tickers[i], color='k')

# plt.xlabel("PC-" + str(len(tickers)+k1+1))
# plt.ylabel("PC-" + str(len(tickers)+k2+1))

# for i in range(len(quar)):
#     # Q1 vs Q3
#     if(quar[i][1] == 1):
#         for j in range(len(quar)):
#             if(quar[j][1] == 3):
#                 plt.figure(figsize=(7,4))

#                 # highly correlated coins according to the PC analysis
#                 print(tickers[quar[i][0]], tickers[quar[j][0]])

#                 ts1 = dfP[tickers[quar[i][0]]]  # time-series
#                 ts2 = dfP[tickers[quar[j][0]]]

#                 # correlation metrics and their p_values
#                 slope, intercept, r2, pvalue, _ = stats.linregress(ts1, ts2)
#                 ktau, kpvalue = stats.kendalltau(ts1, ts2)
#                 print(r2, pvalue)
#                 print(ktau, kpvalue)

#                 plt.plot(ts1, ts2, '.k')
#                 xline = np.linspace(np.min(ts1), np.max(ts1), 100)
#                 yline = slope*xline + intercept
#                 plt.plot(xline, yline,'--', color='b')  # linear model fit
#                 plt.xlabel(tickers[quar[i][0]])
#                 plt.ylabel(tickers[quar[j][0]])
#                 plt.show()
#     # Q2 vs Q4
#     if(quar[i][1] == 2):
#         for j in range(len(quar)):
#             if(quar[j][1] == 4):
#                 plt.figure(figsize=(7,4))
#                 print(tickers[quar[i][0]], tickers[quar[j][0]])
#                 ts1 = dfP[tickers[quar[i][0]]]
#                 ts2 = dfP[tickers[quar[j][0]]]
#                 slope, intercept, r2, pvalue, _ = stats.linregress(ts1, ts2)
#                 ktau, kpvalue = stats.kendalltau(ts1, ts2)
#                 print(r2, pvalue)
#                 print(ktau, kpvalue)
#                 plt.plot(ts1, ts2, '.k')
#                 xline = np.linspace(np.min(ts1), np.max(ts1), 100)
#                 yline = slope*xline + intercept
#                 plt.plot(xline, yline,'--', color='b')
#                 plt.xlabel(tickers[quar[i][0]])
#                 plt.ylabel(tickers[quar[j][0]])
#                 plt.show()