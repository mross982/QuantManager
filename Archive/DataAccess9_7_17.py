'''
Created on Jan 15, 2013

@author: Michael Williams
@contact: mross982@gmail.com
@summary: Data Access python library.

'''
import numpy as np
import pandas as pd
import tempfile
import os
import re
import csv
import pickle as pkl
import time
import datetime as dt
import tempfile
import copy
import sys
from itertools import islice

class DataItem (object):
    DATE = "Date"
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"
    VOLUME = "Volume"
    ACTUAL_CLOSE = "ActualClose"
    ADJUSTED_CLOSE = "AdjClose"
    DESCRIPTIVE_INFO = "DescriptiveInfo"

class DataSource(object):
    GOOGLE = 'Google' # stock/bond data
    YAHOO = 'Yahoo'  # mutual fund/stock/bond data
    CRYPTOCOMPARE = 'Cryptocompare' # daily crypto data
    POLONIEX = 'Poloniex' # intra day crypto data
    MARKETCAP = 'Marketcap' # market data crypto

class DataType(object):
    MUTUAL_FUND = 'Mutual Fund'
    OPTION = 'Option'  #either stock or bond
    CRYPTO = 'Cryptocurrency'

class DataAccess(object):
    '''
    @summary: This class is used to access all the symbol data. It readin in pickled numpy arrays converts them into appropriate pandas objects
    and returns that object. The {main} function currently demonstrates use.
    @note: The earliest time for which this works is platform dependent because the python date functionality is platform dependent.
    '''
    def __init__(self, sourcein=DataSource.GOOGLE, s_datapath=None,
                 s_scratchpath=None, cachestalltime=12, verbose=False):
        '''
        @param sourcestr: Specifies the source of the data. Initializes paths based on source.
        @note: No data is actually read in the constructor. Only paths for the source are initialized
        @param: Scratch defaults to a directory in /tmp/QSScratch
        '''
        # self.accountdir = list()
        self.folderList = list()
        self.folderSubList = list()
        self.cachestalltime = cachestalltime
        self.fileExtensionToRemove = ".pkl"

        try:
            self.rootdir = os.environ['QSREPO']
        except:
            self.rootdir = os.path.realpath(__file__)
        try:
            self.datadir = os.environ['QSDATA']
            try:
                self.scratchdir = os.environ['QSSCRATCH']
            except:
                self.scratchdir = os.path.join(tempfile.gettempdir(), 'QSScratch')
        except:
            if s_datapath != None:
                self.datadir = s_datapath
                if s_scratchpath != None:
                    self.scratchdir = s_scratchpath
                else:
                    self.scratchdir = os.path.join(tempfile.gettempdir(), 'QSScratch')
            else:
                self.datadir = os.path.join(self.rootdir, 'QSData')
                self.scratchdir = os.path.join(tempfile.gettempdir(), 'QSScratch')

        try:
            self.accountdir = os.environ['ACCOUNTS']
        except:
            self.accountdir = os.path.join(self.rootdir, 'Accounts\\')
  
        if verbose:
            print("Scratch Directory: ", self.scratchdir)
            print("Data Directory: ", self.datadir)
            print("Repository Directory: ", self.rootdir)
            print("Accounts Directory: ", self.accountdir)

        if not os.path.isdir(self.rootdir):
            print("Data path provided is invalid")
            raise

        if not os.path.exists(self.scratchdir):
            os.mkdir(self.scratchdir)

        if (sourcein == DataSource.GOOGLE):
            self.source = DataSource.GOOGLE
            self.datafolder = os.path.join(self.datadir + "\Google\\")
            self.accountfiles = ['test.txt', 'test2.txt']
            self.accounttype = DataType.OPTION
            self.fileExtensionToRemove = '.txt'

        if (sourcein == DataSource.YAHOO):
            self.source = DataSource.YAHOO
            self.datafolder = os.path.join(self.datadir + "\Yahoo\\")
            self.accountfiles = ['403b.txt'] # add HSA.csv after testing
            self.accounttype = DataType.MUTUAL_FUND
            self.fileExtensionToRemove = '.txt'

        elif (sourcein == DataSource.CRYPTOCOMPARE):
            self.source = DataSource.CRYPTOCOMPARE
            self.datafolder = os.path.join(self.datadir + "\Cryptocompare\\")
            self.accountfiles = ['test.txt', 'test2.txt']
            self.accounttype = DataType.CRYPTO
            self.fileExtensionToRemove = '.txt'

        elif (sourcein == DataSource.POLONIEX):
            self.source = DataSource.POLONIEX
            self.datafolder = os.path.join(self.datadir + "\Poloniex\\")
            self.accountfiles = ['test.txt']
            self.accounttype = DataType.CRYPTO
            self.fileExtensionToRemove = '.txt'


    def get_info_from_account(self, ls_accountfiles):
        ''' 
        Returns account name, balance and list of symbols for one account file. 
        If the account type is mutualfund, then the third item on in the list will be a dictionary of {symbol, fee}
        Returned list will contain account in index[0],
        balance at index[1], then data at index [2:]
        '''   

        ls_alldata = []
        acctBalance = 0

        for accountfile in ls_accountfiles:
            ls_data = []
            s_symbols_file = os.path.join(self.accountdir, str(accountfile))

            ffile = open(s_symbols_file, 'r')
            for line in ffile.readlines():
                # removes new line character from the string
                line = line.strip('\n')
                # checks to see if the first character in the line is numerical
                if re.search('^\d', line):
                    # if so, it becomes the account balance after removing the delimiter
                    acctBalance = float(line.replace(',', ''))
                    # continue

                # This was for creating a {ticker: expense ratio} entry for mutual funds.
                # if self.accounttype == DataType.MUTUAL_FUND:
                #     # matches two groups in the string separated by a comma group1 = text | group2 = float
                #     match = re.search(r'(\w+),([+-]?([0-9]*[.])?[0-9]+)', line)
                #     ls_data.append({match.group(1): float(match.group(2))})
                else:
                    ls_data.append(line)

            ffile.close()
            
            accountfile = accountfile.replace(self.fileExtensionToRemove, '')
            ls_data.insert(0, acctBalance)
            ls_data.insert(0, accountfile)
            ls_alldata.append(ls_data)

        return ls_alldata


    def get_dataframe(self, ls_acctdata, st_dataitem=DataItem.ADJUSTED_CLOSE):
        
        ls_symbols = []
        symbols = []
        frames = []

        for acct in ls_acctdata:
            ls_symbols = acct[2:]
            account = acct[0]

            filename = account + '-' + st_dataitem + '.pkl'
            filename = filename.replace(' ', '')
            path = os.path.join(c_dataobj.datafolder, filename)
            data = pd.read_pickle(path)
            frames.append(data)
            path = ''
        
        result = pd.concat(frames, axis=1)
        return result

    
if __name__ == '__main__':
    
    if len(sys.argv)>1:
        c_dataobj = DataAccess(sourcein=sys.argv[1], verbose=False)
    else:
        c_dataobj = DataAccess(sourcein=DataSource.YAHOO, verbose=False)


    ls_data = c_dataobj.get_info_from_account(c_dataobj.accountfiles)

    print('data source: ' + c_dataobj.source)
    print('data folder: ' + c_dataobj.datafolder)
    accts = str()
    tickers = []
    for x in ls_data:
        accts += x[0] + ' '
        tickers += x[2:]
    print('Accounts included in data source: ' + accts)
    # print(tickers)

    df_data = c_dataobj.get_dataframe(ls_data, DataItem.ADJUSTED_CLOSE)
    print(df_data.head())


