import numpy as np
import pandas as pd
import DataAccess as da
import sys
import portfolioopt as pfopt
import calculations as calc
import matplotlib.pyplot as plt
import cvxopt as opt
from cvxopt import blas, solvers



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


	def main(self, n=-252, verbose=False):

		# Use N the same way it is used in the rsi calculator, to loop over larger segments of the data i.e. 3 months
		# 6 months, 1 year, etc. all while passing the same dataframe.
		df_data = da.DataAccess.get_dataframe(self, clean=True)

		df_data = df_data[n:]

		returns = df_data.pct_change()
		cov_mat = returns.cov()
		avg_rets = returns.mean()
		
		if verbose == True:
			portfolio_optimizer.section("Example returns")
			print(returns.head(10))
			print("...")

			portfolio_optimizer.section("Mean returns")
			print(avg_rets)

			portfolio_optimizer.section("Covariance matrix")
			print(cov_mat)
			sys.exit(0)

		portfolio_optimizer.section("Minimum variance portfolio (long only)")
		weights = pfopt.min_var_portfolio(cov_mat)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights		
		weights = weights[weights!=0]
		# df = weights.to_frame()
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)
		

		portfolio_optimizer.section("Minimum variance portfolio (long/short)")
		weights = pfopt.min_var_portfolio(cov_mat, allow_short=True)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
		weights = weights[weights!=0]
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

		# Define some target return, here the 70% quantile of the average returns
		target_ret = avg_rets.quantile(0.7)

		# target_ret = 0.0009


		portfolio_optimizer.section("Markowitz portfolio (long only, target return: {:.5f})".format(target_ret))
		weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
		weights = weights[weights!=0]
		df = weights.to_frame()
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)
		
		portfolio_optimizer.section("Markowitz portfolio (long/short, target return: {:.5f})".format(target_ret))
		weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret, allow_short=True)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
		weights = weights[weights!=0]
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

		portfolio_optimizer.section("Markowitz portfolio (market neutral, target return: {:.5f})".format(target_ret))
		weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret, allow_short=True, market_neutral=True)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
		weights = weights[weights!=0]
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)

		portfolio_optimizer.section("Tangency portfolio (long only)")
		weights = pfopt.tangency_portfolio(cov_mat, avg_rets)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
		weights = weights[weights!=0]
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)
		

		portfolio_optimizer.section("Tangency portfolio (long/short)")
		weights = pfopt.tangency_portfolio(cov_mat, avg_rets, allow_short=True)
		weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
		weights = weights[weights!=0]
		portfolio_optimizer.print_portfolio_info(returns, avg_rets, weights)


