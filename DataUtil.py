import math
import datetime as dt
import numpy as np
from math import sqrt
import pandas as pd
from copy import deepcopy
import random as rand
import DataAccess as da
import numpy as np
import optimize
import sys


class normalize(object):
    
    ANNUALIZE = 252


def returnize0(nds):
    """
    @summary Computes stepwise (usually daily) returns relative to 0, where
    0 implies no change in value.
    @return the array is revised in place
    """
    if type(nds) == type(pd.DataFrame()):
        nds = (nds / nds.shift(1)) - 1.0
        nds = nds.fillna(0.0)
        return nds

    s= np.shape(nds)
    if len(s)==1:
        nds=np.expand_dims(nds,1)
    nds[1:, :] = (nds[1:, :] / nds[0:-1]) - 1
    nds[0, :] = np.zeros(nds.shape[1])
    return nds


def returnize1(nds):
    """
    @summary Computes stepwise (usually daily) returns relative to 1, where
    1 implies no change in value.
    @param nds: the array to fill backward
    @return the array is revised in place
    """
    if type(nds) == type(pd.DataFrame()):
        nds = nds / nds.shift(1)
        nds = nds.fillna(1.0)
        return nds

    s= np.shape(nds)
    if len(s)==1:
        nds=np.expand_dims(nds,1)
    nds[1:, :] = (nds[1:, :]/nds[0:-1])
    nds[0, :] = np.ones(nds.shape[1])
    return nds


def get_risk_ret( d_returns, risk_free=0.00 ):
    """
    @summary Used in visuals.sub_efficientfrontier to plot the avg_return & std deviation of every fund
    @param rets: 1d numpy array or fund list of daily returns (centered on 0)
    @param risk_free: risk free returns, default is 0%
    @return Annualized rate of return, not converted to percent
    """

    rets = returnize0(d_returns)

    f_dev = np.std( rets, axis=0 )
    f_mean = np.mean( rets, axis=0 )

    if rets.shape[0] >= 252:
        np_dev = f_dev * np.sqrt(normalize.ANNUALIZE)
        np_ret = f_mean * normalize.ANNUALIZE
    else:
        np_dev = f_dev * sqrt(len(rets))
        np_ret = f_mean * len(rets)

    df = pd.concat([np_ret, np_dev], axis=1) # convert two arrays to single dataframe
    df.columns = ['exp_return', 'std_dev']

    return df

def frontier_target(avg_rets):
    '''
    @Summary: sets the target portfolio to 70% of the total possible returns
    '''
    target_ret = avg_rets.quantile(0.7)
    return target_ret

def get_frontier_portfolios(df_data):
    '''
    @ summary: returns a dataframe of four portfolios (max return, targ return, tangency, min var)
    and two columns with expected return and standard deviation values to be used to create an efficient frontier.
    '''
    df = pd.DataFrame()

    if len(df_data) >= 252:
        annualize = normalize.ANNUALIZE
    else:
        annualize = len(df_data)

    returns = returnize0(df_data) # get daily returns from dataframe
    avg_rets = returns.mean() # get mean of all daily returns

    # Add Max values
    target_ret = avg_rets.nlargest(1) # largest possible target return

    ret = target_ret[0]
    exp_return = ret * annualize
    df_target = returns[target_ret.index[0]]
    std_dev = df_target.std()
    std_dev = std_dev * sqrt(annualize)
    port1 = 'Max_return'
    df = df.append({'Portfolio': port1, 'exp_return': exp_return, 'std_dev': std_dev}, ignore_index=True)

    # Add Target Values
    target_ret = frontier_target(avg_rets)  # get the target return
    weights, exp_return, std_dev = optimize.portfolio_optimizer.target_opt( returns, target_ret ) # optimize
    exp_return = exp_return * annualize
    std_dev = std_dev * sqrt(annualize)
    port2 = 'Target_return'
    df = df.append({'Portfolio': port2, 'exp_return': exp_return, 'std_dev': std_dev}, ignore_index=True)

    # Add tangency values
    weights, exp_return, std_dev = optimize.portfolio_optimizer.tangency_opt(returns)
    exp_return = exp_return * annualize
    std_dev = std_dev * sqrt(annualize)
    port3 = 'Tangency'
    df = df.append({'Portfolio': port3, 'exp_return': exp_return, 'std_dev': std_dev}, ignore_index=True)

    # Add min variance values
    weights, exp_return, std_dev = optimize.portfolio_optimizer.min_variance(returns)
    exp_return = exp_return * annualize
    std_dev = std_dev * sqrt(annualize)
    port4 = 'Min_variance'
    df = df.append({'Portfolio': port4, 'exp_return': exp_return, 'std_dev': std_dev}, ignore_index=True)

    return df


