import numpy as np
import pandas as pd
import DataAccess as da
import sys
import portfolioopt as pfopt
import matplotlib.pyplot as plt
import cvxopt as opt
from cvxopt import blas, solvers
import itertools
import os
import json


class scope(object):
	TIMESERIES = {'3months': 63, '6months': 126, '1year': 252, '3years': 756}

class portfolio_optimizer(object):
	'''
	
	'''

	def main(self):

		# Use N the same way it is used in the rsi calculator, to loop over larger segments of the data i.e. 3 months
		# 6 months, 1 year, etc. all while passing the same dataframe.

		ls_acctdata = da.DataAccess.get_info_from_account(self)
		for acct in ls_acctdata:

			df_data = da.DataAccess.get_dataframe(self, acct[0], clean=True)

			f = open(os.path.join(self.datafolder, acct[0] + '_optimize.json'), 'w+')

			time_series = scope.TIMESERIES
			# time_series['5years'] = len(df_data.index)

			for k,v in time_series.items():

				df_data = df_data[v:]

				returns = df_data.pct_change()
				cov_mat = returns.cov()
				avg_rets = returns.mean()
				
				try:
					#***************** Minimum variance portfolio ***********************
					title = 'Minimum_variance_portfolio_%s' % k
					weights = pfopt.min_var_portfolio(cov_mat)
					weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights		
					weights = weights[weights!=0]
					ret = (weights * avg_rets).sum()
					std = (weights * returns).sum(1).std()
					sharpe = ret / std

					w = dict(weights)
					opt = dict()
					
					opt['portfolio'] = w
					opt['title'] = title
					opt['expectedreturn'] = ret
					opt['std'] = std
					opt['sharpe'] = sharpe
					json.dump(opt, f)

					
					#********* Markowitz Portfolio with target return ************************
					target_ret = avg_rets.quantile(0.7)
					title = 'Markowitz_portfolio_target_return:%s_%s' % (round(target_ret, 4), k)
					weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret)
					weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
					weights = weights[weights!=0]
					weights = round(weights, 4)
					ret = (weights * avg_rets).sum()
					std = (weights * returns).sum(1).std()
					sharpe = ret / std

					w = dict(weights)
					opt = dict()
					
					opt['portfolio'] = w
					opt['title'] = title
					opt['expectedreturn'] = ret
					opt['std'] = std
					opt['sharpe'] = sharpe
					json.dump(opt, f)

				
					#***************** Tangency Portfolio *******************************
					title = 'Tangency_portfolio_%s' % k
					weights = pfopt.tangency_portfolio(cov_mat, avg_rets)
					weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
					weights = weights[weights!=0]
					weights = round(weights, 4)
					ret = (weights * avg_rets).sum()
					std = (weights * returns).sum(1).std()
					sharpe = ret / std
					
					w = dict(weights)
					opt = dict()
					
					opt['portfolio'] = w
					opt['title'] = title
					opt['expectedreturn'] = ret
					opt['std'] = std
					opt['sharpe'] = sharpe
					json.dump(opt, f)
				except:
					pass

				# portfolio_optimizer.section("Markowitz portfolio (long/short, target return: {:.5f})".format(target_ret))
				# weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret, allow_short=True)
				# weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
				# weights = weights[weights!=0]
				# portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

				# portfolio_optimizer.section("Markowitz portfolio (market neutral, target return: {:.5f})".format(target_ret))
				# weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret, allow_short=True, market_neutral=True)
				# weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
				# weights = weights[weights!=0]
				# portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

				# portfolio_optimizer.section("Tangency portfolio (long/short)")
				# weights = pfopt.tangency_portfolio(cov_mat, avg_rets, allow_short=True)
				# weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
				# weights = weights[weights!=0]
				# portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)



if __name__ == '__main__':

	if len(sys.argv)>1:
		c_dataobj = da.DataAccess(sourcein=sys.argv[1], verbose=False)
	else:
		c_dataobj = da.DataAccess(sourcein=da.DataSource.YAHOO, verbose=False)

	portfolio_optimizer.main(c_dataobj)

	