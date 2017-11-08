import os
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
import time
from interruptingcow import timeout
import requests
import DataAccess as da
import sys
from selenium import webdriver #****** selenium requires a browser driver (PHANTOMJS) be saved to the env directory **********
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime as dt
import json
import re
from slimit import ast 
from slimit.parser import Parser
from slimit.visitors import nodevisitor
from pprint import pprint


def optimized_tickers(opt_data):
    tickers = [] # a list of unique tickers found in optimized data
    # opt_data is a list with n+1 entries: one for each account (n) and a combined all accounts (+1)
    for acct in opt_data: # in each of these entries,
        # print(acct[0]) # index 0 is always the account name
        # print(acct[1]) # index 1 is all the data associated with the account of which there are 13 objects
        for info in acct[1]: # in the data for each account
            # print(info.keys()) # keys include: sharpe, title, portfolio, std, expectedreturn
            # print(acct[0]) # name of account
            # print(info['title']) # name of optimization & time period
            for k in info['portfolio'].keys():
                if k not in tickers:
                    tickers.append(k)
    return tickers

class WebDriver(object):
    '''
    This provides the directory to where phantomjs web driver is installed. You can also add it to your environmental
    variables and locate it that way. However, I was unable to get that method to work reliably.
    '''
    DRIVERDIR = 'C:\\Users\\Michael\\Anaconda3\\envs\\QS\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe'

class IndexScrapers(object):
    '''
    
    '''
    def wiki_sp500_sectors(self):
        '''
        This is a web scraper that captures non-java script rendered content (i.e. it's fast) from wikipedia and returns
        a json file where the keys are one of eleven sectors of the S&P 500 and the values are the stock tickers that are
        included in each sector.
        '''

        st_indexdir = self.indexdir

        SITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        hdr = {'User-Agent': 'Mozilla/5.0'}

        filename = da.IndexItem.INDEX_SP500_SECTORS + '.json'
        path = os.path.join(st_indexdir, filename)

        req = requests.get(SITE, headers=hdr)
        soup = BeautifulSoup(req.content, "html.parser")
        
        table = soup.find('table', {'class': 'wikitable sortable'})
        sector_tickers = dict()
        for row in table.findAll('tr'):
            col = row.findAll('td')
            sys.exit(0)
            if len(col) > 0:
                sector = str(col[3].string.strip()).lower().replace(' ', '_')
                ticker = str(col[0].string.strip())
                if sector not in sector_tickers:
                    sector_tickers[sector] = list()
                sector_tickers[sector].append(ticker)

        with open(path, 'w') as outfile:
            json.dump(sector_tickers, outfile)


