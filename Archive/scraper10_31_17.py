import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
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


class WebDriver(object):
    '''
    This provides the directory to where phantomjs web driver is installed. You can also add it to your environmental
    variables and locate it that way. However, I was unable to get that method to work reliably.
    '''
    DRIVERDIR = 'C:\\Users\\Michael\\Anaconda3\\envs\\QS\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe'

class WebScrapers(object):
    '''
    A collection of web scrapers 
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

        filename = 'sp500_sectors.json'
        path = os.path.join(st_indexdir, filename)

        req = requests.get(SITE, headers=hdr)
        soup = BeautifulSoup(req.content, "html.parser")
        
        table = soup.find('table', {'class': 'wikitable sortable'})
        sector_tickers = dict()
        for row in table.findAll('tr'):
            col = row.findAll('td')
            if len(col) > 0:
                sector = str(col[3].string.strip()).lower().replace(' ', '_')
                ticker = str(col[0].string.strip())
                if sector not in sector_tickers:
                    sector_tickers[sector] = list()
                sector_tickers[sector].append(ticker)

        with open(path, 'w') as outfile:
            json.dump(sector_tickers, outfile)
            print(sector_tickers)



    def morning_star_quant_desc(self):
        '''
        this web scraper captures java rendered (i.e. slow) information about each fund in the accounts provided. Fields
        include: '30-Day SEC Yield', 'Category (i.e. large growth or allocation)', 'Credit Quality/Interest Rate Sensitivity', 'Expenses',
        'Fee Level', 'Investment Style (i.e. Large Value)', 'Load Fees', 'Min Investment', Status', 'TTM Yield', 'Ticker',
        'Total Assets', 'Total Market', and 'Turnover'. Each ticker takes approximately 30 seconds to collect the information
        and the information is relatively stable therefore, this script should be run less frequently or when new fund options
        become available in existing or new accounts.
        '''
        
        item = da.DataItem.DESCRIPTIVE_INFO

        ls_data = self.get_info_from_account()
        st_dataPath = self.datafolder

        all_data = []   
        contenturl = str()

        for acct in ls_data:
            account_name = acct[0]
            path = str(st_dataPath) + str(account_name) + '-' + item + '.pkl'
            tickers = []
            tickers = acct[2:]
            k = []
            v = []
            key = str()
            val = str()
            for ticker in tickers:
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

            path = str(st_dataPath) + str(account_name) + item
            df = pd.DataFrame(all_data)
            df.to_pickle(path)


    def morning_star_qual_desc(self):
        '''
        this web scraper captures html rendered (i.e. fast) information about each fund in the accounts provided. Fields
        includ: 'Security Name', 'ticker', 'secID', 'starRating', 'category ID', 'exchangeID', 'fundFamilyID',
        'fundCategoryName', 'sectorCode', 'identifier', 'regionId', 'GRAvailableFlag', 'securityType', 'performanceId',
        'ISIN', 'instrumentId', 'EPUsedForOverallRating'   
        '''
        ls_data = self.get_info_from_account()
        st_dataPath = self.datafolder
        item = da.DataItem.MS_QUAL_DESCRIPTION
        
        all_data = []   
        contenturl = str()

        for acct in ls_data:
            account_name = acct[0]
            path = str(st_dataPath) + str(account_name) + '-' + item + '.pkl'
            print(path)
            tickers = []
            tickers = acct[2:]
            k = []
            v = []
            key = str()
            val = str()
            for ticker in tickers:
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

                all_data.append(fields)


                # Write html to text file for testing
                # f = open("output.txt", "w")
                # f.write(table_body.text)

            df = pd.DataFrame(all_data)
            df.to_pickle(path)


    def morning_star_fund_sectors(self):
        '''
        this web scraper captures java rendered (i.e. slow) information about each fund in the accounts provided. Fields
        includ: 'ticker', 'sector', 'holding' (i.e. 1 - 5 based on percentage), 'fund percentage' & 'benchmark percentage'  
        '''
        ls_data = self.get_info_from_account()
        st_dataPath = self.datafolder
        item = da.DataItem.MS_FUND_SECTORS
        
        divs = []
        all_data = []   
        contenturl = str()

        for acct in ls_data:
            account_name = acct[0]
            path = str(st_dataPath) + str(account_name) + '-' + item + '.pkl'
            tickers = []
            tickers = acct[2:]
            for ticker in tickers:
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

            df = pd.DataFrame(all_data)
            df.to_pickle(path)

if __name__ == '__main__':

    c_dataobj = da.DataAccess(sourcein=da.DataSource.YAHOO)

    # WebScrapers.wiki_sp500_sectors(c_dataobj)
    # WebScrapers.morning_star_quant_desc(c_dataobj)
    WebScrapers.morning_star_fund_sectors(c_dataobj)