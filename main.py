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
	c_dataobj = da.DataAccess(da.DataSource.YAHOO)


if c_dataobj.source == da.DataSource.YAHOO:
	# API call
	# api.API.getYahooData(c_dataobj, da.DataAccess.get_info_from_account(c_dataobj)) # Get financial data

	# Optimize Portfolios
	optimize.portfolio_optimizer.main(c_dataobj) # Optimize portfolio

	# Create Images
	# visuals.line_chart.plot_returns(c_dataobj)
	# visuals.scatter_plot.plot_sharperatio(c_dataobj)
	# visuals.scatter_plot.efficient_frontier(c_dataobj)

	# scraper.IndexScrapers.wiki_sp500_sectors(c_dataobj) # get SP 500 index info
	# sp500_index_json = da.DataAccess.get_json(c_dataobj, c_dataobj.indexdir) # Get SP 500 financial data.
	# api.API.getGoogleData(c_dataobj, da.DataAccess.json_to_ls_acctdata(c_dataobj, sp500_index_json), source='index')
	
	# opt_data = da.DataAccess.get_json(c_dataobj, c_dataobj.datafolder)
	# tickers = scraper.optimized_tickers(opt_data)
					
	# tickers = ['JDMNX', 'DODGX', 'PLGIX'] # ******************** For Testing ONLY ******************
	# scraper.mstar_fund_desc.fund_desc(c_dataobj, tickers) # HTML data (FAST)
	# scraper.mstar_quant_desc.performance_data(c_dataobj)

	# scraper.WebScrapers.morning_star_quant_desc(c_dataobj, tickers) # JS rendererd data (SLOW)
	# scraper.WebScrapers.morning_star_fund_sectors(c_dataobj, tickers)
	