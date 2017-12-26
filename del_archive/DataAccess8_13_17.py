'''
Created on Jan 15, 2013

@author: Michael Williams
@contact: mross982@gmail.com
@summary: Data Access python library.

'''
import numpy as np
import pandas as pa
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
from pprint import pprint

class DataItem (object):
    DATE = "Date"
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"
    VOL = "Volume"
    VOLUME = "Volume"
    ACTUAL_CLOSE = "Actual_Close"
    ADJUSTED_CLOSE = "Adj_Close"

class DataSource(object):
    GOOGLE = 'Google' # stock/bond data
    YAHOO = 'Yahoo'  # mutual fund/stock/bond data
    CRYPTOCOMPARE = 'Cryptocompare' # daily crypto data
    POLONIEX = 'Poloniex' # intra day crypto data
    MARKETCAP = 'Marketcap' # market data crypto


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
            self.accountFiles = ['test.txt']
            self.fileExtensionToRemove = ".pkl"

        if (sourcein == DataSource.YAHOO):
            self.source = DataSource.YAHOO
            self.datafolder = os.path.join(self.datadir + "\Yahoo\\")
            self.accountFiles = ['403b.txt', 'HSA.txt']
            self.fileExtensionToRemove = ".pkl"

        elif (sourcein == DataSource.CRYPTOCOMPARE):
            self.source = DataSource.CRYPTOCOMPARE
            self.datafolder = os.path.join(self.datadir + "\Cryptocompare\\")
            self.accountFiles = ['test.txt']
            self.fileExtensionToRemove = ".pkl"

        elif (sourcein == DataSource.POLONIEX):
            self.source = DataSource.POLONIEX
            self.datafolder = os.path.join(self.datadir + "\Poloniex\\")
            self.accountFiles = ['test.txt']
            # self.fileExtensionToRemove = ".csv"


    def get_info_from_account(self, ls_accountFiles):
        ''' Returns balance and list of symbols for one account file (Should be a list). 
        Should return a list of lists. Each individual list would contain symbol in index[0],
        balance at index[1], then data at index [2:]
        '''   

        # add ability to extract data from all files if ls_accountfiles is not passed.

        ls_allsymbols = []
        acctBalance = 0

        for accountfile in ls_accountFiles:
            ls_symbols = []
            s_symbols_file = os.path.join(self.accountdir, str(accountfile))
            ffile = open(s_symbols_file, 'r')
            for line in ffile.readlines():
                if re.search('\d', line):
                    acctBalance = float(line)
                else:
                    ls_symbols.append(line.strip())
            ffile.close()

            accountfile = accountfile.replace('.txt', '')
            ls_symbols.insert(0, acctBalance)
            ls_symbols.insert(0, accountfile)
            ls_allsymbols.append(ls_symbols)

        return ls_allsymbols


    def get_info(self):
        '''
        @summary: Returns and prints a string that describes the datastore.
        @return: A string.
        '''

        if (self.source == DataSource.NORGATE):
            retstr = "Norgate:\n"
            retstr = retstr + "Daily price and volume data from Norgate (premiumdata.net)\n"
            retstr = retstr + "that is valid at the time of NYSE close each trading day.\n"
            retstr = retstr + "\n"
            retstr = retstr + "Valid data items include: \n"
            retstr = retstr + "\topen, high, low, close, volume, actual_close\n"
            retstr = retstr + "\n"
            retstr = retstr + "Valid subdirs include: \n"
            for i in self.folderSubList:
                retstr = retstr + "\t" + i + "\n"

        elif (self.source == DataSource.YAHOO):
            retstr = "Yahoo:\n"
            retstr = retstr + "Attempts to load a custom data set, assuming each stock has\n"
            retstr = retstr + "a csv file with the name and first column as the stock ticker,\ date in second column, and data in following columns.\n"
            retstr = retstr + "everything should be located in QSDATA/Yahoo\n"
            for i in self.folderSubList:
                retstr = retstr + "\t" + i + "\n"

        elif (self.source == DataSource.COMPUSTAT):
            retstr = "Compustat:\n"
            retstr = retstr + "Compilation of (almost) all data items provided by Compustat\n"
            retstr = retstr + "Valid data items can be retrieved by calling get_data_labels(): \n"
            retstr = retstr + "\n"
            retstr = retstr + "Valid subdirs include: \n"
            for i in self.folderSubList:
                retstr = retstr + "\t" + i + "\n"
        elif (self.source == DataSource.CUSTOM):
            retstr = "Custom:\n"
            retstr = retstr + "Attempts to load a custom data set, assuming each stock has\n"
            retstr = retstr + "a csv file with the name and first column as the stock ticker, date in second column, and data in following columns.\n"
            retstr = retstr + "everything should be located in QSDATA/Processed/Custom\n"
        elif (self.source == DataSource.MLT):
            retstr = "ML4Trading:\n"
            retstr = retstr + "Attempts to load a custom data set, assuming each stock has\n"
            retstr = retstr + "a csv file with the name and first column as the stock ticker,\ date in second column, and data in following columns.\n"
            retstr = retstr + "everything should be located in QSDATA/Processed/ML4Trading\n"
        else:
            retstr = "DataAccess internal error\n"

        print(retstr)
        return retstr
        #get_sublists


    #class DataAccess ends
if __name__ == '__main__':

    print('Instance of c_dataobj created with...')
    
    c_dataobj = DataAccess(sourcein='Google', verbose=True)

    ls_data = c_dataobj.get_info_from_account(c_dataobj.accountFiles)

    print('data source: ' + c_dataobj.source)
    print('data folder: ' + c_dataobj.datafolder)
    print('account files ')
    for sym in ls_data:
        print(sym)


    
    # for file in c_dataobj.accountFiles:
    #     ls_symbols, acctBalance = c_dataobj.get_info_from_account(file)
    #     print('Found ' + str(len(ls_symbols)) + ' symbols and a balance of ' + str(acctBalance) + ' in ' + file)   
