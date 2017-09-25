# Import Section
# special IPython command to prepare the notebook for matplotlib

import requests 
import numpy as np
import pandas as pd                               # pandas
from StringIO import StringIO
import matplotlib.pyplot as plt                   # module for plotting 
import datetime as dt                             # module for manipulating dates and times
from collections import OrderedDict
import sys

# Import scipy library
# import scipy as sp

# Import sklearn Libraries
# import sklearn
# import seaborn as sns

# Import module matlabplot for visaulizations
from matplotlib import pyplot as plt
from matplotlib import rcParams
import math

# Import Beautiful Soup library
import bs4
from BeautifulSoup import BeautifulSoup
import urllib2

# Defining a DataFrame for Fund Family which contains Fund Family and the Fund Family URL.
FFamily = pd.DataFrame(columns=['Fund_Family','MorningstarURL'])

# List of 10 largest Mutual Fund Families
FFamily.loc[0] = ['Vanguard','http://quicktake.morningstar.com/fundfamily/vanguard/0C00001YUF/fund-list.aspx']
FFamily.loc[1] = ['American Funds','http://quicktake.morningstar.com/fundfamily/american-funds/0C00001YPH/fund-list.aspx']
FFamily.loc[2] = ['PIMCO Funds','http://quicktake.morningstar.com/fundfamily/pimco/0C00004ALK/fund-list.aspx']
FFamily.loc[3] = ['T. Rowe Price','http://quicktake.morningstar.com/fundfamily/t-rowe-price/0C00001YZ8/fund-list.aspx']
FFamily.loc[4] = ['JP Morgan','http://quicktake.morningstar.com/fundfamily/jpmorgan/0C00001YRR/fund-list.aspx']
FFamily.loc[5] = ['Fidelity Investments','http://quicktake.morningstar.com/fundfamily/fidelity-investments/0C00001YR0/fund-list.aspx']
FFamily.loc[6] = ['Franklin Templeton Investments','http://quicktake.morningstar.com/fundfamily/franklin-templeton-investments/0C00004AKN/fund-list.aspx']
FFamily.loc[7] = ['BlackRock','http://quicktake.morningstar.com/fundfamily/blackrock/0C000034YC/fund-list.aspx']
FFamily.loc[8] = ['Columbia','http://quicktake.morningstar.com/fundfamily/columbia/0C00001YQG/fund-list.aspx']
FFamily.loc[9] = ['Oppenheimer Funds','http://quicktake.morningstar.com/fundfamily/oppenheimerfunds/0C00001YZF/fund-list.aspx']


# Fund Family DataFrame
Funds_family = pd.DataFrame(columns=['Fund_Name','Fund_Family','Fund_Ticker'])
i = 0

for index in range(0,len(FFamily)):
    # For each fund, fetch the MorningStar URL
    contenturl = FFamily.MorningstarURL[index]
    # Using urllib2 library.
    req = urllib2.Request(contenturl)
    page = urllib2.urlopen(req)
    # Using Beautiful Soup to read from page
    soup = BeautifulSoup(page)
    # Extract the information from the div which contains the class "syn_section_b1"
    table = soup.find("div", { "class" : "syn_section_b1" })
    # Loop to fetch all the fund tickers and its's names which is contained within href section of the URL
    for row in table.findAll('a'):
        # If we carefully observe the URL, the ticker information starts at 73
        if (row['href'][73:]) != '':
            Funds_family.loc[i] = [row.contents[0],FFamily['Fund_Family'][index],row['href'][73:]]
            i = i+1

#**************** Check notebook to see if frame matches what is expected. **************
print Funds_family.head()
print " Total number of funds for analysis : ",len(Funds_family)
sys.exit(0)

# Benchmark columns.
fund_benchmark_columns = ['Fund_Ticker','Benchmark_Index']
# Fund Benchmark DataFrame
fund_benchmark = pd.DataFrame(columns=fund_benchmark_columns)

