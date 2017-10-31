import DataAccess as da
import api
import optimize
import scraper
import visuals
import sys


if len(sys.argv)>1:
	c_dataobj = da.DataAccess(sys.argv[1])
else:
	c_dataobj = da.DataAccess(da.DataSource.YAHOO)


if c_dataobj.source == da.DataSource.YAHOO:
	# api.API.getYahooData(c_dataobj, da.DataAccess.get_info_from_account(c_dataobj)) # Get financial data
	# optimize.portfolio_optimizer.main(c_dataobj) # Optimize portfolio 

	# scraper.WebScrapers.wiki_sp500_sectors(c_dataobj) # get SP 500 index info
	# sp500_index_json = da.DataAccess.get_json(c_dataobj, c_dataobj.indexdir) # Get SP 500 financial data.
	# api.API.getGoogleData(c_dataobj, da.DataAccess.json_to_ls_acctdata(c_dataobj, sp500_index_json), source='index')
	# print(sp500_index_json)

	# open optimized data for all accounts then scrape Quant, Qual, and Fund Sectors data.
	opt_data = da.DataAccess.get_json(c_dataobj, c_dataobj.datafolder)
	tickers = [] # a list of unique tickers found in optimized data
	# opt_data is a list with n+1 entries: one for each account (n) and a combined all accounts (+1)
	for acct in opt_data: # in each of these entries,
		# print(acct[0]) # index 0 is always the account name
		# print(acct[1]) # index 1 is all the data associated with the account of which there are 13 objects
		for info in acct[1]: # in the data for each account
			# print(len(info)) # there is a dictionary with 5 key:value pairs
			# print(info.keys()) # keys include: sharpe, title, portfolio, std, expectedreturn
			# print(acct[0]) # name of account
			# print(info['title']) # name of optimization & time period
			# print(info['portfolio']) # dictionary of ticker: weight
			for k in info['portfolio'].keys():
				if k not in tickers:
					tickers.append(k)

	print(tickers)