class portfolio_visualizer(object):
	'''

	'''
	def randopt_visual(self, n=242):

		df_data = da.DataAccess.get_dataframe(self, clean=True)
		df_data = df_data[n:]

		returns = df_data.pct_change()
		cov_mat = returns.cov()
		avg_rets = returns.mean()

		# ********** Copied Script **************

		## NUMBER OF ASSETS
		n_assets = 4

		## NUMBER OF OBSERVATIONS
		n_obs = 1000

		return_vec = np.random.randn(n_assets, n_obs)

		# %matplotlib inline   # may be necessary to appear correctly in jupyter notebook
		f = plt.figure()
		plt.plot(return_vec.T, alpha=.4);
		plt.xlabel('time')
		plt.ylabel('returns')
		plt.show()
		# f.savefig("random return series.pdf")

		# These return series can be used to create a wide range of portfolios, which all
		# have different returns and risks (standard deviation). We can produce a wide range
		# of random weight vectors and plot those portfolios. As we want all our capital to be invested, this vector will have to sum to one.

	def rand_weights(n):
		''' Produces n random weights that sum to 1 '''
		k = np.random.rand(n)
		return k / sum(k)

		print(rand_weights(n_assets))
		print(rand_weights(n_assets))

	def random_portfolio(returns):
		''' 
		Returns the mean and standard deviation of returns for a random portfolio
		'''

		p = np.asmatrix(np.mean(returns, axis=1))
		w = np.asmatrix(portfolio_visualizer.rand_weights(returns.shape[0]))
		C = np.asmatrix(np.cov(returns))
	
		mu = w * p.T  # Expected return
		# p.T is the transpose for the mean returns for each time series
		# w is the weight vector of the portfolio

		sigma = np.sqrt(w * C * w.T)  #standard deviation
		# C is covariance matrix of the returns NOTE: if it used the simple std dev std(array(ret_vec).T*w)
		# the result would be slightly different as it would not take covariances into account.!
		#********* make sure this is the same in the portfolioopt package *****************************
	
		# This recursion reduces outliers to keep plots pretty
		if sigma > 2: # a filter that only allows to plot portfolios with a standard deviation of < 2 for better illustration.
			return random_portfolio(returns)
		return mu, sigma

	def main():
		## NUMBER OF ASSETS
		n_assets = 4

		## NUMBER OF OBSERVATIONS
		n_obs = 1000

		return_vec = np.random.randn(n_assets, n_obs)
		print(return_vec)
		sys.exit(0)

		n_portfolios = 500
		means, stds = np.column_stack([portfolio_visualizer.random_portfolio(return_vec) for _ in range(n_portfolios)])

		print(type(means))
		print(means)
		# print(shape(means))
		print(type(stds))
		print(stds)
		# print(shape(stds))

		# plt.plot(stds, means, 'o', markersize=5)
		# plt.xlabel('std')
		# plt.ylabel('mean')
		# plt.title('Mean and standard deviation of returns of randomly generated portfolios')


	def optimal_portfolio(returns):

		n = len(returns)
		returns = np.asmatrix(returns)
	
		N = 100
		mus = [10**(5.0 * t/N - 1.0) for t in range(N)]
	
		# Convert to cvxopt matrices
		S = opt.matrix(np.cov(returns))
		pbar = opt.matrix(np.mean(returns, axis=1))
		
		# Create constraint matrices
		G = -opt.matrix(np.eye(n))   # negative n x n identity matrix
		h = opt.matrix(0.0, (n ,1))
		A = opt.matrix(1.0, (1, n))
		b = opt.matrix(1.0)
		
		# Calculate efficient frontier weights using quadratic programming
		portfolios = [solvers.qp(mu*S, -pbar, G, h, A, b)['x'] 
			for mu in mus]
		## CALCULATE RISKS AND RETURNS FOR FRONTIER
		returns = [blas.dot(pbar, x) for x in portfolios]
		risks = [np.sqrt(blas.dot(x, S*x)) for x in portfolios]
		## CALCULATE THE 2ND DEGREE POLYNOMIAL OF THE FRONTIER CURVE
		m1 = np.polyfit(returns, risks, 2)
		x1 = np.sqrt(m1[2] / m1[0])
		# CALCULATE THE OPTIMAL PORTFOLIO
		wt = solvers.qp(opt.matrix(x1 * S), -pbar, G, h, A, b)['x']
		weights = np.asarray(wt)
		return weights, returns, risks

	# weights, returns, risks = optimal_portfolio(return_vec)

	# plt.plot(stds, means, 'o')
	# plt.ylabel('mean')
	# plt.xlabel('std')
	# plt.plot(risks, returns, 'y-o')


if __name__ == '__main__':

	if len(sys.argv)>1:
		c_dataobj = da.DataAccess(sourcein=sys.argv[1], verbose=False)
	else:
		c_dataobj = da.DataAccess(sourcein=da.DataSource.YAHOO, verbose=False)

	# portfolio_optimizer.main(c_dataobj, verbose=False)
	# rsi = technical_indicators.rsi(c_dataobj)
	
	#visulizer testing
	# portfolio_visualizer.randopt_visual(c_dataobj)
	portfolio_visualizer.main()