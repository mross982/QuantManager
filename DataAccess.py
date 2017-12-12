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
import DataUtil as du


class DataItem(object):
    DATE = "Date"
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"
    VOLUME = "Volume"
    ACTUAL_CLOSE = "ActualClose"
    ADJUSTED_CLOSE = "Adj Close"


class IndexItem(object):
    INDEX_SP500_SECTORS = "SP500sectors"


class ScrapeItem(object):
    INDV_DESC = "Individual_Description"
    COMPARATIVE_STATS = "Opt_Comparative_Stats"
    MS_FUND_SECTORS = "MSFundSectors"
    FUND_METADATA = "Fund_MetaData"


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
    def __init__(self, sourcein=DataSource.YAHOO, cachestalltime=12, verbose=False):
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
        self.indexdatadir = os.path.join(self.indexdir, 'Index_data\\')
  
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
            self.imagefolder = os.path.join(self.datafolder + "\Images\\")
            self.accountfiles = ['403b.txt','HSA.txt'] # add HSA.txt & 403b.txt & 401k after testing
            self.fileExtensionToRemove = '.txt'
            

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


    def ensure_dir(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)


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


    def get_json(self, path):
        '''
        Returns a list of all of the json files available in the Index directory. 
        * The first item always the name of the index (i.e. the file name)
        * in the instance where there are multiple json files in the path, all files are returned as a list within
            a larger list
        '''
        
        jsondata = []
        filenames = []
        
        for file in os.listdir(path):
            filename = str(file)
            if filename.endswith('.json'):
                filenames.append(filename)

        if len(filenames) >1:
            for f in filenames:
                acctdata = []
                drtory = os.path.join(path, f)
                with open(drtory) as json_file:
                    data = json.load(json_file)
                    acctdata.append(data)
                    name = f.replace('.json', '')
                    acctdata.insert(0,str(name))
                    jsondata.append(acctdata)
        else:
            drtory = os.path.join(path, filenames[0])
            with open(drtory) as json_file:
                data = json.load(json_file)
                jsondata.append(data)
                name = filenames[0].replace('.json', '')
                jsondata.insert(0,str(name))
            
        return jsondata

    def json_to_ls_acctdata(self, list_of_jsons):
        '''
        * Takes the index json file and arranges it to an ls_acctdata format for API use. 
        * Currently only used for SP500 Sectors index
        '''
        ls_acctdata = []
        json = list_of_jsons[1]
        for k, v in json.items():
            innerlist = []
            innerlist.append(k)
            innerlist.append('amount N/A')
            for sym in v:
                innerlist.append(sym)
            ls_acctdata.append(innerlist)

        return ls_acctdata


    def get_combined_dataframe(self, dataitem=DataItem.ADJUSTED_CLOSE, clean=False):
        '''
        given the data object and item, and returns the dataframe from the object's source associated with the data 
        item. Will combine data from several accounts. 
        * Currently for optimizing multiple accouts at once.
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


    def get_dataframe(filepath, clean=False):
        '''
        given the data object and item, and returns the dataframe from the object's source associated with the data 
        item. Will return a datafram from one account. Currently used for optimizing a single account individually.
        '''
    
        data = pd.read_pickle(filepath)
        if clean == True:
            data = modify_data.clean_data(data)

        return data

    def dataframe_to_csv(self, df_data, filename='Test.csv'):
        '''
        This creates a csv file of a single dataframe. The abbreviate argument allows you to only print the top five 
        rows of data in a dataframe to csv. 
        * Currently only used for spot checking downloaded data.
        '''

        outputfile = os.path.join(self.datafolder, filename + '.csv')
        print(outputfile)
        df_data.to_csv(outputfile)


    def csv_to_dataframe(self, csv_file):
        '''
        This will create a way to make edits to a pickled data frame by first converting it to csv, make any 
        corrective actions, then save the csv over the original pickled data frame.
        '''
        pass

    def get_opt_df(self, acct, summary=None):
        '''
        retrieves dataframe of optimized assets from an account
        '''

        data_path = self.datafolder
        filenames = []
        frames = []

        for file in os.listdir(data_path):
            filename = str(file)
            if filename.endswith('.pkl') and 'opt' in filename and acct in filename:
                path = os.path.join(data_path, filename)
                data = pd.read_pickle(path)
                frames.append(data)
                path = ''

        result = pd.concat(frames, axis=1)
        if summary != None:
            result = result[result['Symbols'].str.contains('opt')]
        return result

    def get_opt_syms(self, acct):
        '''
        retrieves a list of unique symbols from the optimized data sets.
        '''
    
        data_path = self.datafolder
        filenames = []
        frames = []

        for file in os.listdir(data_path):
            filename = str(file)
            if filename.endswith('.pkl') and 'opt' in filename and acct in filename:
                path = os.path.join(data_path, filename)
                data = pd.read_pickle(path)
                frames.append(data)
                path = ''

        result = pd.concat(frames, axis=1)
        symbols = result['Symbols']
        symbols = symbols.drop_duplicates()
        symbols = symbols[~symbols.str.contains('opt')] # removes any data with the sub string 'opt'
        symbols = symbols.tolist()
        return symbols

class modify_data(object):
    def clean_data(df_data):

        df_data = modify_data.remove_drops(df_data)
        df_data = modify_data.remove_rises(df_data)
        df_data = modify_data.remove_nulls(df_data)

        df_data = df_data.fillna(method='ffill')
        df_data = df_data.fillna(method='bfill')

        return df_data


    def remove_drops(df_data):

        ls_symbols1 = list(df_data.columns.values)
        ls_excl = []

        df_rets = du.returnize0(df_data)
        np_rets = df_rets.values
        ar_excl = np.where(np_rets <= -0.5) # remove any drops of over 50%
        ls = list(set(ar_excl[1]))
        for x in ls:
            ls_excl.append(ls_symbols1[x])
        df = df_data.drop(ls_excl, axis=1)

        return df


    def remove_rises(df_data):

        ls_symbols1 = list(df_data.columns.values)
        ls_excl = []

        df_rets = du.returnize0(df_data)
        np_rets = df_rets.values
        ar_excl = np.where(np_rets >= 0.5) # remove any increases of over 50%
        ls = list(set(ar_excl[1]))
        for x in ls:
            ls_excl.append(ls_symbols1[x])
        df = df_data.drop(ls_excl, axis=1)

        return df


    def remove_nulls(df_data):
        ls_symbols1 = list(df_data.columns.values)
        ls_excl = []

        ls_nulls = df_data.columns[df_data.isnull().any()].tolist()
        for x in ls_nulls:
            total = df_data[x].isnull().sum()
            if total >= 20:
                # Ideally, this would remove 20 consecutive null values as opposed to 20 total.
                df = df_data.drop(x, axis=1)
            
        return df
        
        
