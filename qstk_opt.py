import math
import datetime as dt
import numpy as np
from math import sqrt
import pandas as pd
from copy import deepcopy
import random as rand
import DataAccess as da



def getOptPort(rets, f_target, l_period=1, naLower=None, naUpper=None, lNagDebug=0):
    """
    @summary Returns the Markowitz optimum portfolio for a specific return.
    @param rets: Daily returns of the various stocks (using returnize1)
    @param f_target: Target return, i.e. 0.04 = 4% per period
    @param l_period: Period to compress the returns to, e.g. 7 = weekly
    @param naLower: List of floats which corresponds to lower portfolio% for each stock
    @param naUpper: List of floats which corresponds to upper portfolio% for each stock 
    @return tuple: (weights of portfolio, min possible return, max possible return)
    """
    
    # Attempt to import library """
    try:
        pass
        import nagint as nag
    except ImportError:
        print('Could not import NAG library')
        print('make sure nagint.so is in your python path')
        return ([], 0, 0)
    
    # Get number of stocks """
    lStocks = rets.shape[1]
    
    # If period != 1 we need to restructure the data """
    if( l_period != 1 ):
        rets = getReindexedRets( rets, l_period)
    
    # Calculate means and covariance """
    naAvgRets = np.average( rets, axis=0 )
    naCov = np.cov( rets, rowvar=False )
    
    # Special case for None == f_target"""
    # simply return average returns and cov """
    if( f_target is None ):
        return naAvgRets, np.std(rets, axis=0)
    
    # Calculate upper and lower limits of variables as well as constraints """
    if( naUpper is None ): 
        naUpper = np.ones( lStocks )  # max portfolio % is 1
    
    if( naLower is None ): 
        naLower = np.zeros( lStocks ) # min is 0, set negative for shorting
    # Two extra constraints for linear conditions"""
    # result = desired return, and sum of weights = 1 """
    naUpper = np.append( naUpper, [f_target, 1.0] )
    naLower = np.append( naLower, [f_target, 1.0] )
    
    # Initial estimate of portfolio """
    naInitial = np.array([1.0/lStocks]*lStocks)
    
    # Set up constraints matrix"""
    # composed of expected returns in row one, unity row in row two """
    naConstraints = np.vstack( (naAvgRets, np.ones(lStocks)) )

    # Get portfolio weights, last entry in array is actually variance """
    try:
        naReturn = nag.optPort( naConstraints, naLower, naUpper, \
                                      naCov, naInitial, lNagDebug )
    except RuntimeError:
        print('NAG Runtime error with target: %.02lf'%(f_target))
        return ( naInitial, sqrt( naCov[0][0] ) )  
    #return semi-junk to not mess up the rest of the plot

    # Calculate stdev of entire portfolio to return"""
    # what NAG returns is slightly different """
    fPortDev = np.std( np.dot(rets, naReturn[0,0:-1]) )
    
    # Show difference between above stdev and sqrt NAG covariance"""
    # possibly not taking correlation into account """
    #print fPortDev / sqrt(naReturn[0, -1]) 

    # Return weights and stdDev of portfolio."""
    #  note again the last value of naReturn is NAG's reported variance """
    return (naReturn[0, 0:-1], fPortDev)

