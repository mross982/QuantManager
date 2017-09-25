# http://www.pythonforfinance.net/2017/01/21/investment-portfolio-optimisation-with-python/
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import sys


#list of stocks in portfolio
stocks = ['AAPL','MSFT','AMZN','TSLA']

#**** Notes *****
# after creating the dataframe, consider changing the index to everyday in the data range; not just trading days.
# Would also have to fill the data forward and backward. That way you could easily compare stocks and funds to currencies.

data = web.DataReader(stocks,data_source='yahoo',start='01/01/2016')['Adj Close']

#**** NOTES *******
# the sort index line below was added because the dataframe (data) is indexed such that the most recent dates are at the top
# of the dataframe. When you run the pct_change() function, it starts at the top and gives the percent change of the value in
# the above row to that of the current row. (i.e. index +1 value / index value). The result is a negative percent change when
# in fact the percent change was positive between the time periods. It may be much more simple to just multiply the result by -1.

# data.sort_index(ascending=False)
# print(data.head())

#**** NOTES *****
# This may be a good place to reindex the data frame to include all of the dates in the timeline. Would have to backfill and 
# forward fill the data. The below code does not work. It may work if I create a new data frame with the new_index, then fill
# in the values with data where applicable.
# new_index = pd.date_range(start='01/01/2016', end='8/11/2017')[::-1]
# print(new_index[-5:])
# data.reindex(index=new_index,method='bfill')

# this is the print inverse of head()
# print(data[:-5:-1])

#convert daily stock prices into daily returns
returns = data.pct_change()

# print(returns.head())

#calculate mean daily return and covariance of daily returns
mean_daily_returns = returns.mean()

# print(mean_daily_returns.head())

cov_matrix = returns.cov()

# print(cov_matrix.head())

#set number of runs of random portfolio weights
num_portfolios = 25000

#**** NOTES ******
# the first argument (3+len(stocks) is the # of rows | the second argument (num_portfolios) is the # of columns)
# when you print the array it will not represent it's true nature. It will appear as if it has been transposed.

#set up array to hold results
#We have increased the size of the array to hold the weight values for each stock
results = np.zeros((3+len(stocks),num_portfolios))

#*** Added these print options to view the entire array *****
# np.set_printoptions(threshold=np.inf)

for i in range(num_portfolios):
    #select random weights for portfolio holdings
    weights = np.array(np.random.random(4))
    # print(weights)
    #rebalance weights to sum to 1
    weights /= np.sum(weights)
    # print(weights)
    
    #calculate portfolio return and volatility
    portfolio_return = np.sum(mean_daily_returns * weights) * 252
    # print('port return ' + str(portfolio_return))
    # print(portfolio_return)
    portfolio_std_dev = np.sqrt(np.dot(weights.T,np.dot(cov_matrix, weights))) * np.sqrt(252)
    # print('portfolio_std_dev ' + str(portfolio_std_dev))
 
    #store results in results array
    results[0,i] = portfolio_return
    results[1,i] = portfolio_std_dev
    #store Sharpe Ratio (return / volatility) - risk free rate element excluded for simplicity
    results[2,i] = results[0,i] / results[1,i]
    #iterate through the weight vector and add data to results array

    # results[3,i] = weights
    # print(results)
    for j in range(len(weights)):
        results[j+3,i] = weights[j]
    # print(results[:, i])
    # print(results.shape)
    # sys.exit(0)

#convert results array to Pandas DataFrame
# The .T after the data parameter (i.e. results.T) transposes the array in the data frame. Also, the columns argument
# can just accept a list
results_frame = pd.DataFrame(results.T,columns=['ret','stdev','sharpe',stocks[0],stocks[1],stocks[2],stocks[3]])

#locate position of portfolio with highest Sharpe Ratio
max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]
#locate positon of portfolio with minimum standard deviation
min_vol_port = results_frame.iloc[results_frame['stdev'].idxmin()]

#create scatter plot coloured by Sharpe Ratio
plt.scatter(results_frame.stdev,results_frame.ret,c=results_frame.sharpe,cmap='RdYlBu')
plt.xlabel('Volatility')
plt.ylabel('Returns')
plt.colorbar()
#plot red star to highlight position of portfolio with highest Sharpe Ratio
plt.scatter(max_sharpe_port[1],max_sharpe_port[0],marker=(5,1,0),color='r',s=1000)
#plot green star to highlight position of minimum variance portfolio
plt.scatter(min_vol_port[1],min_vol_port[0],marker=(5,1,0),color='g',s=1000)
plt.show()