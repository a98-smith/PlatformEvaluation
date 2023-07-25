import os
import warnings
import analysis_utils as utils
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt


data_dir = 'C:\\Users\\adr-smith\\Documents\\GitHub\\PlatformEvaluation\\Output logs'
filenames = ['combined_df.csv', 'cl_df.csv', 'nl_df.csv', 'adl_df.csv']

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


output_log = pd.DataFrame(columns=['load', 'var', 'sig_high', 'sig_high_p',
						  'sig_low', 'sig_low_p', 'spher', 'spher_p', 'norm_res'], index=[0])

if __name__ == '__main__':

	for path in log_paths:  # Check and create directories to save resultant images to
		utils.check_or_create_folder(path)

	for file in filenames:  # Runs through each of the outputted results files from 0_extract_data.py
		filepath = os.path.join(data_dir, file)
		# Reads the .csv file into a pd.DataFrame object
		data = pd.read_csv(filepath, index_col=0)
  
		if s8_9:	data = data[data.Session in [8,9]] #pd.concat([utils.extract_questionnaire_rows(data, 'Session', '8'), utils.extract_questionnaire_rows(data, 'Session', '9')])
		elif s1_9:	data = data
		elif s1_8:	data = data[data.Session != 9]
   
		data['factor_comb'] = data['Feedback'].astype(
			str) + '-' + data['Session'].astype(str)  # Create factor comb for normailty checks

		if file == 'adl_df.csv':
			vars = data.columns[2:-2]
			within = 'Session'
		else:
			vars = data.columns[3:-2]
			within = ['Session', 'Loading']

		for var in vars:

			# Create a temp pd.DataFrame to store the analysis results of var
			_tmp_df = pd.DataFrame(index=[0], columns=[
								   'load', 'var', 'sig_high', 'sig_high_p', 'sig_low', 'sig_low_p', 'spher', 'spher_p', 'norm_res'])
			_tmp_df['load'] = file[:4].split('_', 1)[0].upper()
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
   
			# print(file, var, '\n', aov)

			# if file == 'adl_df.csv': print(var, '----------------------------------------\n', aov, '\n')
			# Create str variables to store results in
			high_str = 'None'
			high_p_str = 'None'
			low_str = 'None'
			low_p_str = 'None'

			p_interest = 'p-unc'

			if 'p-GG-corr' in aov.columns:
				p_interest = 'p-GG-corr'
				print(f'Greenhouse-Geisser p for {var}')

			# If any results from the ANOVA have a p-value below 0.05
			if (aov[p_interest] <= 0.05).any() or (aov['p-unc'] <= 0.05).any():

				# Extract these results
				high_significance = aov[(aov[p_interest] <= 0.05)]['Source']
				if p_interest != 'p-unc': high_significance = pd.concat( [high_significance, aov[(aov['p-unc'] <= 0.05) & (aov['Source'] != 'Session')]['Source']] )

				for val in high_significance.values:  # Report all high sig results and store them in _tmp_df

					# Plots all results that are significant (excluding significance across sessions)
					if val != 'Session':
						fig, ax = plt.subplots()
					if high_str != 'None':
						high_str = high_str + ', ' + str(val)
						high_p_str = high_p_str + ', ' + \
							str(aov[aov['Source'] == val]
								[p_interest].round(3).values[0])
					else:
						high_str = str(val)
						high_p_str = str(
							aov[aov['Source'] == val][p_interest].round(3).values[0])

			_tmp_df['sig_high'] = high_str
			_tmp_df['sig_high_p'] = high_p_str

			# If any results from the ANOVA have a p-value between 0.05 and 0.1
			if ((aov[p_interest] <= 0.1).any() and (aov[p_interest] > 0.05).any()) or ((aov['p-unc'] <= 0.1).any() and (aov['p-unc'] > 0.05).any()):

				# Extract these results
				low_significance = aov[(aov[p_interest] <= 0.1) & (aov[p_interest] > 0.05)]['Source']
				if p_interest != 'p-unc': low_significance = pd.concat( [low_significance, aov[(aov['p-unc'] > 0.05) & (aov['p-unc'] <= 0.1)& (aov['Source'] != 'Session')]['Source']] )
				# Plots all results that are significant (excluding significance across sessions)
				for val in low_significance.values:
					if val != 'Session':
						fig, ax = plt.subplots()
					if low_str != 'None':
						low_str = low_str + ', ' + str(val)
						low_p_str = low_p_str + ', ' + \
							str(aov[aov['Source'] == val]
								[p_interest].round(3).values[0])
					else:
						low_str = str(val)
						low_p_str = str(
							aov[aov['Source'] == val][p_interest].round(3).values[0])

			_tmp_df['sig_low'] = low_str
			_tmp_df['sig_low_p'] = low_p_str

			# Adds _tmp_df for the processed variable to the output log
			output_log = pd.concat([output_log, _tmp_df])

	output_log.reset_index(inplace=True, drop=True)
	if save:
		if s8_9:	output_log.to_csv(os.path.join(
			os.getcwd(), os.path.join('Output logs', 'stats_summary_8-9.csv')))
		elif s1_8:	output_log.to_csv(os.path.join(
			os.getcwd(), os.path.join('Output logs', 'stats_summary_1-8.csv')))
		elif s1_9:	output_log.to_csv(os.path.join(
			os.getcwd(), os.path.join('Output logs', 'stats_summary_1-9.csv')))
