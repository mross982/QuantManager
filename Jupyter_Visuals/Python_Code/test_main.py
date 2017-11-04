import sys
sys.path.insert(0, 'C:\Users\Michael\Documents\Computation_Investing\QuantMgmt')
import os
import DataAccess as da

c_dataobj = da.DataAccess(da.DataSource.YAHOO)
ls_acctdata = c_dataobj.get_info_from_account()
for acct in ls_acctdata:
	filename = acct[0] + '-' + da.DataItem.ADJUSTED_CLOSE + '.pkl'
	filename = filename.replace(' ', '')
	filepath = os.path.join(c_dataobj.datafolder, filename)		
	df_data = c_dataobj.get_dataframe(filepath, clean=True)
	print(df_data.head())