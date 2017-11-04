import os
import pandas as pd
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
                    # This same process can be used to get R-Squared, Alpha, Beta, and Treynor (possibly) the row index is different.
                    new_data = dict({'ticker': FUND_NAME, 'benchmarkIndex': rows[8].text})
                    df = pd.DataFrame([new_data], columns=fund_benchmark_columns)
                    fund_benchmark = fund_benchmark.append(df, ignore_index=True)
                except:
                    print('No luck with ', FUND_NAME)

        # Reset the fund_benchmark dataframe.
        fund_benchmark = fund_benchmark.reset_index(drop=True)
        # Merge new data to original df_data to maintain all original tickers
        df_data = pd.merge(df_data, fund_benchmark, on='ticker', how='left')

        df_data.to_csv(filepath)


class ms_quant_desc(object):
    
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

    