import os
import warnings
import analysis_utils as utils
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt


# import rpy2.robjects as ro
# import rpy2.robjects.packages as rpackages
# from rpy2.robjects import pandas2ri, StrVector
# from rpy2.robjects.conversion import localconverter


data_dir = os.path.join( os.getcwd(), 'Output logs')
filenames = ['combined_df.csv', 'cl_df.csv', 'nl_df.csv']#, 'adl_df.csv']
# filenames = ['combined_df.csv']

# Directory definitions

log_path = os.path.join(os.getcwd(), os.path.join("Output logs"))
s8_9_path = os.path.join( log_path, 'S8 to 9' )

log_paths = [log_path]#, s8_9_path ]


# Plot definitions for colour and style
e_colors = ['chocolate', 'indigo']
colors = ['orange', 'rebeccapurple']

e_markers = ['.', '.']
markers = ['.', '.']

linestyles = ['solid', 'solid']

###

debug = False
save = True
s8_9 = False
s1_8 = True
s1_9 = False

conditions = ['fb','nfb','comb']

_output_log = pd.DataFrame(index=[0], columns=['load', 'var', 'mm_sig', 'mm_session','mm_feedback','mm_interaction', 'rm_sig','rm_session','rm_loading','rm_interaction','spher','spher_p','norm_res'])