# Loop for each fund for getting it's becnhmark
for i in range(0,len(Funds_family)):
    FUND_NAME = Funds_family['Fund_Ticker'][i]
    # try except exception block is used to ignore errors if any and moving forward for different funds.
    try:
        # Below is the AJAX request URL whose table contains the Benchmark
        ratingriskurl = "http://performance.morningstar.com/RatingRisk/fund/mpt-statistics.action?&t=XNAS:"+FUND_NAME+"&region=usa&culture=en-US&cur=&ops=clear&s=0P00001MK8&y=3&ep=true&comparisonRemove=null&benchmarkSecId=&benchmarktype="
        # Read the 0th value of the array
        mpt_statistics_bench = pd.read_html(ratingriskurl)[0]
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
        print "Index : ",i,"No Benchmark Data Found in Morningstar for Fund : ",FUND_NAME

# Reset the fund_benchmark dataframe.
fund_benchmark = fund_benchmark.reset_index(drop=True)

#**************** Check notebook to see if frame matches what is expected. **************
print fund_benchmark.head()

# Fetch all the distinct benchmarks for the above set of ~1277 funds
index_dup = fund_benchmark.drop_duplicates('Benchmark_Index')
# Total Distinct benchmarks for ~ 1277 funds
index_dup

mstar_benchmark_symbol = pd.DataFrame(index=range(0,len(index_dup)),columns=['Benchmark_Index','Mstar_Symbol'])

mstar_benchmark_symbol.loc[0] = ['S&P 500 TR USD','0P00001MK8']
mstar_benchmark_symbol.loc[1] = ['Morningstar Moderate Target Risk','0P0000J533']
mstar_benchmark_symbol.loc[2] = ['Barclays Municipal TR USD','0P00001G5X']
mstar_benchmark_symbol.loc[3] = ['MSCI ACWI Ex USA NR USD','0P00001MJB']
mstar_benchmark_symbol.loc[4] = ['Barclays US Agg Bond TR USD','0P00001G5L']
mstar_benchmark_symbol.loc[5] = ['MSCI ACWI NR USD','0P00001G8P']
mstar_benchmark_symbol.loc[6] = ['Morningstar Long-Only Commodity TR','0P00009FRD']
mstar_benchmark_symbol.loc[7] = ['BofAML USD LIBOR 3 Mon CM','0P00001L6O']
mstar_benchmark_symbol.loc[8] = ['Credit Suisse Mgd Futures Liquid TR USD','0P00001MK8']

mstar_benchmark_symbol

# Merging the Funds_family dataframe and fund_benchmark dataframe.
fund_df = pd.merge(Funds_family,fund_benchmark,how='left',on='Fund_Ticker')
fund_df = fund_df[fund_df['Benchmark_Index'].notnull()].reset_index(drop=True)

# Printing the head for Fund DataFrame.
fund_df.head()

# Example for a fund with ticker = 'JMGIX'
fund_df[fund_df['Fund_Ticker'] == 'JMGIX']
#fund_df.shape

# Exporting the Fund's DataFrame in a csv format. 
fund_df.to_csv("Fund_Metadata.csv")


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


def get_performance_data(url):
      '''
      This function "get_performance_data" scraps performance data using Beautiful soup
      and convert it to pandas dataframe.
      It also handles missing values.

      '''
      soup = BeautifulSoup(urllib2.urlopen(url).read()) # read data using Beautiful Soup
      table = soup.find('table')                        # find the table
      rows = table.findAll('tr')                        # Find all tr rows with the table
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
      data = data.ffill()                                      # fill null values

      return data

# Initializing the Fund Returns object.
fund_returns = {}

