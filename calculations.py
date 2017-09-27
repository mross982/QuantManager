import numpy as np
import pandas as pd
import DataAccess as da
import sys
import portfolioopt as pfopt
import calculations as calc


class portfolio_optimizer(object):
	'''
	
	'''

	def section(caption):
		print('\n\n' + str(caption))
		print('-' * len(caption))


	def print_portfolio_info(returns, avg_rets, weights):
		"""
		Print information on expected portfolio performance.
		"""
		ret = (weights * avg_rets).sum()
		std = (weights * returns).sum(1).std()
		sharpe = ret / std
		print("Optimal weights:\n{}\n".format(weights))
		print("Expected return:   {}".format(ret))
		print("Expected variance: {}".format(std**2))
		print("Expected Sharpe:   {}".format(sharpe))


	def main(self, verbose=False):

		df_data = da.DataAccess.get_dataframe(self)
		
		
		# Need perminant solution to find instances of no data.
		del df_data['VMFXX']

		returns = df_data.pct_change()
		cov_mat = returns.cov()
		avg_rets = returns.mean()
		
		if verbose == True:
			portfolio_optimizer.section("Example returns")
			print(returns.head(10))
			print("...")

			portfolio_optimizer.section("Average returns")
			print(avg_rets)

			portfolio_optimizer.section("Covariance matrix")
			print(cov_mat)

		portfolio_optimizer.section("Minimum variance portfolio (long only)")
		weights = pfopt.min_var_portfolio(cov_mat)
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

		portfolio_optimizer.section("Minimum variance portfolio (long/short)")
		weights = pfopt.min_var_portfolio(cov_mat, allow_short=True)
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

		# Define some target return, here the 70% quantile of the average returns
		target_ret = avg_rets.quantile(0.7)

		portfolio_optimizer.section("Markowitz portfolio (long only, target return: {:.5f})".format(target_ret))
		weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret)
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

		portfolio_optimizer.section("Markowitz portfolio (long/short, target return: {:.5f})".format(target_ret))
		weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret, allow_short=True)
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

		portfolio_optimizer.section("Markowitz portfolio (market neutral, target return: {:.5f})".format(target_ret))
		weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret, allow_short=True, market_neutral=True)
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

		portfolio_optimizer.section("Tangency portfolio (long only)")
		weights = pfopt.tangency_portfolio(cov_mat, avg_rets)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

		portfolio_optimizer.section("Tangency portfolio (long/short)")
		weights = pfopt.tangency_portfolio(cov_mat, avg_rets, allow_short=True)
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

if __name__ == '__main__':

	if len(sys.argv)>1:
		c_dataobj = da.DataAccess(sourcein=sys.argv[1], verbose=False)
	else:
		c_dataobj = da.DataAccess(sourcein=da.DataSource.YAHOO, verbose=False)

	portfolio_optimizer.main(c_dataobj)

	