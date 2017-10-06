'''
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
import json


class DataItem (object):
    DATE = "Date"
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"
    VOLUME = "Volume"
    ACTUAL_CLOSE = "ActualClose"
    ADJUSTED_CLOSE = "Adj Close"
    MS_QUANT_DESCRIPTION = "MSQuantDescription"
    MS_QUAL_DESCRIPTION = "MSQualDescription"
    MS_TOP_SECTORS = "MSTopSectors"
    MS_FUND_SECTORS = "MSFundSectors"
    INDEX_SP500_SECTORS = "SP500sectors"
    


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
    def __init__(self, sourcein=DataSource.YAHOO, cachestalltime=12, verbose=True):
        '''
        @param sourcestr: Specifies the source of the data. Initializes paths based on source.
        @note: No data is actually read in the constructor. Only paths for the source are initialized
        @param: Scratch defaults to a directory in /tmp/QSScratch

        @******* You need to set the QSREPO and QSDATA environmental variables before this will run **********
        '''
        self.folderList = list()
        self.folderSubList = list()
        self.cachestalltime = cachestalltime
        self.fileExtension = '.pkl'

        try:
            self.rootdir = os.path.dirname(os.path.realpath(__file__))
        except:
            self.rootdir = os.environ['QSREPO']
        try:
            self.datadir = os.path.join(self.rootdir, 'QSData')
        except:
            self.datadir = os.environ['QSDATA']
        try:
            self.scratchdir = os.path.join(tempfile.gettempdir(), 'QSScratch')
        except:
            self.scratchdir = os.environ['QSSCRATCH']
       
        self.accountdir = os.path.join(self.rootdir, 'Accounts\\')

        self.indexdir = os.path.join(self.datadir, 'Indexes\\')
  
        if verbose:
            print("Scratch Directory: ", self.scratchdir)
            print("Data Directory: ", self.datadir)
            print("Repository Directory: ", self.rootdir)
            print("Accounts Directory: ", self.accountdir)

        if not os.path.isdir(self.rootdir):
            print("Root path provided is invalid")
            raise

        if not os.path.exists(self.scratchdir):
            os.mkdir(self.scratchdir)

        if (sourcein == DataSource.GOOGLE):
            self.source = DataSource.GOOGLE
            self.datafolder = os.path.join(self.datadir + "\Google\\")
            self.accountfiles = ['test.txt', 'test2.txt']
            self.fileExtensionToRemove = '.txt'

        if (sourcein == DataSource.YAHOO):
            self.source = DataSource.YAHOO
            self.datafolder = os.path.join(self.datadir + "\Yahoo\\")
            self.accountfiles = ['403b.txt'] # add HSA.txt & 403b.txt & 401k after testing
            self.fileExtensionToRemove = '.txt'
            self.imagefile = os.path.join(self.datadir + "\Images\\")

        elif (sourcein == DataSource.CRYPTOCOMPARE):
            self.source = DataSource.CRYPTOCOMPARE
            self.datafolder = os.path.join(self.datadir + "\Cryptocompare\\")
            self.accountfiles = ['test.txt', 'test2.txt']
            self.fileExtensionToRemove = '.txt'

        elif (sourcein == DataSource.POLONIEX):
            self.source = DataSource.POLONIEX
            self.datafolder = os.path.join(self.datadir + "\Poloniex\\")
            self.accountfiles = ['test.txt']
            self.fileExtensionToRemove = '.txt'


    def get_info_from_account(self):
        ''' 
        Returns account name, balance and list of symbols for one account file. 
        If the account type is mutualfund, then the third item on in the list will be a dictionary of {symbol, fee}
        Returned list will contain account in index[0],
        balance at index[1], then data at index [2:]
        '''   

        ls_accountfiles = self.accountfiles
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
                else:
                    ls_data.append(line)

            ffile.close()
            
            accountfile = accountfile.replace(self.fileExtensionToRemove, '')
            ls_data.insert(0, acctBalance)
            ls_data.insert(0, accountfile)
            ls_alldata.append(ls_data)

        return ls_alldata


    def get_index_json(self):
        '''
        Returns a list of all of the json files available in the Index directory. The first item always the name of the
        index (i.e. the file name)
        '''
        index_path = self.indexdir
        list_of_jsons = []
        
        for index_file in os.listdir(index_path):
            filename = str(index_file)
            file = filename.replace('.txt','')
            path = os.path.join(index_path, filename)
            with open(path) as json_file:
                data = json.load(json_file)
                list_of_jsons.append(data)
                list_of_jsons.insert(0,str(file))
            
        return list_of_jsons


    def get_dataframe(self, dataitem=DataItem.ADJUSTED_CLOSE, clean=False):
        '''
        given the data object and item, and returns the dataframe from the object's source associated with the data item.
        '''
        ls_acctdata = self.get_info_from_account()
        frames = []

        for acct in ls_acctdata:
            account = acct[0]

            filename = account + '-' + dataitem.replace(' ','') + '.pkl'
            filename = filename.replace(' ', '')
            path = os.path.join(self.datafolder, filename)
            data = pd.read_pickle(path)
            frames.append(data)
            path = ''
        
        result = pd.concat(frames, axis=1)

        if clean == True:
            result = result.fillna(method='ffill').fillna(method='bfill')
            result = result.dropna(axis=1, how='all')

        return result


    def dataframe_to_csv(self, df_data, abbr=False):
        '''
        This creates a csv file of a dataframe to test values to make sure they make sense. The abbreviate argument allows
        you to only print the top five rows of data in a dataframe to csv.
        '''

        path = self.datafolder
        filename = 'calcTest.csv'

        # if isinstance(df_data, pd.dataframe):
        if abbr == True:
            df_data.head().to_csv(os.path.join(path,filename))
        else:
            df_data.to_csv(os.path.join(path, filename))


    def csv_to_dataframe(self, csv_file):
        '''
        This will create a way to make edits to a pickled data frame by first converting it to csv, make any 
        corrective acctions, then save the csv over the original pickled data frame.
        '''
        pass

    
if __name__ == '__main__':
    
    if len(sys.argv)>1:
        c_dataobj = DataAccess(sourcein=sys.argv[1], verbose=False)
    else:
        c_dataobj = DataAccess(sourcein=DataSource.YAHOO, verbose=False)

    index = c_dataobj.get_index_json()

    # Default call is for Adjusted Close data frame (which only works with Yahoo data)
    # df_data = c_dataobj.get_dataframe(DataItem.MS_QUANT_DESCRIPTION)
    df_data = c_dataobj.get_dataframe()

    # cleandata = DataAccess.clean_data(df_data)

    # Note the difference between running the function on the object or passing the object as an argument.
    # DataAccess.dataframe_to_csv(c_dataobj, df_data, abbr=True)
    
    # the data frame to csv function is used exclusively to view and verify the data.
    c_dataobj.dataframe_to_csv(df_data, abbr=False)