def OptPort( naData, fTarget, naLower=None, naUpper=None, naExpected=None, s_type = "long"):
    """
    @summary Returns the Markowitz optimum portfolio for a specific return.
    @param naData: Daily returns of the various stocks (using returnize1)
    @param fTarget: Target return, i.e. 0.04 = 4% per period
    @param lPeriod: Period to compress the returns to, e.g. 7 = weekly
    @param naLower: List of floats which corresponds to lower portfolio% for each stock
    @param naUpper: List of floats which corresponds to upper portfolio% for each stock 
    @return tuple: (weights of portfolio, min possible return, max possible return)
    """
    ''' Attempt to import library '''
    try:
        pass
        from cvxopt import matrix
        from cvxopt.blas import dot
        from cvxopt.solvers import qp, options

    except ImportError:
        print('Could not import CVX library')
        raise
    
    ''' Get number of stocks '''
    length = naData.shape[1]
    b_error = False

    naLower = deepcopy(naLower)
    naUpper = deepcopy(naUpper)
    naExpected = deepcopy(naExpected)
    
    # Assuming AvgReturns as the expected returns if parameter is not specified
    if (naExpected==None):
        naExpected = np.average( naData, axis=0 )

    na_signs = np.sign(naExpected)
    indices,  = np.where(na_signs == 0)
    na_signs[indices] = 1
    if s_type == "long":
        na_signs = np.ones(len(na_signs))
    elif s_type == "short":
        na_signs = np.ones(len(na_signs))*(-1)
    
    naData = na_signs*naData
    naExpected = na_signs*naExpected

    # Covariance matrix of the Data Set
    naCov=np.cov(naData, rowvar=False)
    
    # If length is one, just return 100% single symbol
    if length == 1:
        return (list(na_signs), np.std(naData, axis=0)[0], False)
    if length == 0:
        return ([], [0], False)
    # If we have 0/1 "free" equity we can't optimize
    # We just use     limits since we are stuck with 0 degrees of freedom
    
    ''' Special case for None == fTarget, simply return average returns and cov '''
    if( fTarget is None ):
        return (naExpected, np.std(naData, axis=0), b_error)
    
    # Upper bound of the Weights of a equity, If not specified, assumed to be 1.
    if(naUpper is None):
        naUpper= np.ones(length)
    
    # Lower bound of the Weights of a equity, If not specified assumed to be 0 (No shorting case)
    if(naLower is None):
        naLower= np.zeros(length)

    if sum(naLower) == 1:
        fPortDev = np.std(np.dot(naData, naLower))
        return (naLower, fPortDev, False)

    if sum(naUpper) == 1:
        fPortDev = np.std(np.dot(naData, naUpper))
        return (naUpper, fPortDev, False)
    
    naFree = naUpper != naLower
    if naFree.sum() <= 1:
        lnaPortfolios = naUpper.copy()
        
        # If there is 1 free we need to modify it to make the total
        # Add up to 1
        if naFree.sum() == 1:
            f_rest = naUpper[~naFree].sum()
            lnaPortfolios[naFree] = 1.0 - f_rest
            
        lnaPortfolios = na_signs * lnaPortfolios
        fPortDev = np.std(np.dot(naData, lnaPortfolios))
        return (lnaPortfolios, fPortDev, False)

    # Double the covariance of the diagonal elements for calculating risk.
    for i in range(length):
        naCov[i][i]=2*naCov[i][i]

    # Note, returns are modified to all be long from here on out
    (fMin, fMax) = getRetRange(False, naLower, naUpper, naExpected, "long") 
    #print (fTarget, fMin, fMax)
    if fTarget<fMin or fTarget>fMax:
        print("Target not possible", fTarget, fMin, fMax)
        b_error = True

    naLower = naLower*(-1)
 
    # Setting up the parameters for the CVXOPT Library, it takes inputs in Matrix format.
    '''
    The Risk minimization problem is a standard Quadratic Programming problem according to the Markowitz Theory.
    '''
    S=matrix(naCov)
    #pbar=matrix(naExpected)
    naLower.shape=(length,1)
    naUpper.shape=(length,1)
    naExpected.shape = (1,length)
    zeo=matrix(0.0,(length,1))
    I = np.eye(length)
    minusI=-1*I
    G=matrix(np.vstack((I, minusI)))
    h=matrix(np.vstack((naUpper, naLower)))
    ones=matrix(1.0,(1,length)) 
    A=matrix(np.vstack((naExpected, ones)))
    b=matrix([float(fTarget),1.0])

    # Optional Settings for CVXOPT
    options['show_progress'] = False
    options['abstol']=1e-25
    options['reltol']=1e-24
    options['feastol']=1e-25
    

    # Optimization Calls
    # Optimal Portfolio
    try:
            lnaPortfolios = qp(S, -zeo, G, h, A, b)['x']
    except:
        b_error = True

    if b_error == True:
        print("Optimization not Possible")
        na_port = naLower*-1
        if sum(na_port) < 1:
            if sum(naUpper) == 1:
                na_port = naUpper
            else:
                i=0
                while(sum(na_port)<1 and i<25):
                    naOrder = naUpper - na_port
                    i = i+1
                    indices = np.where(naOrder > 0)
                    na_port[indices]= na_port[indices] + (1-sum(na_port))/len(indices[0]) 
                    naOrder = naUpper - na_port
                    indices = np.where(naOrder < 0)
                    na_port[indices]= naUpper[indices]
            
        lnaPortfolios = matrix(na_port)

    lnaPortfolios = (na_signs.reshape(-1,1) * lnaPortfolios).reshape(-1)
    # Expected Return of the Portfolio
    # lfReturn = dot(pbar, lnaPortfolios)
    
    # Risk of the portfolio
    fPortDev = np.std(np.dot(naData, lnaPortfolios))
    return (lnaPortfolios, fPortDev, b_error)


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


def _create_dict(df_rets, lnaPortfolios):

    allocations = {}
    for i, sym in enumerate(df_rets.columns):
        allocations[sym] = lnaPortfolios[i]

    return allocations