def get_frontier(df_data):
    '''
    *** Under Construction: returns a dataframe of 20 progressive expected return efficient porfolios with
    two columns with expected return and standard deviation values to be used to create an efficient frontier.
    '''
    df = pd.DataFrame()

    if len(df_data) >= 252:
        annualize = normalize.ANNUALIZE
    else:
        annualize = len(df_data)

    returns = returnize0(df_data) # get daily returns from dataframe
    avg_rets = returns.mean() # get mean of all daily returns

    
    max_ret = avg_rets.nlargest(1) # largest possible target return
    max_ret = max_ret[0]
    for x in range(20):
        target_ret = max_ret - ((x/20) * max_ret)
        weights, exp_return, std_dev = optimize.portfolio_optimizer.target_opt( returns, target_ret ) # optimize
        exp_return = exp_return * annualize
        std_dev = std_dev * sqrt(annualize)
        df = df.append({'exp_return': exp_return, 'std_dev': std_dev}, ignore_index=True)
        x += 1

    return df



def relative_measures():
    '''
    Under constuction: used after optimization and should be included in the same json file to be shown in the same table.
    @summary: calculates alpha, beta, r squared, momentum and volitility of a fund and it's corresponding benchmark.
    
    '''
    # Grab time series data for 5-year history for the stock (here AAPL)
    # and for S&P-500 Index
    sdate = date(2008,12,31)
    edate = date(2013,12,31)
    df = DataReader('WFM','yahoo',sdate,edate)
    dfb = DataReader('^GSPC','yahoo',sdate,edate)

    # create a time-series of monthly data points
    rts = df.resample('M',how='last')
    rbts = dfb.resample('M',how='last')
    dfsm = pd.DataFrame({'s_adjclose' : rts['Adj Close'],
                            'b_adjclose' : rbts['Adj Close']},
                            index=rts.index)

    # compute returns
    dfsm[['s_returns','b_returns']] = dfsm[['s_adjclose','b_adjclose']]/\
        dfsm[['s_adjclose','b_adjclose']].shift(1) -1
    dfsm = dfsm.dropna()
    covmat = np.cov(dfsm["s_returns"],dfsm["b_returns"])

    # calculate measures now
    beta = covmat[0,1]/covmat[1,1]
    alpha= np.mean(dfsm["s_returns"])-beta*np.mean(dfsm["b_returns"])

    # r_squared     = 1. - SS_res/SS_tot
    ypred = alpha + beta * dfsm["b_returns"]
    SS_res = np.sum(np.power(ypred-dfsm["s_returns"],2))
    SS_tot = covmat[0,0]*(len(dfsm)-1) # SS_tot is sample_variance*(n-1)
    r_squared = 1. - SS_res/SS_tot
    # 5- year volatiity and 1-year momentum
    volatility = np.sqrt(covmat[0,0])
    momentum = np.prod(1+dfsm["s_returns"].tail(12).values) -1

    # annualize the numbers
    prd = 12. # used monthly returns; 12 periods to annualize
    alpha = alpha*prd
    volatility = volatility*np.sqrt(prd)

    # print(beta,alpha, r_squared, volatility, momentum)


