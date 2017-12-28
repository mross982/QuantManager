import DataAccess as da
import api
import optimize
import scraper
import visuals
import sys
import os


if len(sys.argv)>1:
	c_dataobj = da.DataAccess(sys.argv[1])
else:
	c_dataobj = da.DataAccess(da.DataSource.FUND)


if c_dataobj.source == da.DataSource.FUND:
	# **************************************** API call ***********************
	# api.API.get_MF_close(c_dataobj) # Get mutual fund adjusted close data

	# *********************************** Optimize Portfolios **************************************
	# optimize.portfolio_optimizer.main(c_dataobj) # Optimize portfolio

	# *************************************** Create Images ******************************************
	# visuals.create_plots(c_dataobj)

	# ************************************** Scrap Data *******************************************
	# scraper.html_scraper.fund_desc(c_dataobj) # fund name, star rating, benchmark, alpha, beta.	
	# scraper.java_scraper.fund_individual_desc(c_dataobj) # 30-day SEC Yield, Category, Credit Quality, Expenses, Fee Level,
	# Investment Style, Load, Min. Inv., Status, TTM Yield, Total Assets, Total Mkt, Turnover

	# *************************** Review pkl files by converting to csv *******************************
	# Converts pkl to csv when given a filename
	# print('Enter a filename and pathway to be converted to a csv. Don\'t include the file extension.')
	# filename = input('Filename: ')
	# da.DataAccess.dataframe_to_csv(c_dataobj, filename)

	# *********************************** SP500 sectors Index **************************************
	# scraper.IndexScrapers.wiki_sp500_sectors(c_dataobj) # scrape SP 500 index info and pull financial data via api
	visuals.sector_stock_returns(c_dataobj)




	# scraper.java_scraper.fund_holdings(c_dataobj) # work in progress

	# scraper.WebScrapers.morning_star_quant_desc(c_dataobj, tickers) # JS rendererd data (SLOW)
	# scraper.WebScrapers.morning_star_fund_sectors(c_dataobj, tickers)
	