# 15 year returns data for each fund.
for i in range(0,len(fund_df)):
    # Fetch the Ticker.
    fund_name = fund_df['Fund_Ticker'][i]
    # Fetch the Benchmark
    fund_benchmark_var = fund_df['Benchmark_Index'][i]
    # Key to be stored
    key = "fund_returns_"+fund_name
    # Fetching the Fund's benchmark and it s symbol
    symbol = (mstar_benchmark_symbol[mstar_benchmark_symbol['Benchmark_Index'] == fund_benchmark_var]['Mstar_Symbol']).values[0]
    # Fund Returns URL, passing the Fund Ticker, the bechmark symbol and 15 years of data to the URL
    fund_ret_url = "http://performance.morningstar.com/Performance/fund/performance-history-1.action?&t=XNAS:"+fund_name+"&region=usa&culture=en-US&cur=&ops=clear&s="+symbol+"&ndec=2&ep=true&align=m&y=15&comparisonRemove=false&loccat=&taxadj=&benchmarkSecId=&benchmarktype="
    # Try Except block in case to encounter any errors
    try:
        # Calling get_performance_data function to scrape the data using Beautiful soup.
        fund_history = get_performance_data(fund_ret_url)
        # Calling fnc_transpose to Transpose the DataFrame
        fund_history = fnc_transpose(fund_history)
        fund_history = fund_history.reset_index()
        # Assigning the columns to the DataFrame.
        fund_history.columns = ['Year',fund_name+'_Returns',fund_benchmark_var,'Category (LB)','+/- S&P 500 TR USD','+/- Category (LB)','Annual_Net_Exp_Ratio','Turnover_Ratio','Rank_In_Category']
    except:
        # No returns Information then print and store an empty array in the value for that fund.
        print "No Returns Data available for Fund : ",fund_name
        # Creating an Empty DataFrame for fund with no returns
        fund_history = pd.DataFrame()
    # Assigning the DataFrame to the value
    fund_returns[key] = fund_history

fund_returns['fund_returns_FCNTX']

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
            print "Index : ",yt,", No Statitics available for Fund : ",fund_name," for ",i," years"
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
print " Total # of funds with 3 year analysis data : ",len(Fund_param_3)

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
print " Total # of funds with 5 year analysis data : ",len(Fund_param_5)

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
print " Total # of funds with 10 year analysis data : ",len(Fund_param_10)

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
print " Total # of funds with 15 year analysis : ",len(Fund_param_15)

# Print the header
Fund_param_15.head()

# Exporting the 15 years data to csv file

Fund_param_15.to_csv("Fund_statistics_15years.csv")

"""
1) TTM Yield :
A Company's Trailing Twelve Months(TTM) is a representation of its financial performance for a 12-month period, but typically not at its fiscal year end. Since quarterly reports rarely report how the company has done in the past 12 months, TTM tends to be calculated manually or found on various websites. Trailing 12 months figures can be calculated by subtracting the previous year's results from the same quarter as the most recent quarter reported and adding the difference to the latest fiscal year end results.
2) Load:
Load fees are fees incurred by the investor for investing in the mutual fund. There is an entry load fee for purchasing some units within fund and exit load fees for exiting the fund within say 1 year.
3) Portfolio Market Value:
The expected return of a market portfolio is identical to the expected return of the market as a whole. A bundle of investments that includes every type of asset available in the world financial market, with each asset weighted in proportion to its total presence in the market.
4) Total Assets :
The sum of current and long-term assets owned by a mutual fund.
5) Expense Ratio :
Fees charged on the Investor per year for investing in a fund.
6) FeeLevel :
The fees if it falls in the Low,Medium or High level bracket.
7) TurnOver Ratio :
The percentage of a mutual fund's holdings that have been turned over or replaced with other holdings in a given year.
8) Category Information :
The Category in which the fund is invested in, whether it is Large Cap Growth funds, or Large cap Value funds or Medium or Small Cap funds.
9) Management Information:
Who is the current manager of the Fund and for how many years the manager is managing the fund. Manager's tenure is very important as the returns are based on his/her style of investing and getting maximum returns.
"""

# Column values
class_values = ['Fund_Ticker','TTM_Yield','Load','PortfolioMktValue','TotalAssets','ExpenseRatio','FeeLevel',
                'Turnover','Status','MinInvestment','Yield','MorningstarCategory','InvestmentStyle']

# Pandas DataFrame fund_other_params
fund_other_params = pd.DataFrame()
fund_other = pd.DataFrame(columns=class_values)

