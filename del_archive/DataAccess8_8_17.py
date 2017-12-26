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
            self.accountFiles = ['403b.txt']
            self.fileExtensionToRemove = ".pkl"

        if (sourcein == DataSource.YAHOO):
            self.source = DataSource.YAHOO
            self.datafolder = os.path.join(self.datadir + "\Yahoo\\")
            self.accountFiles = ['403b.txt']
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

        #__init__ ends

    def get_data_hardread(self, ts_list, symbol_list, data_item, verbose=False, bIncDelist=False):
        '''
        Read data into a DataFrame no matter what.
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.  May be a list, in which case a list of DataFrame is returned.
        @param bIncDelist: If true, delisted securities will be included.
        @note: If a symbol is not found then a message is printed. All the values in the column for that stock will be NaN. Execution then
        continues as usual. No errors are raised at the moment.
        '''

        ''' Now support lists of items, still support old string behaviour '''
        print("inside HARD read")
        bStr = False
        if( isinstance( data_item, str) ):
            data_item = [data_item]
            bStr = True

        # init data struct - list of arrays, each member is an array corresponding do a different data type
        # arrays contain n rows for the timestamps and m columns for each stock
        all_stocks_data = []
        for i in range(len(data_item)):
            all_stocks_data.append( np.zeros ((len(ts_list), len(symbol_list))) );
            all_stocks_data[i][:][:] = np.NAN
        
        list_index= []
        
        ''' For each item in the list, add to list_index (later used to delete non-used items) '''
        for sItem in data_item:
            # if( self.source == DataSource.CUSTOM ) :
            #     ''' If custom just load what you can '''
            #     if (sItem == DataItem.CLOSE):
            #         list_index.append(1)
            #     elif (sItem == DataItem.ACTUAL_CLOSE):
            #         list_index.append(2)
            # if( self.source == DataSource.COMPUSTAT ):
            #     ''' If compustat, look through list of features '''
            #     for i, sLabel in enumerate(DataItem.COMPUSTAT):
            #         if sItem == sLabel:
            #             ''' First item is date index, labels start at 1 index '''
            #             list_index.append(i+1)
            #             break
            #     else:
            #         raise ValueError ("Incorrect value for data_item %s"%sItem)
            
            # if( self.source == DataSource.NORGATE ):
            #     if (sItem == DataItem.OPEN):
            #         list_index.append(1)
            #     elif (sItem == DataItem.HIGH):
            #         list_index.append (2)
            #     elif (sItem ==DataItem.LOW):
            #         list_index.append(3)
            #     elif (sItem == DataItem.CLOSE):
            #         list_index.append(4)
            #     elif(sItem == DataItem.VOL):
            #         list_index.append(5)
            #     elif (sItem == DataItem.ACTUAL_CLOSE):
            #         list_index.append(6)
            #     else:
            #         #incorrect value
            #         raise ValueError ("Incorrect value for data_item %s"%sItem)

            if self.source == DataSource.YAHOO:
                if (sItem == DataItem.OPEN):
                    list_index.append(1)
                elif (sItem == DataItem.HIGH):
                    list_index.append(2)
                elif (sItem ==DataItem.LOW):
                    list_index.append(3)
                elif (sItem == DataItem.ACTUAL_CLOSE):
                    list_index.append(4)
                elif(sItem == DataItem.VOL):
                    list_index.append(5)
                elif (sItem == DataItem.CLOSE):
                    list_index.append(6)
                else:
                    #incorrect value
                    raise ValueError ("Incorrect value for data_item %s"%sItem)
                #end elif

        symbol_ctr=-1
        for symbol in symbol_list: # Loop starts with a symbol from the provided list
            _file = None
            symbol_ctr = symbol_ctr + 1
            try: # depending on source, it finds the pathway to the file (interestingly pkl file second to csv)
                if self.source == DataSource.YAHOO:
                    file_path= self.getPathOfCSVFile(symbol);
                    print('found csv file')
                else:
                    file_path= self.getPathOfFile(symbol);
                    print('did not get csv file, looking for pkl file')
                
                ''' Get list of other files if we also want to include delisted '''
                if bIncDelist:
                    lsDelPaths = self.getPathOfFile( symbol, True )
                    if file_path == None and len(lsDelPaths) > 0:
                        print('Found delisted paths:', lsDelPaths)
                
                ''' If we don't have a file path continue... unless we have delisted paths '''
                if (type (file_path) != type ("random string")):
                    if bIncDelist == False or len(lsDelPaths) == 0:
                        continue; #File not found
                
                if not file_path == None: 
                    _file = open(file_path, "rb")
            except IOError:
                # If unable to read then continue. The value for this stock will be nan
                print(_file + 'could not be found')
                continue;
                
            assert( not _file == None or bIncDelist == True )
            ''' Open the file only if we have a valid name, otherwise we need delisted data '''
            if _file != None:
                print('file found is ' + str(_file))
                if self.source==DataSource.YAHOO:
                    creader = csv.reader(_file)
                    row=creader.next() # This is the headers in the workbook [list]
                    row=creader.next() # This is the first row of data [list] 
                    # next just moves the row of data down one.

                    # row is a list which is looped to format datetime and all other values to floats (n=7)

                    # changes all data into type float. date goes from yyyy-mm-dd to yyyymmdd.0
                    for i, item in enumerate(row):
                        if i==0:
                            try:
                                date = dt.datetime.strptime(item, '%Y-%m-%d') # changed dt object to new format
                                date = date.strftime('%Y%m%d') # changed dt object to sting
                                row[i] = float(date)
                            except:
                                date = dt.datetime.strptime(item, '%m/%d/%y') # May need to change this to accomodate different date formats
                                date = date.strftime('%Y%m%d')
                                row[i] = float(date)
                        else:
                            row[i]=float(item) # seems to just reassemble the same dict while converting to floats
                    naData=np.array(row) # creates a numpy array shaped (7,) from the row of data

                    # At this point I have processes the next row of data from the csv file into an np.array
                    # Once the np.array has been created and partially shaped, next you read in data re writing
                    # the first line of data with the same values.

                    for row in creader: # for each horizontal section (top to bottom)
                        for i, item in enumerate(row): # each section vertically (left to right)
                            if i==0:
                                try:
                                    date = dt.datetime.strptime(item, '%Y-%m-%d')
                                    date = date.strftime('%Y%m%d')
                                    row[i] = float(date)
                                except:
                                    date = dt.datetime.strptime(item, '%m/%d/%y')
                                    date = date.strftime('%Y%m%d')
                                    row[i] = float(date)
                            else: 
                                row[i]=float(item)
                        naData=np.vstack([np.array(row),naData])
                        # print "naData shape after float"
                        # print naData.shape
                else:
                    naData = pkl.load (_file) # or this does the same thing !!!!
                _file.close()
            else:
                naData = None
                
            ''' If we have delisted data, prepend to the current data '''
            if bIncDelist == True and len(lsDelPaths) > 0 and naData == None:
                for sFile in lsDelPaths[-1:]:
                    ''' Changed to only use NEWEST data since sometimes there is overlap (JAVA) '''
                    inFile = open( sFile, "rb" )
                    naPrepend = pkl.load( inFile )
                    inFile.close()
                    
                    if naData == None:
                        naData = naPrepend
                    else:
                        naData = np.vstack( (naPrepend, naData) )
                        
            #now remove all the columns except the timestamps and one data column
            if verbose:
                print(self.getPathOfFile(symbol))
            
            ''' Fix 1 row case by reshaping '''
            if( naData.ndim == 1 ):
                naData = naData.reshape(1,-1)
                
            #print naData
            #print list_index
            ''' We open the file once, for each data item we need, fill out the array in all_stocks_data '''
            for lLabelNum, lLabelIndex in enumerate(list_index):
                
                ts_ctr = 0
                b_skip = True
                
                ''' select timestamps and the data column we want '''
                temp_np = naData[:,(0,lLabelIndex)]
                
                #print temp_np
                
                num_rows= temp_np.shape[0]

                
                symbol_ts_list = range(num_rows) # preallocate
                for i in range (0, num_rows):

                    timebase = temp_np[i][0]
                    timeyear = int(timebase/10000)
                    
                    # Quick hack to skip most of the data
                    # Note if we skip ALL the data, we still need to calculate
                    # last time, so we know nothing is valid later in the code
                    if timeyear < ts_list[0].year and i != num_rows - 1:
                        continue
                    elif b_skip == True:
                        ts_ctr = i
                        b_skip = False
                    
                    
                    timemonth = int((timebase-timeyear*10000)/100)
                    timeday = int((timebase-timeyear*10000-timemonth*100))
                    timehour = 16
    
                    #The earliest time it can generate a time for is platform dependent
                    symbol_ts_list[i]=dt.datetime(timeyear,timemonth,timeday,timehour) # To make the time 1600 hrs on the day previous to this midnight
                    
                #for ends
    
    
                #now we have only timestamps and one data column
                
                
                #Skip data from file which is before the first timestamp in ts_list
    
                while (ts_ctr < temp_np.shape[0]) and (symbol_ts_list[ts_ctr] < ts_list[0]):
                    ts_ctr=  ts_ctr+1
                    
                    #print "skipping initial data"
                    #while ends
                
                for time_stamp in ts_list:
                    
                    if (symbol_ts_list[-1] < time_stamp):
                        #The timestamp is after the last timestamp for which we have data. So we give up. Note that we don't have to fill in NaNs because that is 
                        #the default value.
                        break;
                    else:
                        while ((ts_ctr < temp_np.shape[0]) and (symbol_ts_list[ts_ctr]< time_stamp)):
                            ts_ctr = ts_ctr+1
                            #while ends
                        #else ends
                                            
                    #print "at time_stamp: " + str(time_stamp) + " and symbol_ts "  + str(symbol_ts_list[ts_ctr])
                    
                    if (time_stamp == symbol_ts_list[ts_ctr]):
                        #Data is present for this timestamp. So add to numpy array.
                        #print "    adding to numpy array"
                        if (temp_np.ndim > 1): #This if is needed because if a stock has data for 1 day only then the numpy array is 1-D rather than 2-D
                            all_stocks_data[lLabelNum][ts_list.index(time_stamp)][symbol_ctr] = temp_np [ts_ctr][1]
                        else:
                            all_stocks_data[lLabelNum][ts_list.index(time_stamp)][symbol_ctr] = temp_np [1]
                        #if ends
                        
                        ts_ctr = ts_ctr +1
                    
                #inner for ends
            #outer for ends
        #print all_stocks_data
        
        ldmReturn = [] # List of data matrixes to return
        for naDataLabel in all_stocks_data:
            ldmReturn.append( pa.DataFrame( naDataLabel, ts_list, symbol_list) )            

        
        ''' Contine to support single return type as a non-list '''
        if bStr:
            return ldmReturn[0]
        else:
            return ldmReturn            
        
        #get_data_hardread ends

    def get_data (self, ts_list, symbol_list, data_item, verbose=True, bIncDelist=False):
        '''
        Read data into a DataFrame, but check to see if it is in a cache first.
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.  May be a list, in which case a list of DataFrame is returned.
        @param bIncDelist: If true, delisted securities will be included.
        @note: If a symbol is not found then a message is printed. All the values in the column for that stock will be NaN. Execution then 
        continues as usual. No errors are raised at the moment.
        '''

        # Construct hash -- filename where data may be already
        #
        # The idea here is to create a filename from the arguments provided.
        # We then check to see if the filename exists already, meaning that
        # the data has already been created and we can just read that file.

        ls_syms_copy = copy.deepcopy(symbol_list)

        # Create the hash for the symbols
        hashsyms = 0
        for i in symbol_list:
            hashsyms = (hashsyms + hash(i)) % 10000000

        # Create the hash for the timestamps
        hashts = 0

        # print "test point 1: " + str(len(ts_list))
        # spyfile=os.environ['QSDATA'] + '/Processed/Norgate/Stocks/US/NYSE Arca/SPY.pkl'
        for i in ts_list:
            hashts = (hashts + hash(i)) % 10000000
        hashstr = 'qstk-' + str (self.source)+'-' +str(abs(hashsyms)) + '-' + str(abs(hashts)) \
            + '-' + str(hash(str(data_item))) #  + '-' + str(hash(str(os.path.getctime(spyfile))))

        # get the directory for scratch files from environment
        # try:
        #     scratchdir = os.environ['QSSCRATCH']
        # except KeyError:
        #     #self.rootdir = "/hzr71/research/QSData"
        #     raise KeyError("Please be sure to set the value for QSSCRATCH in config.sh or local.sh")

        # final complete filename
        cachefilename = self.scratchdir + '/' + hashstr + '.pkl'
        if verbose:
            print('cachefilename is: ' + cachefilename)

        # now eather read the pkl file, or do a hardread
        readfile = False  # indicate that we have not yet read the file

        #check if the cachestall variable is defined.
        # try:
        #     catchstall=dt.timedelta(hours=int(os.environ['CACHESTALLTIME']))
        # except:
        #     catchstall=dt.timedelta(hours=1)
        cachestall = dt.timedelta(hours=self.cachestalltime)

        # Check if the file is older than the cachestalltime
        if os.path.exists(cachefilename):
            if ((dt.datetime.now() - dt.datetime.fromtimestamp(os.path.getmtime(cachefilename))) < cachestall):
                if verbose:
                    print('cache hit')
                try:
                    cachefile = open(cachefilename, "rb")
                    start = time.time() # start timer
                    retval = pkl.load(cachefile)
                    elapsed = time.time() - start # end timer
                    readfile = True # remember success
                    cachefile.close()
                except IOError:
                    if verbose:
                        print('error reading cache: ' + cachefilename)
                        print('recovering...')
                except EOFError:
                    if verbose:
                        print('error reading cache: ' + cachefilename)
                        print('recovering...')
        if (readfile!=True):
            if verbose:
                print('cache miss')
                print('beginning hardread')
            start = time.time() # start timer
            if verbose:
                print('data_item(s): ' + str(data_item))
                print('symbols to read: ' + str(symbol_list))
            retval = self.get_data_hardread(ts_list, 
                symbol_list, data_item, verbose, bIncDelist)
            elapsed = time.time() - start # end timer
            if verbose:
                print('end hardread')
                print('saving to cache')
            try:
                cachefile = open(cachefilename,"wb")
                pkl.dump(retval, cachefile, -1)
                # os.chmod(cachefilename,0666)
            except IOError:
                print('error writing cache: ' + cachefilename)
            if verbose:
                print('end saving to cache')
            if verbose:
                print('reading took ' + str(elapsed) + ' seconds')

        if type(retval) == type([]):
            for i, df_single in enumerate(retval):
                retval[i] = df_single.reindex(columns=ls_syms_copy)
        else:
            retval = retval.reindex(columns=ls_syms_copy)
        return retval


    # def getPathOfFile(self, symbol_name, bDelisted=False):
    #     '''
    #     @summary: Since a given pkl file can exist in any of the folders- we need to look for it in each one until we find it. Thats what this function does.
    #     @return: Complete path to the pkl file including the file name and extension
    #     '''

    #     if not bDelisted:
    #         for path1 in self.folderList:
    #             if (os.path.exists(str(path1) + str(symbol_name + '.pkl'))):
    #                 # Yay! We found it!
    #                 return (str(str(path1) + str(symbol_name) + '.pkl'))
    #                 #if ends
    #             elif (os.path.exists(str(path1) + str(symbol_name + '.csv'))):
    #                 # Yay! We found it!
    #                 return (str(str(path1) + str(symbol_name) + '.csv'))
    #             #for ends

    #     else:
    #         ''' Special case for delisted securities '''
    #         lsPaths = []
    #         for sPath in self.folderList:
    #             if re.search('Delisted Securities', sPath) == None:
    #                 continue

    #             for sFile in dircache.listdir(sPath):
    #                 if not re.match( '%s-\d*.pkl'%symbol_name, sFile ) == None:
    #                     lsPaths.append(sPath + sFile)

    #         lsPaths.sort()
    #         return lsPaths

    #     print('Did not find path to ' + str(symbol_name) + '. Looks like this file is missing')

    # def getPathOfCSVFile(self, symbol_name):

    #     for path1 in self.folderList:
    #             if (os.path.exists(str(path1)+str(symbol_name+".csv"))):
    #                 #Yay! We found it!
    #                 return (str(str(path1)+str(symbol_name)+".csv"))
    #                 #if ends
    #             else:
    #             #for ends
    #                 print('Did not find path to ' + str (symbol_name)+ '. Looks like this file is missing')    

    # def get_all_symbols (self):
    #     '''
    #     @summary: Returns a list of all the symbols located at any of the paths for this source. @see: {__init__}
    #     @attention: This will discard all files that are not of type pkl. ie. Only the files with an extension pkl will be reported.
    #     '''

    #     listOfStocks = list()
    #     #Path does not exist

    #     if (len(self.folderList) == 0):
    #         raise ValueError("DataAccess source not set")

    #     for path in self.folderList:
    #         stocksAtThisPath = list()
    #         stocksAtThisPath = dircache.listdir(str(path))
    #         #Next, throw away everything that is not a .pkl And these are our stocks!
    #         stocksAtThisPath = filter (lambda x:(str(x).find(str(self.fileExtensionToRemove)) > -1), stocksAtThisPath)
    #         #Now, we remove the .pkl to get the name of the stock
    #         stocksAtThisPath = map(lambda x:(x.partition(str(self.fileExtensionToRemove))[0]),stocksAtThisPath)

    #         listOfStocks.extend(stocksAtThisPath)
    #         #for stock in stocksAtThisPath:
    #             #listOfStocks.append(stock)
    #     return listOfStocks
    #     #get_all_symbols ends

    # def check_symbol(self, symbol, s_list=None):
    #     '''
    #     @summary: Returns True if given symbol is present in the s_list.
    #     @param symbol: Symbol to be checked for.
    #     @param s_list: Optionally symbol sub-set listing can be given.
    #                     if not provided, all listings are searched.
    #     @return:  True if symbol is present in specified list, else False.
    #     '''
        
    #     all_symbols = list()
        
    #     # Create a super-set of symbols.
    #     if s_list is not None:
    #         all_symbols = self.get_symbols_from_list(s_list)
    #     else:
    #         all_symbols = self.get_all_symbols()
        
    #     # Check if the symbols is present.
    #     if ( symbol in all_symbols ):
    #         return True
    #     else:
    #         return False

    def get_info_from_account(self, sourcein=DataSource.YAHOO):
        ''' Returns balance and list of symbols for one account file (Should be a list). 
        Should return a list of lists. Each individual list would contain symbol in index[0],
        balance at index[1], then data at index [2:]
        '''   

        # add ability to extract data from all files if ls_accountfiles is not passed.

        ls_allsymbols = []
        acctBalance = 0
        ls_accountfiles = self.c_dataobj.accountFiles

        for accountfile in ls_accountfiles:
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
    
    # Setup DataAccess object
    c_dataobj = DataAccess('Google')
    
    # # Check if GOOG is a valid symbol.
    # val = c_dataobj.check_symbol('GOOG')
    # print('Is GOOG a valid symbol? :' , val)
    
    # # Check if QWERTY is a valid symbol.
    # val = c_dataobj.check_symbol('QWERTY')
    # print('Is QWERTY a valid symbol? :' , val)

    # # Check if EBAY is part of SP5002012 list.
    # val = c_dataobj.check_symbol('EBAY', s_list='sp5002012')
    # print('Is EBAY a valid symbol in SP5002012 list? :', val)

    # for file in c_dataobj.accountFiles:
    #     ls_symbols, acctBalance = c_dataobj.get_info_from_account(file)
    #     print('Found ' + str(len(ls_symbols)) + ' symbols and a balance of ' + str(acctBalance) + ' in ' + file)   

    # # Check if GLD is part of SP5002012 after checking if GLD is a valid symbol.
    # val = c_dataobj.check_symbol('GLD')
    # print('Is GLD a valid symbol? : ', val)
    # val = c_dataobj.check_symbol('GLD', 'sp5002012')
    # print('Is GLD a valid symbol in sp5002012 list? :', val)