class mstar_fund_desc(object):
    '''
    A collection of web scrapers I built
    '''


    def fund_desc(self, ls_tickers):
            '''
            this web scraper captures html rendered (i.e. fast) information about each fund in the accounts provided. Fields
            includ: 'Security Name', 'ticker', 'secID', 'starRating', 'category ID', 'exchangeID', 'fundFamilyID',
            'fundCategoryName', 'sectorCode', 'identifier', 'regionId', 'GRAvailableFlag', 'securityType', 'performanceId',
            'ISIN', 'instrumentId', 'EPUsedForOverallRating' 
            * Captures ticker, securityName, fundCategory, and starRating
            '''
            
            df_data = pd.DataFrame({'ticker':ls_tickers})
            st_dataPath = self.datafolder
            item = da.ScrapeItem.MS_FUND_DESCRIPTION
            
            all_data = []
            exceptions = [] 
            contenturl = str()

            for ticker in ls_tickers:
                ticker = ticker.upper()
                print('Scraping qualitative data for %s from MorningStar' % ticker)
                contenturl = 'http://www.morningstar.com/funds/XNAS/' + ticker + '/quote.html'

                startTime = dt.now()
                response = requests.get(contenturl)

                print('Scrape took ' + str(dt.now() - startTime))

                soup = BeautifulSoup(response.content, 'html.parser')
                script = soup.find_all('script')
                htmlinfo = script[-1]
                parser = Parser()
                tree = parser.parse(htmlinfo.text)
                fields = {getattr(node.left, 'value', ''): getattr(node.right, 'value', '') for node in nodevisitor.visit(tree) if isinstance(node, ast.Assign)}
                if '"securityName"' in fields:
                    all_data.append(fields)
                else:
                    exceptions.append(ticker)
            
            df = pd.DataFrame(all_data) # Convert the json data to a dataframe
            ls_selection = ['"ticker"', '"fundCategoryName"', '"securityName"', '"starRating"'] # Columns we want with double quotation marks
            ls_corrected = ['ticker', 'fundCategoryName', 'securityName', 'starRating'] # Columns we want without double quotation marks
            df1 = df[ls_selection] # filter only these column names
            

            df1[ls_selection] = df1[ls_selection].replace({'"':''}, regex=True) # remove all double quotes from values
            df1.columns = ls_corrected # remove double quotations from col names
            # df1['securityName'] = df1['securityName'].replace('\\u0026','&', regex=True,inplace=True) # fixes an escape character, but doesn't work
            
            df_data = pd.merge(df_data, df1, on='ticker', how='left') # merge with original dataframe in case any values are missing.

            path = str(st_dataPath) + item + '.csv'

            mstar_fund_desc.fund_benchmark(df_data, path)


    def fund_benchmark(df_data, filepath):
        '''
        - Adds benchmark information to the qualitative description
        '''

        # Benchmark columns.
        fund_benchmark_columns = ['ticker','benchmarkIndex']
        # Fund Benchmark DataFrame
        fund_benchmark = pd.DataFrame(columns=fund_benchmark_columns)
        exceptions = list()
        # Loop for each fund for getting it's becnhmark
        for i in range(0,len(df_data)): # loops through the index values of the dataframe
            FUND_NAME = df_data['ticker'][i]
            
            try:
                
                # Below is the AJAX request URL whose table contains the Benchmark
                ratingriskurl = "http://performance.morningstar.com/RatingRisk/fund/mpt-statistics.action?&t=XNAS:"+FUND_NAME+"&region=usa&culture=en-US&cur=&ops=clear&s=0P00001MK8&y=3&ep=true&comparisonRemove=null&benchmarkSecId=&benchmarktype="
                print('scraping bencharks for %s' % FUND_NAME)
                response = requests.get(ratingriskurl)
                mpt_statistics_bench = pd.read_html(response.text)
                # Read the 0th value of the array
                mpt_statistics_bench = pd.read_html(response.content)[0]
                # Filtering all the not null values
                mpt_statistics_bench = mpt_statistics_bench[mpt_statistics_bench.Alpha.notnull()]
                # After filtering the row at index at 1 has the bechmark
                mpt_statistics_bench = mpt_statistics_bench.reset_index(drop=True).iloc[[1]]
                mpt_statistics_bench = mpt_statistics_bench.ix[:,0:2]
                mpt_statistics_bench.columns = fund_benchmark_columns
                # Append fund benchmark dataframe for each fund
                fund_benchmark = fund_benchmark.append(mpt_statistics_bench)
                
            except:
                # Those Funds which have error in finding benchmark are printed.
                print("Index : ",i,"No Benchmark Data Found in Morningstar for Fund : ",FUND_NAME)
                exceptions.append(FUND_NAME)
                # sys.exit(0)


        if exceptions:
            for FUND_NAME in exceptions:
                print('Reruning ',FUND_NAME)
                try:
                    ratingriskurl = "http://performance.morningstar.com/RatingRisk/fund/mpt-statistics.action?&t=XNAS:"+FUND_NAME+"&region=usa&culture=en-US&cur=&ops=clear&s=0P00001MK8&y=3&ep=true&comparisonRemove=null&benchmarkSecId=&benchmarktype="
                    response = requests.get(ratingriskurl)
                    soup = BeautifulSoup(response.text, 'lxml')
                    table = soup.find('table', attrs={'class': 'r_table2 text2'})
                    table_body = table.find('tbody')
                    rows = table_body.find_all('td')
                    # rows[8] = best fit index; [9] = R squared; [10] = beta; [11]= alpha; [12] = treynor
                    # This same process can be used to get R-Squared, Alpha, Beta, and Treynor (possibly) the row index is different.
                    new_data = dict({'ticker': FUND_NAME, 'benchmarkIndex': rows[22].text})
                    df = pd.DataFrame([new_data], columns=fund_benchmark_columns)
                    fund_benchmark = fund_benchmark.append(df, ignore_index=True)
                except AttributeError:
                    print('No luck with ', FUND_NAME)

        # Reset the fund_benchmark dataframe.
        fund_benchmark = fund_benchmark.reset_index(drop=True)
        # Merge new data to original df_data to maintain all original tickers
        df_data = pd.merge(df_data, fund_benchmark, on='ticker', how='left')

        df_data.to_csv(filepath, encoding='utf-8')