# For Loop for fetch the parameters for each fund.
for fd in range(0,len(fund_df)):
    fund_name = fund_df['Fund_Ticker'][fd]
    print "Fund other paramters : ",fund_name
    try:
        # Fetching the parameters of the fund like Expense Ratio
        fund_oth_params_url = "http://quotes.morningstar.com/fund/c-standardized?&t=XNAS:"+fund_name+"&region=usa&culture=en-US&cur="
        fund_oth_params = pd.read_html(fund_oth_params_url,match='Max Front Load')[0]
        fund_oth_params.columns = fund_oth_params.loc[0]
        fund_oth_params = pd.DataFrame(pd.Series(fund_oth_params.loc[1])).T.reset_index(drop=True)
        fund_oth_params['Fund_Ticker'] = fund_name       
        
        # Fetching the annualized returns Since Inception
        fund_oth_params_ret = pd.read_html(fund_oth_params_url,match='Standardized Return')[0]
        fund_oth_params_ret.columns = ['Inception','Return','Tax_Return','Unnamed']
        fund_oth_params_ret = fund_oth_params_ret[fund_oth_params_ret['Inception'].str.contains('Inception',na=False)]
        fund_oth_params_ret['Fund_Ticker'] = fund_name
        fund_oth_params_ret = fund_oth_params_ret[['Fund_Ticker','Inception','Return']].reset_index(drop=True)
        var_inc = fund_oth_params_ret['Inception']
        start = var_inc[0].find('(')+1
        end = var_inc[0].find(')', start)
        fund_oth_params_ret['Inception'] = var_inc[0][start:end]

        # Fetching Fund Manager Information
        fund_management_url = "http://quotes.morningstar.com/fund/c-management?&t=XNAS:"+fund_name+"&region=usa&culture=en-US&cur="
        fund_management = pd.read_html(fund_management_url,match='Start')[0]
        fund_management = fund_management[fund_management[0].notnull()].tail(1).reset_index(drop=True)
        fund_management.columns = ['Fund_Manager','Manager_Start_Date']
        fund_management['Fund_Ticker'] = fund_name
        
        # Merging above 3 dataframes fund_oth_params,fund_oth_params_ret and fund_management and storing it in fund_other_params dataframe.
        fund_other_params_sub = pd.merge(fund_oth_params_ret,fund_oth_params,on='Fund_Ticker',how='inner')
        fund_other_params_sub = pd.merge(fund_other_params_sub,fund_management,on='Fund_Ticker',how='inner')
        fund_other_params = fund_other_params.append(fund_other_params_sub)
        
        # Fetching other parameters like TurnOver Ratio etc.
        url_param = urllib2.urlopen("http://quotes.morningstar.com/chart/fund/c-banner?&t=XNAS:"+fund_name+"&region=usa&culture=en-US&cur=") # Opens URLS
        htmlSource = url_param.read()
        param_soup = bs4.BeautifulSoup(htmlSource)
        param_table = param_soup.find('table', attrs={'class': 'gr_table_b1'})
        param_rows = param_table.findAll('td')
        fund_values = {}
        i=0
        # The below code is used for stripping the spaces and only getting the required value.
        for tr in param_rows:
            fund_values_sub = tr.findAll('span')
            if len(fund_values_sub) != 0:
                fund_values[i] = fund_values_sub[0]
                if (i == 2):
                    var_total_asset = fund_values_sub[2].contents[3].contents[0].splitlines()[1].strip()          
                i = i+1

        for j in range(0,len(fund_values)):
            try:
                fund_values[j] = fund_values[j].contents[1].contents[0].splitlines()[1].strip()
            except:
                try:
                    fund_values[j] = fund_values[j].contents[2].splitlines()[1].strip()
                except:
                    fund_values[j] = fund_values[j].contents[0].splitlines()[1].strip()

        class_series = pd.Series([fund_name,fund_values[0],fund_values[1],fund_values[2],var_total_asset,fund_values[3],\
                                   fund_values[4],fund_values[5],fund_values[6],fund_values[7],fund_values[8],fund_values[9],\
                                   fund_values[10]])

        col_df = pd.DataFrame()
        col_df = col_df.append(class_series,ignore_index=True)
        col_df.columns=class_values
        fund_other = fund_other.append(col_df)
    except:
        # Print all the funds who had issues in loading the parameters information
        print "Issues in finding paramters for Fund : ",fund_name

