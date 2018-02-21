import DataAccess as da

class DataAccess(object):
	'''
	@summary:
	'''

	def dataframe_to_csv(filepath):
		'''
		This creates a csv file of a single dataframe.
		* Currently only used for spot checking downloaded data.
		'''

		df_data = da.DataAccess.get_dataframe(filepath)
		# outputfile = os.path.join(self.datafolder, filename + '.csv')
		# tup_pathfile = os.path.split(os.path.abspath(inputfile))
		outfilepath = filepath[:-3]
		outfilepath = outfilepath + 'csv'

		df_data.to_csv(outfilepath, encoding='utf-8')


	def csv_to_dataframe(csv_filepath):
		'''
		This will create a way to make edits to a pickled data frame by first converting it to csv, make any 
		corrective actions, then save the csv over the original pickled data frame.
		'''
		df_data = pd.read_csv(csv_filepath)
		outfilepath = csv_filepath[:-3]
		outfilepath = outfilepath + 'pkl'
		df_data.to_pickle(outfilepath)


	def optimize_db(self):
		'''
		here, you will go through the 10 year data set and run the usual optimization function, saving the three timescope
		optimized portfolios each run. This will increment one day then rerun the optimization function from t - 5 years to 
		present. Finally, I would like to create a chart to see how many options come into the opt portfolio, how long they
		stay on average, how often they change positions, how much the percetage moves, maybe chart them like the 3d line 
		chart in Excel.
		'''
		pass