class mstar_quant_desc(object):

    def fnc_transpose(fund_history):
      '''
      This function "fnc_transpose" create transpose of fund_history data frame
      and removes unwanted data from the data frame
      It converts the data into float format.

      Parameter - fund_history dataframe

      Returns - transpose with required columns

      '''
      fund_history.index=fund_history[fund_history.columns[0]] # Make the parameters as the index
      fund_history = fund_history.drop(fund_history.columns[0], axis = 1)     
      fund_history = fund_history.transpose()    
      fund_history = fund_history.drop('Fund Category',1)    
      fund_history = fund_history.replace(to_replace=u'\u2014',value=0).astype(float) 
      fund_history = fund_history.ffill()
      fund_history = fund_history[(fund_history['Rank in Category']).notnull()] 
      return fund_history


    def performance_data(self):

        st_dataPath = self.datafolder
        item = da.ScrapeItem.MS_FUND_DESCRIPTION
        path = str(st_dataPath) + item + '.csv'

        df_desc_data = pd.DataFrame.from_csv(path, encoding='utf-8')
        # df_desc_data.dropna(how='any') # doesn't work for now
        # df_desc_data = df_desc_data[np.notnull(df_desc_data['benchmarkIndex'])] # remove any records that did not scrape 
        # a benchmark index.

        # index_dup = df_desc_data.drop_duplicates('benchmarkIndex')
       
        # mstar_benchmark_symbol = pd.DataFrame(index=range(0,len(index_dup)),columns=['Benchmark_Index','Mstar_Symbol'])

        # mstar_benchmark_symbol = pd.DataFrame(columns=['Benchmark_Index','Mstar_Symbol'])


        # mstar_benchmark_symbol.loc[0] = ['S&P 500 TR USD','0p00001mk8']
        # mstar_benchmark_symbol.loc[1] = ['Morningstar Moderate Target Risk','0p0000j533']
        # mstar_benchmark_symbol.loc[2] = ['Barclays Municipal TR USD','0p00001g5x']
        # mstar_benchmark_symbol.loc[3] = ['MSCI ACWI Ex USA NR USD','0p00001mjb']
        # mstar_benchmark_symbol.loc[4] = ['Barclays US Agg Bond TR USD','0p00001g5l']
        # mstar_benchmark_symbol.loc[5] = ['MSCI ACWI NR USD','0p00001g8p']
        # mstar_benchmark_symbol.loc[6] = ['Morningstar Long-Only Commodity TR','0p00009frd']
        # mstar_benchmark_symbol.loc[7] = ['BofAML USD LIBOR 3 Mon CM','0p00001l6o']
        # mstar_benchmark_symbol.loc[8] = ['Credit Suisse Mgd Futures Liquid TR USD','0p00001mk8']
        # mstar_benchmark_symbol.loc[9] = ['BBgBarc US Agg Bond TR USD','0p00001g5l']
        # mstar_benchmark_symbol.loc[10] = ['Morningstar US Mid Growth TR USD','0p00001gk2']
        # mstar_benchmark_symbol.loc[11] = ['Russell 3000 Value TR USD','0p00001g42']
        # mstar_benchmark_symbol.loc[12] = ['Morningstar US Large Growth TR USD','0p00001gk1']
        # mstar_benchmark_symbol.loc[13] = ['Russell 2000 Value TR USD','0p00001g40']
        # mstar_benchmark_symbol.loc[14] = ['Morningstar Lifetime Mod 2050 TR USD','0p0000j53u']
        # mstar_benchmark_symbol.loc[15] = ['S&P 1500 Financials TR','0p000099mh']
        # mstar_benchmark_symbol.loc[16] = ['Russell 1000 TR USD','0p00001g7d']
        # mstar_benchmark_symbol.loc[17] = ['Russell 1000 Value TR USD','0p00001g3y']
        # mstar_benchmark_symbol.loc[18] = ['Russell 2000 TR USD','0p00001g7e']
        # mstar_benchmark_symbol.loc[19] = ['Russell 1000 Growth TR USD','0p00001g3x']
        # mstar_benchmark_symbol.loc[20] = ['Morningstar US Small Growth TR USD','0p00001gk3']
        # mstar_benchmark_symbol.loc[21] = ['Morningstar Mod Tgt Risk TR USD','0p0000j533']
        # # mstar_benchmark_symbol.loc[12] = ['','']
        # mstar_benchmark_symbol.loc[12] = ['','']
        # if you do not match a benchmark with it's symbol, just search the benchmark in mstar then capture the 
        # symbol code in the URL and create another row of data here.

        fund_returns = {}

        # 15 year returns data for each fund.
        for i in range(0,len(df_desc_data)):
            # Fetch the Ticker.
            fund_name = df_desc_data['ticker'][i]
            # Fetch the Benchmark
            fund_benchmark_var = df_desc_data['benchmarkIndex'][i]
            # Key to be stored
            key = "fund_returns_"+fund_name
            # Fetching the Fund's benchmark and it s symbol
            # try: # Unnecessaryly finds the benchmark sysmbol code and puts it into url.
            #     symbol = (mstar_benchmark_symbol[mstar_benchmark_symbol['Benchmark_Index'] == fund_benchmark_var]['Mstar_Symbol']).values[0]
            # except IndexError:
            #     print('no benchmark symbol for ' + fund_name + '. Check the benchmark has a symbol associated.')
            # Fund Returns URL, passing the Fund Ticker, the bechmark symbol and 15 years of data to the URL
            #fund_ret_url = "http://performance.morningstar.com/Performance/fund/performance-history-1.action?&t=XNAS:"+fund_name+"&region=usa&culture=en-US&cur=&ops=clear&s="+symbol+"&ndec=2&ep=true&align=m&y=15&comparisonRemove=false&loccat=&taxadj=&benchmarkSecId=&benchmarktype="
            fund_ret_url = "http://performance.morningstar.com/fund/performance-return.action?t="+fund_name+"&region=USA&culture=en-US&ops=clear"
            
            # Calling get_performance_data function to scrape the data using Beautiful soup.
            print(fund_name)

            # Must be java script rendered
            response = requests.get(fund_ret_url)
            bs = BeautifulSoup(response.text, 'lxml')

            # Attempt 1
            # table = bs.find(lambda tag: tag.name=='table' and tag.has_key('class') and tag['class']=="r_table3")

            # Attempt 2
            div = bs.find("div", {"id": "total_returns_page"})
            # .find("div", {"id": "div_growth_10k"})
            # Write html to text file for testing
            f = open("output.txt", "w")
            f.write(str(div))
            sys.exit(0)
            print(div)
            table = bs.find('table', {'class': 'r_table3 print97'})

            # Attempt 3
            # table = bs.find_all('table')



            print(table)
            sys.exit(0)

            # # Attempt 2

            
            # container = soup.find('div', id='chart_container')
            # print(container)
            # sys.exit(0)
            
            # print(table)
            # sys.exit(0)
            soup = BeautifulSoup(urllib2.urlopen(fund_ret_url).read()) # read data using Beautiful Soup
            table = soup.find('table') # find the table
            rows = table.findAll('tr') # Find all tr rows with the table
            print(rows)
            sys.exit(0)                       
            for i in range(len(rows)):                        # read table data for each table row
                if(i==0):
                    header = rows[i].findAll('th')            # Assign first row as dataframe header
                    column_names = [head.text for head in  header] 
                    data = pd.DataFrame(columns=column_names)
                else:
                    row = [0.0]*len(column_names)             # add table data to dataframe
                    j=1
                    row[0] = rows[i].find('th').text
                    for cell in rows[i].findAll('td'):
                        row[j] = cell.text
                        j=j+1
                    data.loc[i-1]=row
            # For those funds who donot have returns for 15 years contain --. Replacing those dashes with nan values.\
            data = data.replace(to_replace='&mdash;',value=np.nan)   #replace dash with null
            data = data.ffill()





        fund_history = mstar_quant_desc.get_performance_data(fund_ret_url)
        # Calling fnc_transpose to Transpose the DataFrame
        fund_history = mstar_quant_desc.fnc_transpose(fund_history)
        fund_history = fund_history.reset_index()
        # Assigning the columns to the DataFrame.
        fund_history.columns = ['Year',fund_name+'_Returns',fund_benchmark_var,'Category (LB)','+/- S&P 500 TR USD','+/- Category (LB)','Annual_Net_Exp_Ratio','Turnover_Ratio','Rank_In_Category']
        # except:
        #     # No returns Information then print and store an empty array in the value for that fund.
        #     print("No Returns Data available for Fund : ",fund_name)
        #     # Creating an Empty DataFrame for fund with no returns
        #     fund_history = pd.DataFrame()
        #     # Assigning the DataFrame to the value
        #     fund_returns[key] = fund_history

        print(fund_returns)
        sys.exit(0)

        for i in range(0, len(fund_returns)):
            fund_key = fund_returns.keys()[i]
            # Fund Returns filename
            fund_filename = fund_returns.keys()[i][-5:]+"_RETURNS.csv"
            # Storing the Fund Returns values in a csv
            fund_returns[fund_key].replace(to_replace=u'\u2014',value='').to_csv(fund_filename)

        # Year_Trailing array for years
        Year_trailing = ['3','5','10','15']
        # MPT Stats DataFrame columns
        mpt_stats_columns = ['Fund_Ticker','Benchmark_Index', 'R_Squared','Beta','Alpha','Treynor_Ratio','Currency','Year_Trailing']
        # Volatility Measures DataFrame columns
        volatility_measures_columns = ['Fund_Ticker','Std_Dev','Return','Sharpe_Ratio','Sortino_Ratio','Bear_MktPercentile_Rank']

        # Fund Statistics object
        fund_statistics = {}

        # Loop to hover for each fund
        for yt in range(0,len(fund_df)):
            fund_name = fund_df['Fund_Ticker'][yt]
            fund_stats_benchmark = fund_df['Benchmark_Index'][yt]
            # Key value:
            key = "fund_statistics_"+fund_name
            # Fetch the Benchmark for each fund in loop
            symbol = (mstar_benchmark_symbol[mstar_benchmark_symbol['Benchmark_Index'] == fund_stats_benchmark]['Mstar_Symbol']).values[0]   
            # Initializing the mpt_statistics DataFrame for each fund. This DataFrame will be used to append statitics and measures information for different years.
            mpt_statistics = pd.DataFrame()
            # Another Loop for a fund and for 4 different years
            for i in Year_trailing:
                # MPT statistics URL passing fund ticker, year and morningstar benchmark ID
                mptstatsurl = "http://performance.morningstar.com/RatingRisk/fund/mpt-statistics.action?&t=XNAS:"+fund_name+"&region=usa&culture=en-US&cur=&ops=clear&s="+fund_stats_benchmark+"&y="+i+"&ep=true&comparisonRemove=null&benchmarkSecId=&benchmarktype="
                # Volatility measures URL passing fund ticker, year and morningstar benchmark ID
                volmeasuresurl = "http://performance.morningstar.com/RatingRisk/fund/volatility-measurements.action?&t=XNAS:"+fund_name+"&region=usa&culture=en-US&cur=&ops=clear&s="+fund_stats_benchmark+"&y="+i+"&ep=true&comparisonRemove=null&benchmarkSecId=&benchmarktype="
                try:
                    # Read the MPT statistics URL information using pandas and store it in a DataFrame. Fetching the 0th value of the array.
                    mpt_statistics_sub = pd.read_html(mptstatsurl)[0]
                    # The read URL contains many nulls. Filtering the nan values
                    mpt_statistics_sub = mpt_statistics_sub[mpt_statistics_sub.Alpha.notnull()]
                    mpt_statistics_sub['Year_Trailing'] = i
                    # Assigning columns to mpt_statistics_sub DataFrame
                    mpt_statistics_sub.columns = mpt_stats_columns
                    # Fetching the required information from the readed pandas table.
                    mpt_statistics_sub = mpt_statistics_sub[(mpt_statistics_sub['Fund_Ticker'] == fund_name) & (mpt_statistics_sub['Benchmark_Index'] == fund_stats_benchmark)].reset_index(drop=True).tail(1)
                    # Reading the volatility measures information using pandas and store it in a DataFrame. Fetching the 0th value of the array.
                    volatility_measures = pd.read_html(volmeasuresurl)[0]
                    # The read URL contains many nulls. Filtering the nan values
                    volatility_measures = volatility_measures[volatility_measures.Return.notnull()].reset_index(drop = True)
                    # Assigning columns to volatility_measures DataFrame
                    volatility_measures.columns = volatility_measures_columns
                    # Merging the mpt_statistics_sub and volatility_measures DataFrames on Fund_Ticker.
                    mpt_statistics_sub = pd.merge(mpt_statistics_sub,volatility_measures,on='Fund_Ticker',how='inner')
                    # Appending the merged information in the mpt_statistics information.
                    mpt_statistics = mpt_statistics.append(mpt_statistics_sub)
                except:
                    # Printing the Fund Information for which no data is available.
                    print("Index : ",yt,", No Statitics available for Fund : ",fund_name," for ",i," years")
                    # Assigning Empty DataFrame to store as value
                    mpt_statistics = pd.DataFrame()
            # Assigning the value to the fund_statistics key for each fund in loop after reseting the index
            fund_statistics[key] = mpt_statistics.reset_index(drop=True)

            # Fetching the Fund Statistics information for FCNTX fund.
        fund_statistics["fund_statistics_FCNTX"]

        # Export Data for Statistics in CSV files
        for i in range(0, len(fund_statistics)):
            fund_key = fund_statistics.keys()[i]
            # Assigning file names for each fund
            fund_filename = fund_statistics.keys()[i][-5:]+"_STATS.csv"
            # Replacing the Unicode values
            fund_statistics[fund_key].replace(to_replace=u'\u2014',value='').to_csv(fund_filename)

        fund_statistics.keys()[1]
        fund_statistics["fund_statistics_VTWNX"]

        # Fund Stats columns
        fund_stats_cols = fund_statistics["fund_statistics_FCNTX"].columns
        # DataFrame for 3 years:
        Fund_param_3 = pd.DataFrame(columns = fund_stats_cols)

        # Looping through the fund_statistics object for each fund and retrieving the 3 year information.
        for i in range(0,len(fund_statistics)):
            # Fetching the Key for each fund
            fund_stat_keys = fund_statistics.keys()[i]
            # Fetching the 3 year returns data and appending it to the Fund_param_3 dataframe 
            Fund_param_3 = Fund_param_3.append(fund_statistics[fund_stat_keys][fund_statistics[fund_stat_keys]['Year_Trailing'] == '3'])

        # Dropping the Bear Market Percentile Market Rank as most of the values are not available
        Fund_param_3 = Fund_param_3.drop('Bear_MktPercentile_Rank',1)
        # Resetting the Fund_param_3 DataFrame index
        Fund_param_3 = Fund_param_3.reset_index(drop=True)

        # It is found that ticker JPCIX has Treynor_Ratio as incorrect. Assigning the correct value
        Fund_param_3['Treynor_Ratio'][102] = 1954.64
        # Replacing the columns with - with a random number -10001 for later removing the values from the dataframe
        Fund_param_3[['R_Squared','Beta','Alpha','Std_Dev','Return','Sharpe_Ratio','Sortino_Ratio']] = Fund_param_3[['R_Squared','Beta','Alpha','Std_Dev','Return','Sharpe_Ratio','Sortino_Ratio']].replace(to_replace=u'\u2014',value=-10001).astype(float)
        # Filtering the funds who donot have information on the parmaters
        Fund_param_3 = Fund_param_3[Fund_param_3['R_Squared'] != -10001.0]
        Fund_param_3 = Fund_param_3[Fund_param_3['Std_Dev'] != -10001.0].reset_index(drop=True)
        # Print the length of the funds
        print(" Total # of funds with 3 year analysis data : ",len(Fund_param_3))

        # Print the header
        Fund_param_3.head()

        # Exporting 3 years data to CSV file under ../Fund_Data/Fund_Stats_Annualized_data/Fund_statistics_3years.csv 

        Fund_param_3.to_csv("Fund_statistics_3years.csv")

        # DataFrame for 5 years:
        Fund_param_5 = pd.DataFrame(columns = fund_stats_cols)

        # Looping through the fund_statistics object for each fund and retrieving the 5 year information.
        for i in range(0,len(fund_statistics)):
            # Fetching the Key for each fund
            fund_stat_keys = fund_statistics.keys()[i]
            # Fetching the 5 year returns data and appending it to the Fund_param_5 dataframe 
            Fund_param_5 = Fund_param_5.append(fund_statistics[fund_stat_keys][fund_statistics[fund_stat_keys]['Year_Trailing'] == '5'])

        # Dropping the Bear Market Percentile Market Rank as most of the values are not available
        Fund_param_5 = Fund_param_5.drop('Bear_MktPercentile_Rank',1)
        Fund_param_5 = Fund_param_5.reset_index(drop=True)

        # Replacing the columns with - with a random number -10001 for later removing the values from the dataframe
        Fund_param_5[['R_Squared','Beta','Alpha','Std_Dev','Return','Sharpe_Ratio','Sortino_Ratio']] = Fund_param_5[['R_Squared','Beta','Alpha','Std_Dev','Return','Sharpe_Ratio','Sortino_Ratio']].replace(to_replace=u'\u2014',value=-10001).astype(float)
        # Filtering the funds who donot have information on the parmaters
        Fund_param_5 = Fund_param_5[Fund_param_5['R_Squared'] != -10001.0]
        Fund_param_5 = Fund_param_5[Fund_param_5['Std_Dev'] != -10001.0].reset_index(drop=True)
        # Print the length of the funds
        print(" Total # of funds with 5 year analysis data : ",len(Fund_param_5))

        # Print the header
        Fund_param_5.head()

        # Exporting the 5 years data to csv file
        Fund_param_5.to_csv("Fund_statistics_5years.csv")

        # DataFrame for 10 years:
        Fund_param_10 = pd.DataFrame(columns = fund_stats_cols)

        # Looping through the fund_statistics object for each fund and retrieving the 10 year information.
        for i in range(0,len(fund_statistics)):
            # Fetching the Key for each fund
            fund_stat_keys = fund_statistics.keys()[i]
            # Fetching the 10 year returns data and appending it to the Fund_param_10 dataframe 
            Fund_param_10 = Fund_param_10.append(fund_statistics[fund_stat_keys][fund_statistics[fund_stat_keys]['Year_Trailing'] == '10'])

        # Dropping the Bear Market Percentile Market Rank as most of the values are not available
        Fund_param_10 = Fund_param_10.drop('Bear_MktPercentile_Rank',1)
        Fund_param_10 = Fund_param_10.reset_index(drop=True)

        # Replacing the columns with - with a random number -10001 for later removing the values from the dataframe
        Fund_param_10[['R_Squared','Beta','Alpha','Std_Dev','Return','Sharpe_Ratio','Sortino_Ratio']] = Fund_param_10[['R_Squared','Beta','Alpha','Std_Dev','Return','Sharpe_Ratio','Sortino_Ratio']].replace(to_replace=u'\u2014',value=-10001).astype(float)
        # Filtering the funds who donot have information on the parmaters
        Fund_param_10 = Fund_param_10[Fund_param_10['R_Squared'] != -10001.0]
        Fund_param_10 = Fund_param_10[Fund_param_10['Std_Dev'] != -10001.0].reset_index(drop=True)
        # Print the length of the funds
        print(" Total # of funds with 10 year analysis data : ",len(Fund_param_10))

        # Print the header
        Fund_param_10.head()

        # Exporting the 10 years data to csv file
        Fund_param_10.to_csv("Fund_statistics_10years.csv")

        # DataFrame for 15 years:
        Fund_param_15 = pd.DataFrame(columns = fund_stats_cols)

        # Looping through the fund_statistics object for each fund and retrieving the 15 year information.
        for i in range(0,len(fund_statistics)):
            # Fetching the Key for each fund
            fund_stat_keys = fund_statistics.keys()[i]
            # Fetching the 15 year returns data and appending it to the Fund_param_15 dataframe 
            Fund_param_15 = Fund_param_15.append(fund_statistics[fund_stat_keys][fund_statistics[fund_stat_keys]['Year_Trailing'] == '15'])

        # Dropping the Bear Market Percentile Market Rank as most of the values are not available
        Fund_param_15 = Fund_param_15.drop('Bear_MktPercentile_Rank',1)
        Fund_param_15 = Fund_param_15.reset_index(drop=True)

        # Replacing the columns with - with a random number -10001 for later removing the values from the dataframe
        Fund_param_15[['R_Squared','Beta','Alpha','Std_Dev','Return','Sharpe_Ratio','Sortino_Ratio']] = Fund_param_15[['R_Squared','Beta','Alpha','Std_Dev','Return','Sharpe_Ratio','Sortino_Ratio']].replace(to_replace=u'\u2014',value=-10001).astype(float)
        # Filtering the funds who donot have information on the parmaters
        Fund_param_15 = Fund_param_15[Fund_param_15['R_Squared'] != -10001.0]
        Fund_param_15 = Fund_param_15[Fund_param_15['Std_Dev'] != -10001.0].reset_index(drop=True)
        # Print the length of the funds
        print(" Total # of funds with 15 year analysis : ",len(Fund_param_15))

        # Print the header
        Fund_param_15.head()

        # Exporting the 15 years data to csv file

        Fund_param_15.to_csv("Fund_statistics_15years.csv")



    
    def morning_star_quant_desc(self, ls_tickers):
        '''
        this web scraper captures java rendered (i.e. slow) information about each fund in the accounts provided. Fields
        include: '30-Day SEC Yield', 'Category (i.e. large growth or allocation)', 'Credit Quality/Interest Rate Sensitivity', 'Expenses',
        'Fee Level', 'Investment Style (i.e. Large Value)', 'Load Fees', 'Min Investment', Status', 'TTM Yield', 'Ticker',
        'Total Assets', 'Total Market', and 'Turnover'. Each ticker takes approximately 30 seconds to collect the information
        and the information is relatively stable therefore, this script should be run less frequently or when new fund options
        become available in existing or new accounts.
        '''
        
        item = da.ScrapeItem.MS_QUANT_DESCRIPTION
        st_dataPath = self.datafolder

        all_data = []   
        contenturl = str()

        k = []
        v = []
        key = str()
        val = str()
        print('There are ' + str(len(ls_tickers)) + ' symbols to scrape')
        for ticker in ls_tickers:
            ticker = ticker.upper()
            print('Scraping quantitative data for %s from MorningStar' % ticker)
            contenturl = 'http://www.morningstar.com/funds/XNAS/' + ticker + '/quote.html'

            startTime = dt.now()
            driver = webdriver.PhantomJS(WebDriver.DRIVERDIR) 
            driver.get(contenturl)

            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "//iframe[starts-with(@id,'QT_IFRAME')]")))
            except:
                pass

            driver.switch_to_frame(driver.find_element_by_xpath("//iframe[starts-with(@id,'QT_IFRAME')]"))

            print('Scrape took ' + str(dt.now() - startTime))

            soup = BeautifulSoup(driver.page_source, "html.parser")

            table = soup.find('table', attrs={'class': 'gr_table_b1'})
            table_body = table.find('tbody')

            # Write html to text file for testing
            # f = open("output.txt", "w")
            # f.write(table_body.text)
            # sys.exit(0)

            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                for col in cols:
                    keys = col.find_all('h3')
                    values = col.find_all('span')
                    for key in keys:
                        k.append(str(key.text).strip())
                    for value in values:
                        corrval = str(value.text).strip()
                        corrval = (corrval.replace('\n','')) and (corrval.replace('\t','') and corrval.replace(' ', ''))
                        if ('\n' not in corrval) and ('$' not in corrval) and (corrval  != ''):
                            v.append(corrval)

            data = dict(zip(k,v))
            data['Ticker'] = ticker
            all_data.append(data)

            # f = open("list_output.txt", "w")
            # f.write(str(all_data))

        path = str(st_dataPath) + item + '.pkl'
        df = pd.DataFrame(all_data)
        df.to_pickle(path)


    

    def morning_star_fund_sectors(self, ls_tickers):
        '''
        this web scraper captures java rendered (i.e. slow) information about each fund in the accounts provided. Fields
        includ: 'ticker', 'sector', 'holding' (i.e. 1 - 5 based on percentage), 'fund percentage' & 'benchmark percentage'  
        '''

        st_dataPath = self.datafolder
        item = da.ScrapeItem.MS_FUND_SECTORS
        
        divs = []
        all_data = []   
        contenturl = str()
  
        for ticker in ls_tickers:
            tick_data = []
            ticker = ticker.upper()
            print('Scraping fund sector data for %s from MorningStar' % ticker)
            contenturl = 'http://www.morningstar.com/funds/XNAS/' + ticker + '/quote.html'

            startTime = dt.now()
            driver = webdriver.PhantomJS(WebDriver.DRIVERDIR) 
            driver.get(contenturl)

            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "//iframe[starts-with(@id,'QT_IFRAME')]")))
            except:
                pass

            driver.switch_to_frame(driver.find_element_by_xpath("//iframe[starts-with(@id,'QT_IFRAME')]"))

            print('Scrape took ' + str(dt.now() - startTime))

            soup = BeautifulSoup(driver.page_source, "html.parser")

            divs = soup.find_all("div", {"class": "gr_section_b1"})

            # divs[6] = top sectors and fund % as well as benchmark %.
            # divs[5] = top holdings

            # Write html to text file for testing
            # f = open("sectors_output.txt", "w")
            # f.write(divs[6])
            
            y = 1
            data = {}
            for row in divs[6].find_all('tr', attrs={'class': 'gr_table_row4'}):
                data['ticker'] = ticker
                data['holding'] = str(y)
                y += 1
                i = 0
                for column in row.find_all('td'):
                    if i == 0:
                        data['sector'] = str(column.text).strip()
                    if i == 1:
                        data['fund percentage'] = str(column.text).strip()
                    if i == 5:
                        data['benchmark percentage'] = str(column.text).strip()
                    i += 1
                all_data.append(data)
                data = {}
                
            # f = open("list_output.txt", "w")
            # f.write(str(all_data))
        path = str(st_dataPath) + item + '.pkl'
        df = pd.DataFrame(all_data)
        df.to_pickle(path)