# Merging fund_other and fund_other_params.
fund_other = pd.merge(fund_other,fund_other_params,on='Fund_Ticker',how='inner')        

# Fetching the fund_other parameter data.

fund_other[fund_other['Fund_Ticker'] == 'FCNTX']

# New Dataframe fund_other_copy
fund_other_copy = fund_other.copy()
# Dropping the Minimum Investment column as it is not significant
fund_other_copy = fund_other_copy.drop('MinInvestment',1)
# Replacing the unicode character to Nan
fund_other_copy.replace(to_replace=u'\u2014',value=np.nan,inplace=True)
# Encoding thr Fund Manager column which contains unicode characters to UTF-8 so to export to csv is possible
fund_other_copy['Fund_Manager'] = fund_other_copy['Fund_Manager'].apply(lambda x: x.encode("UTF-8"))
# Stripping the trailing % character in the below 4 columns
fund_other_copy['TTM_Yield_in_percent'] = fund_other_copy['TTM_Yield'].str.strip('%')
fund_other_copy['ExpenseRatio_in_percent'] = fund_other_copy['ExpenseRatio'].str.strip('%')
fund_other_copy['Turnover_in_percent'] = fund_other_copy['Turnover'].str.strip('%')
fund_other_copy['Yield_in_percent'] = fund_other_copy['Yield'].str.strip('%')

# Converting the columns PortfolioMktValue and TotalAssets columns to millions
fund_other_copy['PortfolioMktValue_in_millions'] = fund_other_copy['PortfolioMktValue'].apply(lambda x: float(x.strip(' bil'))*1000.0 if x[-4:] == ' bil'  else  x.strip(' mil'))
fund_other_copy['TotalAssets_in_millions'] = fund_other_copy['TotalAssets'].apply(lambda x: float(x.strip(' bil'))*1000.0 if x[-4:] == ' bil'  else  x.strip(' mil'))

# Changing column name for Inception, it is Fund Inception
fund_other_copy['Fund_Inception'] = fund_other_copy['Inception']
# Dropping the changed percent columns 
fund_other_copy = fund_other_copy.drop(['TTM_Yield','ExpenseRatio','Turnover','Yield','PortfolioMktValue','TotalAssets','Inception'],1)

# Print the Header
fund_other_copy.head()

#pd.set_option('display.max_columns', None)
#fund_other1

#pd.set_option('display.max_rows',None)
#fund_other1['Fund_Manager'] = fund_other1['Fund_Manager'].map(lambda x: x[:-2])
#fund_other1['Fund_Manager']
#pd.reset_option('display.max_rows')

# Exporting the Fund Other Parameter data to csv file
fund_other_copy[['Fund_Ticker','Status','TTM_Yield_in_percent','PortfolioMktValue_in_millions','TotalAssets_in_millions',
             'ExpenseRatio_in_percent','Net Expense Ratio %','Gross Expense Ratio %','Turnover_in_percent','Yield_in_percent','Status','FeeLevel',\
             'Fund_Manager','Manager_Start_Date','Fund_Inception','MorningstarCategory','InvestmentStyle',\
             'FeeLevel','Load','Max Front Load %','Max Back Load %','Return']].to_csv("Fund_Parameters.csv")

url_fund_holding = "http://portfolios.morningstar.com/fund/holdingsExport?exportType=details&&t=XNAS:FUSEX&region=usa&culture=en-US&cur=&dataType=0&holnum="

fund_holding =pd.read_csv(url_fund_holding)
fund_holding

url_q_top_sector ="http://quotes.morningstar.com/fund/c-topSector?&t=XNAS:FUSEX&region=usa&culture=en-US&cur="

q_top_sector = pd.read_html(url_q_top_sector, match="Fund", header=0)[0]
q_top_sector

url_q_perf ="http://quotes.morningstar.com/fund/c-performance?&t=XNAS:FUSEX&region=usa&culture=en-US&cur=&benchmarkSecId=&benchmarktype="
q_perf = pd.read_html(url_q_perf, match="Fund", header=0)[0]
q_perf