def moving_averages(df_data):
    '''
    Under construction: calculates the rolling average of a given fund (i.e. must be a data panel)
    then returns two panels; short rolling average and long rolling average.
    '''
    if isinstance(df_data, 'dataframe'):
        for fund in df_data.columns:
            # calculate the 20 day and 100 day moving averages
            short_rolling = fund.rolling(window=20).mean()
            long_rolling = fund.rolling(window=100).mean()
            f_name = fund.column # need the column header
            fig = plot.figure()
            ax = fig.add_subplot(1,1,1)
            ax.plot(fund.index, fund, label=fname)
            ax.plot(short_rolling.index, short_rolling, label='20 days rolling')
            ax.plot(long_rolling.index, long_rolling, label='100 days rolling')
            ax.set_xlabel('Date')
            ax.set_ylabel('Adjusted closing price ($)')
            ax.legend()
            plt.show


def remove_duplicates(ls_values):
    '''
    @summary: takes a list with possible duplicate values and returns a list with no duplicate values.
    '''
    output = []
    seen = set()
    for value in ls_values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output
# ******************** UNUSED EXTRA CODE **********************************************************************

def daily(lfFunds):
    """
    @summary Computes daily returns centered around 0
    @param funds: A time series containing daily fund values
    @return an array of daily returns
    """
    if type(lfFunds) == type(pd.Series()):
        ldt_timestamps = du.getNYSEdays(lfFunds.index[0], lfFunds.index[-1], dt.timedelta(hours=16))
        lfFunds = lfFunds.reindex(index=ldt_timestamps, method='ffill')
    nds = np.asarray(deepcopy(lfFunds))
    s= np.shape(nds)
    if len(s)==1:
        nds=np.expand_dims(nds,1)
    returnize0(nds)
    return(nds)

def daily1(lfFunds):
    """
    @summary Computes daily returns centered around 1
    @param funds: A time series containing daily fund values
    @return an array of daily returns
    """
    nds = np.asarray(deepcopy(lfFunds))
    s= np.shape(nds)
    if len(s)==1:
        nds=np.expand_dims(nds,1)
    returnize1(nds)
    return(nds)

def monthly(funds):
    """
    @summary Computes monthly returns centered around 0
    @param funds: A time series containing daily fund values
    @return an array of monthly returns
    """
    funds2 = []
    last_last_month = -1
    years = qsdateutil.getYears(funds)
    for year in years:
        months = qsdateutil.getMonths(funds, year)
        for month in months:
            last_this_month = qsdateutil.getLastDay(funds, year, month)
            if last_last_month == -1 :
                last_last_month=qsdateutil.getFirstDay(funds, year, month)
            if type(funds).__name__=='TimeSeries':
                funds2.append(funds[last_this_month]/funds[last_last_month]-1)
            else:
                funds2.append(funds.xs(last_this_month)/funds.xs(last_last_month)-1)
            last_last_month = last_this_month
    return(funds2)

def average_monthly(funds):
    """
    @summary Computes average monthly returns centered around 0
    @param funds: A time series containing daily fund values
    @return an array of average monthly returns
    """
    rets = daily(funds)
    ret_i = 0
    years = qsdateutil.getYears(funds)
    averages = []
    for year in years:
        months = qsdateutil.getMonths(funds, year)
        for month in months:
            avg = 0
            count = 0
            days = qsdateutil.getDays(funds, year, month)
            for day in days:
                avg += rets[ret_i]
                ret_i += 1
                count += 1
            averages.append(float(avg) / count)
    return(averages)    

