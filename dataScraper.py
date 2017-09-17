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




def wiki_sp500_sectors(st_indexdir):

    SITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    hdr = {'User-Agent': 'Mozilla/5.0'}

    filename = 'sp500_sectors.pkl'
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

    df = pd.DataFrame.from_dict(sector_tickers, orient='index')
    df.transpose()
    df.to_pickle(path)

def morning_star_desc(ls_data, st_dataPath):

    item = da.DataItem.DESCRIPTION
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
            print('Scraping data for %s from MorningStar' % ticker)
            contenturl = 'http://www.morningstar.com/funds/XNAS/' + ticker + '/quote.html'

            startTime = dt.now()

            response = requests.get(contenturl)


            # if response.status_code != requests.codes.ok:
            #     response.raise_for_status()
            # print(response.encoding) # allows you to manually set the encoding
            # print(response.content) # one of the first lines give the encoding guessed by requests based on the script.
            # print(response.status_code)   # 200 is successful connection
            # print(response.text[:1000])
            # print(response.cookies)  # shows any cookies in the response
            # print(contenturl)


            # Describe how long the scrape took to execute
            print('Scrape took ' + str(dt.now() - startTime))

            soup = BeautifulSoup(response.content, 'html.parser')

            script= soup.find_all('script')
            # print(len(script))  # 16
            f = open("output.txt", "w")
            f.write(str(script[-1]))


            sys.exit(0)

            # Write html to text file for testing
            # f = open("output.txt", "w")
            # f.write(table_body.text)
            # sys.exit(0)

           
            data = dict(zip(k,v))
            data['Ticker'] = ticker
            all_data.append(data)

            f = open("list_output.txt", "w")
            f.write(str(all_data))

        path = str(st_dataPath) + str(account_name) + item
        df = pd.DataFrame(all_data)
        df.to_pickle(path)


def morning_star_desc_info(ls_data, st_dataPath):
    
    item = da.DataItem.DESCRIPTIVE_INFO
    all_data = []   
    contenturl = str()
    exceptions = []

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
            print('Scraping data for %s from MorningStar' % ticker)
            contenturl = 'http://www.morningstar.com/funds/XNAS/' + ticker + '/quote.html'

            startTime = dt.now()

            # I added the chromedriver location to PATH variables, otherwise provide path here Chrome(path/to/driver)
            driver = webdriver.PhantomJS(da.WebDriver.DRIVERDIR) 
            # driver = webdriver.Chrome()
            driver.get(contenturl)

            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "//iframe[starts-with(@id,'QT_IFRAME')]")))
            except:
                pass
                # WebDriverWait(driver, 10)
                # print('%s added to exceptions list' % ticker)
                # exceptions.append(ticker)
                # continue

            #Very complicated way to find the dynamically named JavaScript created iframe within the HTML doc. html below:
            driver.switch_to_frame(driver.find_element_by_xpath("//iframe[starts-with(@id,'QT_IFRAME')]"))

            # Describe how long the scrape took to execute
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
                        # for some reason the values are sometimes duplicate and contain additional return characters.
                        # fortunately these return characters, $ symbols, and empty values are only found in duplicate values
                        corrval = (corrval.replace('\n','')) and (corrval.replace('\t','') and corrval.replace(' ', ''))
                        if ('\n' not in corrval) and ('$' not in corrval) and (corrval  != ''):
                            v.append(corrval)

            data = dict(zip(k,v))
            data['Ticker'] = ticker
            all_data.append(data)

            f = open("list_output.txt", "w")
            f.write(str(all_data))

        path = str(st_dataPath) + str(account_name) + item
        df = pd.DataFrame(all_data)
        df.to_pickle(path)


if __name__ == '__main__':

    c_dataobj = da.DataAccess(sourcein=da.DataSource.YAHOO)
    ls_data = c_dataobj.get_info_from_account(c_dataobj.accountfiles)

    morning_star_desc(ls_data, c_dataobj.datafolder)
    # wiki_sp500_sectors(c_dataobj.indexdir)