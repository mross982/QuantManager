import DataAccess as da
import utility as ut
import sys
import os


if len(sys.argv)>1:
	c_dataobj = da.DataAccess(sys.argv[1])
	# a keyword can be assigned to run a different set of code
else:
	c_dataobj = da.DataAccess(da.DataSource.FUND)
	# else, it runs the mutual fund program


if c_dataobj.source == da.DataSource.FUND:
	
	import scraper

	# # ************************************ Scrape lists of data ***********************************
	# scraper.IndexScrapers.wiki_sp500_sectors(c_dataobj) # scrape SP 500 index info and pull financial data via api

	# # **************************************** API call ***********************
	import api
	api.API.get_MF_close(c_dataobj) # Get mutual fund adjusted close data
	
	# *********************************** Optimize Portfolios **************************************
	import optimize
	optimize.portfolio_optimizer.main(c_dataobj) # Optimize portfolio

	# # *************************************** Create Images ******************************************
	import visuals
	visuals.create_plots(c_dataobj, verbose=False)
	visuals.index_plots(c_dataobj)

	# # ************************************** Scrap Qualitative Data *******************************************
	# scraper.html_scraper.fund_desc(c_dataobj) # fund name, star rating, benchmark, alpha, beta.	
	# scraper.java_scraper.fund_individual_desc(c_dataobj) # 30-day SEC Yield, Category, Credit Quality, Expenses, Fee Level,
	# Investment Style, Load, Min. Inv., Status, TTM Yield, Total Assets, Total Mkt, Turnover



	# **************************** Work in Progress ****************************************************
	# scraper.java_scraper.fund_holdings(c_dataobj) # work in progress

	# scraper.WebScrapers.morning_star_quant_desc(c_dataobj, tickers) # JS rendererd data (SLOW)
	# scraper.WebScrapers.morning_star_fund_sectors(c_dataobj, tickers)
	
	pass

if c_dataobj.source == da.DataSource.CRYPTO:
	# @ keyword: 'Crypto'
	import scraper
	import api

	# # ************************************ Scrape lists of data ***********************************
	scraper.Crypto.market_list(c_dataobj) # scrape 

	# # **************************************** API call ***********************
	api.API.get_crypto_close(c_dataobj)




if c_dataobj.source == da.DataSource.UTILITY:
	# *************************** Review pkl files by converting to csv *******************************
	# @ keyword: 'Utility'
	# Converts pkl to csv when given a filename

	print('Enter a filepath to be converted to a csv.')
	filename = input('Filename: ')
	ut.DataAccess.dataframe_to_csv(filename)


	# print('Enter a filepath to be converted to a pkl.')
	# filename = input('Filename: ')
	# da.DataAccess.csv_to_dataframe(filename)