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


class portfolio_visualizer(object):
	'''

	'''
	def returns(self, n=242, plot=False):

		# for fun I am testing the last three months returns
		# n = round(n/3)

		df_data = da.DataAccess.get_dataframe(self, clean=True)

		syms = df_data.columns.tolist()

		df = df_data.copy(deep=True)
		df = df[-n:]
		ls_index = df.index.tolist()

		df = df.values # converts dataframe to numpy array

		return_vec = df/df[0,:] # Divides each column by the first value in the column (i.e % returns)

		# returns = df_data.pct_change()
		# cov_mat = returns.cov()
		# avg_rets = returns.mean()

		# %matplotlib inline   # may be necessary to appear correctly in jupyter notebook

		if plot == True:
			filepath = os.path.join(self.imagefile, '3mo_All_Returns.pdf')
			f = plt.figure(num=None, figsize=(12, 6), dpi=80, facecolor='w', edgecolor='k')
			plt.clf()
			plt.plot(ls_index, return_vec)
			plt.legend(syms)
			plt.ylabel('Adjusted Close')
			plt.xlabel('Date')
			plt.show()
			# f.savefig(filepath)

		return return_vec


	def rand_weights(n):
		''' Produces n random weights that sum to 1 '''
		k = np.random.rand(n)
		return k / sum(k)


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
	
		#*************** REMOVED THIS FILTER ********************
		# This recursion reduces outliers to keep plots pretty  
		# if sigma > 2: # a filter that only allows to plot portfolios with a standard deviation of < 2 for better illustration.
		# 	return random_portfolio(returns)
		return mu, sigma

	def main(return_vec, plot=False):
		

		n_portfolios = 1000
		# means, stds = np.column_stack([portfolio_visualizer.random_portfolio(return_vec) for _ in range(n_portfolios)])

		means, stds = np.column_stack([portfolio_visualizer.random_portfolio(return_vec) for _ in range(n_portfolios)])
		# print(type(means))
		# print(means)
		# print(type(stds))
		# print(stds)

		if plot == True:
			plt.plot(stds, means, 'o', markersize=5)
			plt.xlabel('std')
			plt.ylabel('mean')
			plt.title('Mean and standard deviation of returns of randomly generated portfolio weights')
			plt.show()


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

	returns = portfolio_visualizer.returns(c_dataobj, plot=False)
	# weights, returns, risks = portfolio_visualizer.optimal_portfolio(returns)
	# print(weights)
	# print(returns)
	# print(risks)
	portfolio_visualizer.main(returns, plot=True)