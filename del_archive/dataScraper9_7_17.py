import pytz
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import DataAccess as da
import sys
from selenium import webdriver # selenium is req'd to read JS rendered content
#****** selenium requires a browser driver be saved to the env directory **********
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime as dt




def sp500_sectors():

    SITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    # START = datetime(1900, 1, 1, 0, 0, 0, 0, pytz.utc)
    # END = datetime.today().utcnow()
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # Unsupported urllib2 code
    # req = urllib2.Request(site, headers=hdr)
    # page = urllib2.urlopen(req)
    # soup = BeautifulSoup(page)

    # Replacement code
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

    print(str(len(sector_tickers)) + ' sector tickers')
    print(sector_tickers)


def fund_info(ls_data, st_dataPath):

    # these fields are not the same across all assets. They will need to be scraped as well.
    #data = ['Fund_Name','TTM_Yield', 'Total_Assets', 'Expenses', 'Fee_Level', 'Turnover', 'Status', '30-day_SEC_Yield', 'Category']
    # df_FundInfo = pd.DataFrame(columns=data)
    
    item = [da.DataItem.DESCRIPTIVE_INFO]
    all_data = []   
    contenturl = str()

    # browser = webdriver.Chrome() # not sure if I can open chrome once or each time I change the URL?
    for acct in ls_data:
        account_name = acct[0]
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
            driver = webdriver.PhantomJS('C:\\Users\\Michael\\Anaconda3\\envs\\QS\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe') 
            # driver = webdriver.Chrome()
            driver.get(contenturl)

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "//iframe[starts-with(@id,'QT_IFRAME')]")))
            except:
                pass

            #Very complicated way to find the dynamically named JavaScript created iframe within the HTML doc. html below:
            # <iframe frameborder='0' scolling='no' width='100%'
            # id='QT_IFRAME_1502144948271937491' src='//someurl'
            #   #Document
            driver.switch_to_frame(driver.find_element_by_xpath("//iframe[starts-with(@id,'QT_IFRAME')]"))

            # Describe how long the scrape took to execute
            print('Scrape took ' + str(dt.now() - startTime))

            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find('table', attrs={'class': 'gr_table_b1'})
            table_body = table.find('tbody')

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

        path = str(st_dataPath) + str(account_name) + item
        df = pd.DataFrame(all_data)
        df.to_pickle(path)



        #***** beautiful soup and requests method (does not work with JS rendering) ****************
        # if response.status_code != requests.codes.ok:
        #     response.raise_for_status()
        # print(response.encoding) # allows you to manually set the encoding
        # print(response.content) # one of the first lines give the encoding guessed by requests based on the script.
        # print(response.status_code)   # 200 is successful connection
        # print(response.text[:1000])
        # print(response.cookies)  # shows any cookies in the response
        # print(contenturl)

if __name__ == '__main__':

    c_dataobj = da.DataAccess(sourcein=da.DataSource.YAHOO)
    ls_data = c_dataobj.get_info_from_account(c_dataobj.accountfiles)

    fund_info(ls_data, c_dataobj.datafolder, )