class OpenScrapers(object):
    '''
    Web scrapers I found but are written for python 2.7
    '''

    def scrape_benchmarks(df_data):

        # Change list of tickers to single diminsion dataframe
        df_data = pd.DataFrame({'Fund_Ticker':ls_tickers})

        # Benchmark columns.
        fund_benchmark_columns = ['Fund_Ticker','Benchmark_Index']
        # Fund Benchmark DataFrame
        fund_benchmark = pd.DataFrame(columns=fund_benchmark_columns)
        # Loop for each fund for getting it's becnhmark
        for i in range(0,len(df_data)): # loops through the index values of the dataframe
            FUND_NAME = df_data['Fund_Ticker'][i]
            
            try:
                
                # Below is the AJAX request URL whose table contains the Benchmark
                ratingriskurl = "http://performance.morningstar.com/RatingRisk/fund/mpt-statistics.action?&t=XNAS:"+FUND_NAME+"&region=usa&culture=en-US&cur=&ops=clear&s=0P00001MK8&y=3&ep=true&comparisonRemove=null&benchmarkSecId=&benchmarktype="
                print('scraping meta data for %s' % FUND_NAME)
                response = requests.get(ratingriskurl)
                # Read the 0th value of the array
                mpt_statistics_bench = pd.read_html(response.text)[0]
                # Filtering all the not null values
                mpt_statistics_bench = mpt_statistics_bench[mpt_statistics_bench.Alpha.notnull()]
                # After filtering the row at index at 1 has the bechmark
                mpt_statistics_bench = mpt_statistics_bench.reset_index(drop=True).iloc[[1]]
                mpt_statistics_bench = mpt_statistics_bench.ix[:,0:2]
                mpt_statistics_bench.columns = fund_benchmark_columns
                # Append fund benchmark dataframe for each fund
                fund_benchmark = fund_benchmark.append(mpt_statistics_bench)

            except:
                # Those Funds which have error in finding benchmark are printed.
                print("Index : ",i,"No Benchmark Data Found in Morningstar for Fund : ",FUND_NAME)

        # Reset the fund_benchmark dataframe.
        fund_benchmark = fund_benchmark.reset_index(drop=True)


        print(fund_benchmark)
        
        st_dataPath = self.datafolder
        item = da.ScrapeItem.FUND_METADATA
        path = str(st_dataPath) + item + '.pkl'
        fund_benchmark.to_pickle(path)


        # # Fetch all the distinct benchmarks for the above set of ~1277 funds
        # index_dup = fund_benchmark.drop_duplicates('Benchmark_Index')
        # # Total Distinct benchmarks for ~ 1277 funds
        # index_dup

        # mstar_benchmark_symbol = pd.DataFrame(index=range(0,len(index_dup)),columns=['Benchmark_Index','Mstar_Symbol'])

        # mstar_benchmark_symbol.loc[0] = ['S&P 500 TR USD','0P00001MK8']
        # mstar_benchmark_symbol.loc[1] = ['Morningstar Moderate Target Risk','0P0000J533']
        # mstar_benchmark_symbol.loc[2] = ['Barclays Municipal TR USD','0P00001G5X']
        # mstar_benchmark_symbol.loc[3] = ['MSCI ACWI Ex USA NR USD','0P00001MJB']
        # mstar_benchmark_symbol.loc[4] = ['Barclays US Agg Bond TR USD','0P00001G5L']
        # mstar_benchmark_symbol.loc[5] = ['MSCI ACWI NR USD','0P00001G8P']
        # mstar_benchmark_symbol.loc[6] = ['Morningstar Long-Only Commodity TR','0P00009FRD']
        # mstar_benchmark_symbol.loc[7] = ['BofAML USD LIBOR 3 Mon CM','0P00001L6O']
        # mstar_benchmark_symbol.loc[8] = ['Credit Suisse Mgd Futures Liquid TR USD','0P00001MK8']

        # mstar_benchmark_symbol

        # # Merging the Funds_family dataframe and fund_benchmark dataframe.
        # fund_df = pd.merge(Funds_family,fund_benchmark,how='left',on='Fund_Ticker')
        # fund_df = fund_df[fund_df['Benchmark_Index'].notnull()].reset_index(drop=True)

        # # Printing the head for Fund DataFrame.
        # fund_df.head()

        # # Example for a fund with ticker = 'JMGIX'
        # # fund_df[fund_df['Fund_Ticker'] == 'JMGIX']
        # #fund_df.shape

        # # Exporting the Fund's DataFrame in a csv format. 
        # fund_df.to_csv("Fund_Metadata.csv")

    