if __name__ == '__main__':

	utils.close_event_loop()
	utils.atexit.register(utils.close_event_loop)

	for path in log_paths:  # Check and create directories to save resultant images to
		utils.check_or_create_folder(path)
  
	for condition in conditions: 
     
		output_log = _output_log	

		for file in filenames:  # Runs through each of the outputted results files from 0_extract_data.py
			filepath = os.path.join(data_dir, file)
			
 
			# Reads the .csv file into a pd.DataFrame object
			data = pd.read_csv(filepath, index_col=0)
	
			if s8_9:	data = data[data['Session'].isin([8,9])] #pd.concat([utils.extract_questionnaire_rows(data, 'Session', '8'), utils.extract_questionnaire_rows(data, 'Session', '9')])
			elif s1_9:	data = data
			elif s1_8:	data = data[data.Session != 9]
	
				
			if file == 'adl_df.csv':
				vars = data.columns[2:-2]
				within = 'Session'
			else:
				vars = data.columns[3:-1]
				within = ['Session', 'Loading']
    

			data['factor_comb'] = data['Feedback'].astype(
				str) + '-' + data['Session'].astype(str)  # Create factor comb for normailty checks


			if condition == 'fb': data = data[data.Feedback == True]
			elif condition == 'nfb': data = data[data.Feedback == False]
			else: data = data
			
			for var in vars:

				# Create a temp pd.DataFrame to store the analysis results of var
				_tmp_df = pd.DataFrame(index=[0], columns=['load', 'var', 'mm_sig', 'mm_session','mm_feedback','mm_interaction', 'rm_sig','rm_session','rm_loading','rm_interaction','spher','spher_p','norm_res'])
				_tmp_df['load'] = file[:4].split('_', 1)[0].upper() + ' ' + condition.upper()
				_tmp_df['var'] = var

				# Pinguoin has a lot of warnings that clog up the monitor, turning them off while using these functions
				warnings.filterwarnings('ignore')

				# Sphericity checks for the dependant variable in question
				spher_check = pg.sphericity(
					data=data, dv=var, within=within, subject='ID')[-1]#.round(3)

				if spher_check > 0.05:
					if debug:
						print('{} Data has met criteria of Sphericity ( p = {} )'.format(
							var, spher_check))
					_spher_str = 'PASS'
				else:
					if debug:
						print('### Err:\tSphericity check failed ( p = {} ), for {} in {}'.format(
							round(spher_check, 3), var, file))
					_spher_str = 'FAIL'

				# Stores sphericity check results to _tmp_df before being stored in the output log
				_tmp_df['spher'] = _spher_str
				_tmp_df['spher_p'] = spher_check

				# Normality checks
				norm_check = pg.normality(data=data, dv=var, group='factor_comb')
				norm_count = norm_check['normal'].value_counts()
				norm_sum = norm_count.sum()

				try:
					if (norm_count[True] / norm_sum) == 1:
						_norm_res = 'Perfectly normal'
					elif (norm_count[True] / norm_sum) > 0.75:
						_norm_res = 'Highly normal'
					elif (norm_count[True] / norm_sum) > 0.5:
						_norm_res = 'Normal'
					else:
						_norm_res = False
				except: _norm_res = False

				# Stores normality check results to _tmp_df before being stored in the output log
				_tmp_df['norm_res'] = _norm_res

				# Runs Mixed-Mode ANOVA on dependant variable across sessions
				aov = data.mixed_anova(
					dv=var, within='Session', subject='ID', between='Feedback', correction='auto')
				warnings.filterwarnings('default')

				if file == 'combined_df.csv': aov2 = data.rm_anova(dv=var, within=within, subject='ID')
				elif file != 'adl_df.csv': aov2 = data.rm_anova(dv=var, within='Session', subject='ID')
				else: aov2 = aov

				if debug: print(file, var, '\n', aov, '\n', aov2)

				#Create str variables to store results in
				high_str = 'None'
				high_p_str = 'None'
				low_str = 'None'
				low_p_str = 'None'

				p_interest = 'p-unc'
				p2_interest = 'p-unc'

				if 'p-GG-corr' in aov.columns:
					p_interest = 'p-GG-corr'
				if 'p-GG-corr' in aov2.columns:
					p2_interest = 'p-GG-corr'


				# If any results from the ANOVA have a p-value below significance report it in the dataframe
				if (aov[aov['Source'] != 'Session'][p_interest] < 0.05).any():
					_tmp_df['mm_sig'] = 'HIGH'
				elif (aov[aov['Source'] != 'Session'][p_interest] < 0.1).any():
					_tmp_df['mm_sig'] = 'LOW' 
				elif (aov[aov.Source == 'Session'][p_interest] < 0.1).any():
					_tmp_df['mm_sig'] = 'SESSION ONLY'
				else: _tmp_df['mm_sig'] = 'NONE'
	
				if (aov2[aov2.Source != 'Session'][p2_interest] < 0.05).any():
					_tmp_df['rm_sig'] = 'HIGH'
				elif (aov2[aov2.Source != 'Session'][p2_interest] < 0.1).any():
					_tmp_df['rm_sig'] = 'LOW'
				elif (aov2[aov2.Source == 'Session'][p2_interest] < 0.1).any():
					_tmp_df['rm_sig'] = 'SESSION ONLY'
				else: _tmp_df['rm_sig'] = 'NONE'

				loc = {'Session':'mm_session', 'Feedback':'mm_feedback','Interaction':'mm_interaction'}
				loc2 = {'Session':'rm_session', 'Loading':'rm_loading','Session * Loading':'rm_interaction'}

				for val in aov['Source'].values:  # Report all high sig results and store them in _tmp_df

					_tmp_df[loc[val]] = 'F({},{}) = {},\ p={}'.format(aov[aov['Source']==val]['DF1'].round(3).values[0],aov[aov['Source']==val]['DF2'].round(3).values[0],aov[aov['Source']==val]['F'].round(3).values[0],aov[aov['Source']==val]['p-unc'].round(3).values[0])

				if file !='adl_df.csv':
					for val in aov2['Source'].values:  # Report all high sig results and store them in _tmp_df
						if val != 'Error':
							try: _tmp_df[loc2[val]] = 'F({}) = {},\ p={}'.format(aov2[aov2['Source']==val]['DF'].round(3).values[0],aov2[aov2['Source']==val]['F'].round(3).values[0],aov2[aov2['Source']==val][p2_interest].round(3).values[0])
							except:	_tmp_df[loc2[val]] = 'F({},{}) = {},\ p={}'.format(aov2[aov2['Source']==val]['ddof1'].round(3).values[0],aov2[aov2['Source']==val]['ddof2'].round(3).values[0],aov2[aov2['Source']==val]['F'].round(3).values[0],aov2[aov2['Source']==val][p2_interest].round(3).values[0])


				# Adds _tmp_df for the processed variable to the output log
				output_log = pd.concat([output_log, _tmp_df])

		output_log.reset_index(inplace=True, drop=True)
		if save:
			if s8_9:	
				_path = os.path.join(os.getcwd(), os.path.join('Output logs', 'stats_summary_8-9 {}'.format(condition)+'.csv'))
				output_log.to_csv(_path)
			elif s1_8:	
				_path = os.path.join(os.getcwd(), os.path.join('Output logs', 'stats_summary_1-8 {}'.format(condition)+'.csv'))
				output_log.to_csv(_path)
			elif s1_9:	
				_path = os.path.join(os.getcwd(), os.path.join('Output logs', 'stats_summary_1-9 {}'.format(condition)+'.csv'))
				output_log.to_csv(_path)