def optimizePortfolio(df_rets, list_min, list_max, list_price_target, 
                      target_risk, direction="long"):
    
    naLower = np.array(list_min)
    naUpper = np.array(list_max)
    naExpected = np.array(list_price_target)      

    b_same_flag = np.all( naExpected == naExpected[0])
    if b_same_flag and (naExpected[0] == 0):
        naExpected = naExpected + 0.1
    if b_same_flag:
        na_randomness = np.ones(naExpected.shape)
        target_risk = 0
        for i in range(len(na_randomness)):
            if i%2 ==0:
                na_randomness[i] = -1
        naExpected = naExpected + naExpected*0.0000001*na_randomness

    (fMin, fMax) = getRetRange( df_rets.values, naLower, naUpper, 
                                naExpected, direction)
    
    # Try to avoid intractible endpoints due to rounding errors """
    fMin += abs(fMin) * 0.00000000001 
    fMax -= abs(fMax) * 0.00000000001
    
    if target_risk == 1:
        (naPortWeights, fPortDev, b_error) = OptPort( df_rets.values, fMax, naLower, naUpper, naExpected, direction)
        allocations = _create_dict(df_rets, naPortWeights)
        return {'allocations': allocations, 'std_dev': fPortDev, 'expected_return': fMax, 'error': b_error}

    fStep = (fMax - fMin) / 50.0

    lfReturn =  [fMin + x * fStep for x in range(51)]
    lfStd = []
    lnaPortfolios = []
    
    for fTarget in lfReturn: 
        (naWeights, fStd, b_error) = OptPort( df_rets.values, fTarget, naLower, naUpper, naExpected, direction)
        if b_error == False:
            lfStd.append(fStd)
            lnaPortfolios.append( naWeights )
        else:
            # Return error on ANY failed optimization
            allocations = _create_dict(df_rets, np.zeros(df_rets.shape[1]))
            return {'allocations': allocations, 'std_dev': 0.0, 
                    'expected_return': fMax, 'error': True}

    if len(lfStd) == 0:
        (naPortWeights, fPortDev, b_error) = OptPort( df_rets.values, fMax, naLower, naUpper, naExpected, direction)
        allocations = _create_dict(df_rets, naPortWeights)
        return {'allocations': allocations, 'std_dev': fPortDev, 'expected_return': fMax, 'error': True}

    f_return = lfReturn[lfStd.index(min(lfStd))]

    if target_risk == 0:
        naPortWeights=lnaPortfolios[lfStd.index(min(lfStd))]    
        allocations = _create_dict(df_rets, naPortWeights)
        return {'allocations': allocations, 'std_dev': min(lfStd), 'expected_return': f_return, 'error': False}

    # If target_risk = 0.5, then return the one with maximum sharpe
    if target_risk == 0.5:
        lf_return_new = np.array(lfReturn)
        lf_std_new = np.array(lfStd)
        lf_std_new = lf_std_new[lf_return_new >= f_return]
        lf_return_new = lf_return_new[lf_return_new >= f_return]
        na_sharpe = lf_return_new / lf_std_new

        i_index_max_sharpe, = np.where(na_sharpe == max(na_sharpe))
        i_index_max_sharpe = i_index_max_sharpe[0]
        fTarget = lf_return_new[i_index_max_sharpe]
        (naPortWeights, fPortDev, b_error) = OptPort(df_rets.values, fTarget, naLower, naUpper, naExpected, direction)
        allocations = _create_dict(df_rets, naPortWeights)
        return {'allocations': allocations, 'std_dev': fPortDev, 'expected_return': fTarget, 'error': b_error}

    # Otherwise try to hit custom target between 0-1 min-max return
    fTarget = f_return + ((fMax - f_return) * target_risk)

    (naPortWeights, fPortDev, b_error) = OptPort( df_rets.values, fTarget, naLower, naUpper, naExpected, direction)
    allocations = _create_dict(df_rets, naPortWeights)
    return {'allocations': allocations, 'std_dev': fPortDev, 'expected_return': fTarget, 'error': b_error}
    

def getFrontier( rets, lRes=100, fUpper=0.2, fLower=0.00):
    """
    @summary Generates an efficient frontier based on average returns.
    @param rets: Array of returns to use
    @param lRes: Resolution of the curve, default=100
    @param fUpper: Upper bound on portfolio percentage
    @param fLower: Lower bound on portfolio percentage
    @return tuple containing (lf_ret, lfStd, lnaPortfolios)
            lf_ret: List of returns provided by each point
            lfStd: list of standard deviations provided by each point
            lnaPortfolios: list of numpy arrays containing weights for each portfolio
    """    
    
    # Limit/enforce percent participation """
    naUpper = np.ones(rets.shape[1]) * fUpper
    naLower = np.ones(rets.shape[1]) * fLower
    
    (fMin, fMax) = getRetRange( rets, naLower, naUpper )
    
    # Try to avoid intractible endpoints due to rounding errors """
    fMin *= 1.0000001 
    fMax *= 0.9999999

    # Calculate target returns from min and max """
    lf_ret = []
    for i in range(lRes):
        lf_ret.append( (fMax - fMin) * i / (lRes - 1) + fMin )
    
    
    lfStd = []
    lnaPortfolios = []
    
    # Call the function lRes times for the given range, use 1 for period """
    for f_target in lf_ret: 
        (naWeights, fStd) = getOptPort( rets, f_target, 1, \
                               naUpper=naUpper, naLower=naLower )
        lfStd.append(fStd)
        lnaPortfolios.append( naWeights )
    
    # plot frontier """
    plt.plot( lfStd, lf_ret )
    plt.plot( np.std( rets, axis=0 ), np.average( rets, axis=0 ), \
                                                  'g+', markersize=10 ) 
    plt.show()
    
    return (lf_ret, lfStd, lnaPortfolios)
