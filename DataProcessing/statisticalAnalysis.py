import os, warnings
import pandas as pd, numpy as np, pingouin as pg, matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot


data_dir = 'C:\\Users\\adr-smith\\Documents\\GitHub\\PlatformEvaluation\\Output logs'
filenames = [ 'combined_df.csv', 'cl_df.csv', 'nl_df.csv' ]


debug = False
save = False

output_log = pd.DataFrame(columns=[ 'load','var', 'sig_high', 'sig_high_p', 'sig_low', 'sig_low_p','spher', 'spher_p', 'norm_res'], index=[0] )

if __name__ == '__main__':
	
	for file in filenames:
		filepath = os.path.join( data_dir, file )
		data = pd.read_csv( filepath, index_col=0 )
		data['factor_comb'] = data['Feedback'].astype(str) + '-' + data['Session'].astype(str)

		for var in data.columns[3:29]:
			
			_tmp_df = pd.DataFrame(index=[0], columns=[ 'load','var', 'sig_high', 'sig_high_p', 'sig_low', 'sig_low_p','spher', 'spher_p', 'norm_res'])
			_tmp_df['load'] = file[:4].split( '_', 1 )[0].upper()
			_tmp_df['var'] = var
			
			# Pinguoin has a lot of warnings that clog up the monitor, turning them off while using these functions
			warnings.filterwarnings( 'ignore' )
   
			# Sphericity checks for the dependant variable in question
			spher_check = pg.sphericity( data=data, dv=var, within=['Session','Loading'], subject='ID' )[-1].round(3)
			if spher_check > 0.05: 
				if debug: print('{} Data has met criteria of Sphericity ( p = {} ), type 2 error controlled'.format(var, spher_check))
				_spher_str = 'PASS'
    			
			else: 
				if debug: print('### Err:\tSphericity check failed ( p = {} ), for {} in {}'.format(round(spher_check,3), var, file))
				_spher_str = 'FAIL'

			_tmp_df['spher'] = _spher_str
			_tmp_df['spher_p'] = spher_check

   
			# Normality checks
			norm_check = pg.normality(data=data, dv=var, group='factor_comb' )
			norm_count = norm_check['normal'].value_counts()
			norm_sum = norm_count.sum()
			
			if ( norm_count[True] / norm_sum ) == 1: _norm_res = 'Perfectly normal'
			elif ( norm_count[True] / norm_sum ) > 0.75:	_norm_res = 'Highly normal'
			elif ( norm_count[True] / norm_sum ) > 0.5:	_norm_res = 'Normal'
			else: _norm_res = False 
   
			_tmp_df['norm_res'] = _norm_res
   
			# Runs Mixed-Mode ANOVA on dependant variable across sessions
			aov = data.mixed_anova( dv=var, within='Session', subject='ID', between='Feedback')
			warnings.filterwarnings( 'default' )

			high_str = 'None'
			high_p_str = 'None'
			low_str = 'None'
			low_p_str = 'None'
   
			if (aov['p-unc'] <= 0.05).any() : 
		
				high_significance = aov[(aov['p-unc'] <= 0.05)]['Source']
				
				for val in high_significance.values:
        
					if val != 'Session': 
						fig = interaction_plot(x=data['Session'], trace=data['Feedback'], response=data[var])
						plt.show()
					if high_str != 'None':
						high_str = high_str + ', ' + str( val )
						high_p_str = high_p_str + ', ' + str(aov[aov['Source']==val]['p-unc'].round(3).values[0])
					else: 
						high_str = str( val ) 
						high_p_str = str(aov[aov['Source']==val]['p-unc'].round(3).values[0])

			_tmp_df['sig_high'] = high_str
			_tmp_df['sig_high_p'] = high_p_str
					
			if (aov['p-unc'] <= 0.1).any() and (aov['p-unc'] > 0.05).any() :
			
				low_significance = aov[(aov['p-unc'] <= 0.1) & (aov['p-unc'] > 0.05)]['Source']

				for val in low_significance.values:
					if low_str != 'None':
						low_str = low_str + ', ' + str( val )
						low_p_str = low_p_str + ', ' + str(aov[aov['Source']==val]['p-unc'].round(3).values[0])
					else: 
						low_str = str( val ) 
						low_p_str = str(aov[aov['Source']==val]['p-unc'].round(3).values[0])

			_tmp_df['sig_low'] = low_str
			_tmp_df['sig_low_p'] = low_p_str

			output_log = pd.concat( [output_log, _tmp_df] )

			# fig = interaction_plot(x=data['Session'], trace=data['Feedback'], response=data[var])
			# plt.show()

	output_log.reset_index(inplace=True, drop=True)
	if save: output_log.to_csv(os.path.join( os.getcwd(), os.path.join('Output logs', 'stats_summary.csv')))