def fillforward(nds):
    """
    @summary Removes NaNs from a 2D array by scanning forward in the 
    1st dimension.  If a cell is NaN, the value above it is carried forward.
    @param nds: the array to fill forward
    @return the array is revised in place
    """
    for col in range(nds.shape[1]):
        for row in range(1, nds.shape[0]):
            if math.isnan(nds[row, col]):
                nds[row, col] = nds[row-1, col]

def fillbackward(nds):
    """
    @summary Removes NaNs from a 2D array by scanning backward in the 
    1st dimension.  If a cell is NaN, the value above it is carried backward.
    @param nds: the array to fill backward
    @return the array is revised in place
    """
    for col in range(nds.shape[1]):
        for row in range(nds.shape[0] - 2, -1, -1):
            if math.isnan(nds[row, col]):
                nds[row, col] = nds[row+1, col]





def priceize1(nds):
    """
    @summary Computes stepwise (usually daily) returns relative to 1, where
    1 implies no change in value.
    @param nds: the array to fill backward
    @return the array is revised in place
    """
    
    nds[0, :] = 100 
    for i in range(1, nds.shape[0]):
        nds[i, :] = nds[i-1, :] * nds[i, :]
    
    
def logreturnize(nds):
    """
    @summary Computes stepwise (usually daily) logarithmic returns.
    @param nds: the array to fill backward
    @return the array is revised in place
    """
    returnize1(nds)
    nds = np.log(nds)
    return nds

def get_winning_days( rets):
    """
    @summary Returns the percentage of winning days of the returns.
    @param rets: 1d numpy array or fund list of daily returns (centered on 0)
    @return Percentage of winning days
    """
    negative_rets = []
    for i in rets:
        if(i<0):
            negative_rets.append(i)
    return 100 * (1 - float(len(negative_rets)) / float(len(rets)))

def get_max_draw_down(ts_vals):
    """
    @summary Returns the max draw down of the returns.
    @param ts_vals: 1d numpy array or fund list
    @return Max draw down
    """
    MDD = 0
    DD = 0
    peak = -99999
    for value in ts_vals:
        if (value > peak):
            peak = value
        else:
            DD = (peak - value) / peak
        if (DD > MDD):
            MDD = DD
    return -1*MDD

def get_sortino_ratio( rets, risk_free=0.00 ):
    """
    @summary Returns the daily Sortino ratio of the returns.
    @param rets: 1d numpy array or fund list of daily returns (centered on 0)
    @param risk_free: risk free return, default is 0%
    @return Sortino Ratio, computed off daily returns
    """
    rets = np.asarray(rets)
    f_mean = np.mean( rets, axis=0 )
    negative_rets = rets[rets < 0]
    f_dev = np.std( negative_rets, axis=0 )
    f_sortino = (f_mean*252 - risk_free) / (f_dev * np.sqrt(252))
    return f_sortino


    

def get_ror_annual( rets ):
    """
    @summary Returns the rate of return annualized.  Assumes len(rets) is number of days.
    @param rets: 1d numpy array or list of daily returns
    @return Annualized rate of return, not converted to percent
    """

    f_inv = 1.0
    for f_ret in rets:
        f_inv = f_inv * f_ret
    
    f_ror_ytd = f_inv - 1.0    
    
    print (' RorYTD =', f_inv, 'Over days:', len(rets) )
    
    return ( (1.0 + f_ror_ytd)**( 1.0/(len(rets)/252.0) ) ) - 1.0

def getPeriodicRets( dmPrice, sOffset ):
    """
    @summary Reindexes a DataMatrix price array and returns the new periodic returns.
    @param dmPrice: DataMatrix of stock prices
    @param sOffset: Offset string to use, choose from _offsetMap in pandas/core/datetools.py
                    e.g. 'EOM', 'WEEKDAY', 'W@FRI', 'A@JAN'.  Or use a pandas DateOffset.
    """    
    
    # Could possibly use DataMatrix.asfreq here """
    # Use pandas DateRange to create the dates we want, use 4:00 """
    drNewRange = DateRange(dmPrice.index[0], dmPrice.index[-1], timeRule=sOffset)
    drNewRange += DateOffset(hours=16)
    
    dmPrice = dmPrice.reindex( drNewRange, method='ffill' )  

    returnize1( dmPrice.values )
    
    # Do not leave return of 1.0 for first time period: not accurate """
    return dmPrice[1:]

