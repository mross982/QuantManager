import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import sys
import DataAccess as da
import os




def optimize(data_path):
    data = pd.read_pickle(data_path)
 
    #*****Notes****:
    # @data is a pandas.core.frame.dataframe with a (# of dates [rows], len(stocks) [cols]) diminsion. Dates do not
    # include closed market days. FYI, each year is 251 trading days.

    #convert daily stock prices into daily returns
    returns = data.pct_change()

    #calculate mean daily return and covariance of daily returns
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()
     
    #set number of runs of random portfolio weights
    num_portfolios = 25000
     
    #****Notes****: 
    # @results is a np.zeros array with (3 plus the number of stocks) rows and 25000 columns
    #  -notice how flat the array is.

    #set up array to hold results
    #We have increased the size of the array to hold the weight values for each stock
    results = np.zeros((3+len(returns.columns),num_portfolios))
     
    for i in range(num_portfolios):
        #*** Notes ***: weights is a list of floats from 0 to 1 that when added together equals 1.
        # the length of the list is equal to the number of options in the account file. 

        #select random weights for portfolio holdings
        weights = np.array(np.random.random(len(returns.columns)))
        #rebalance weights to sum to 1
        weights /= np.sum(weights)
     
        #calculate portfolio return and volatility
        portfolio_return = np.sum(mean_daily_returns * weights) * 252
        portfolio_std_dev = np.sqrt(np.dot(weights.T,np.dot(cov_matrix, weights))) * np.sqrt(252)
     
        #store results in results array
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev
        #store Sharpe Ratio (return / volatility) - risk free rate element excluded for simplicity
        results[2,i] = results[0,i] / results[1,i]
        #iterate through the weight vector and add data to results array
        for j in range(len(weights)):
            results[j+3,i] = weights[j]
    
    #convert results array to Pandas DataFrame
    results_frame = pd.DataFrame(results.T,columns=['ret','stdev','sharpe',returns.columns[0],returns.columns[1],returns.columns[2],returns.columns[3], \
        returns.columns[4], returns.columns[5], returns.columns[6], returns.columns[7], returns.columns[8], returns.columns[9], returns.columns[10], \
        returns.columns[11], returns.columns[12]])
     
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

if __name__ == '__main__':


    # For the time being, I plan to just analyze each account separately. Once done, I can come back
    # and find the optimal way to analyze data from multiple sources.
    # this code should end up in DataAccess where it would return a dataframe
    c_dataobj = da.DataAccess(da.DataSource.YAHOO)
    ls_acctdata = c_dataobj.get_info_from_account(c_dataobj.accountFiles)
    
    ls_symbols = []
    symbols = []

    for acct in ls_acctdata:
        ls_symbols = acct[2:]
        if datatype == da.DataType.MUTUAL_FUND:
            for x in ls_symbols:
                symbols += x.keys()
        else:
            symbols = ls_symbols

        account = str(acct[0])
        path = os.path.join(c_dataobj.datafolder, account + '.pkl')
        optimize(path)
        path = ''


    