def getReindexedRets( rets, l_period ):
    """
    @summary Reindexes returns using the cumulative product. E.g. if returns are 1.5 and 1.5, a period of 2 will
             produce a 2-day return of 2.25.  Note, these must be returns centered around 1.
    @param rets: Daily returns of the various stocks (using returnize1)
    @param l_period: New target period.
    @note: Note that this function does not track actual weeks or months, it only approximates with trading days.
           You can use 5 for week, or 21 for month, etc.
    """    
    naCumData = np.cumprod(rets, axis=0)

    lNewRows =(rets.shape[0]-1) / (l_period)
    # We compress data into height / l_period + 1 new rows """
    for i in range( lNewRows ):
        lCurInd = -1 - i*l_period
        # Just hold new data in same array"""
        # new return is cumprod on day x / cumprod on day x-l_period """
        start=naCumData[lCurInd - l_period, :]
        naCumData[-1 - i, :] = naCumData[lCurInd, :] / start 
        # Select new returns from end of cumulative array """
    
    return naCumData[-lNewRows:, ]

def getRetRange( rets, naLower, naUpper, naExpected = "False", s_type = "long"):
    """
    @summary Returns the range of possible returns with upper and lower bounds on the portfolio participation
    @param rets: Expected returns
    @param naLower: List of lower percentages by stock
    @param naUpper: List of upper percentages by stock
    @return tuple containing (fMin, fMax)
    """    
    
    # Calculate theoretical minimum and maximum theoretical returns """
    fMin = 0
    fMax = 0

    rets = deepcopy(rets)
    
    if naExpected == "False":
        naExpected = np.average( rets, axis=0 )
        
    na_signs = np.sign(naExpected)
    indices,  = np.where(na_signs == 0)
    na_signs[indices] = 1
    if s_type == "long":
        na_signs = np.ones(len(na_signs))
    elif s_type == "short":
        na_signs = np.ones(len(na_signs))*(-1)
    
    rets = na_signs*rets
    naExpected = na_signs*naExpected

    naSortInd = naExpected.argsort()
    
    # First add the lower bounds on portfolio participation """ 
    for i, fRet in enumerate(naExpected):
        fMin = fMin + fRet*naLower[i]
        fMax = fMax + fRet*naLower[i]


    # Now calculate minimum returns"""
    # allocate the max possible in worst performing equities """
    # Subtract min since we have already counted it """
    naUpperAdd = naUpper - naLower
    fTotalPercent = np.sum(naLower[:])
    for i, lInd in enumerate(naSortInd):
        fRetAdd = naUpperAdd[lInd] * naExpected[lInd]
        fTotalPercent = fTotalPercent + naUpperAdd[lInd]
        fMin = fMin + fRetAdd
        # Check if this additional percent puts us over the limit """
        if fTotalPercent > 1.0:
            fMin = fMin - naExpected[lInd] * (fTotalPercent - 1.0)
            break
    
    # Repeat for max, just reverse the sort, i.e. high to low """
    naUpperAdd = naUpper - naLower
    fTotalPercent = np.sum(naLower[:])
    for i, lInd in enumerate(naSortInd[::-1]):
        fRetAdd = naUpperAdd[lInd] * naExpected[lInd]
        fTotalPercent = fTotalPercent + naUpperAdd[lInd]
        fMax = fMax + fRetAdd
        
        # Check if this additional percent puts us over the limit """
        if fTotalPercent > 1.0:
            fMax = fMax - naExpected[lInd] * (fTotalPercent - 1.0)
            break

    return (fMin, fMax)


