import analysis_utils as utils
import os
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statistics import mean

# Directory definitions
data_dir = os.path.join( os.getcwd(), 'Output logs')
# filenames = ['combined_df.csv', 'cl_df.csv', 'nl_df.csv']#, 'adl_df.csv']
filenames = ['adl_df.csv']
fig_dir = os.path.join(os.getcwd(), "Output figs")
utils.check_or_create_folder(fig_dir)


# Plot style definitions
e_colors = ['chocolate', 'indigo']
colors = ['orange', 'rebeccapurple']
e_colors_l = ['goldenrod', 'darkturquoise']
colors_l = ['gold', 'teal']
e_colors_h = ['firebrick', 'midnightblue']
colors_h = ['coral', 'mediumblue']

e_markers = ['.', '.']
markers = ['.', '.']

linestyles = ['solid', 'solid']
linestyles_h = [ 'dashed', 'dashed' ]
linestyles_l = [ 'dotted', 'dotted' ]

labels = ['No Feedback (NTFB)', 'w/ Feedback (TFB)']
labels_l = ['NTFB (Light)', 'TFB (Light)']
labels_h = ['NTFB (Heavy)', 'TFB (Heavy)']

loads = {'COMB':'irrespective of loading condition',
			 'CL':'under high cognitive loading',
			 'NL':'under low cognitive loading'}

# s1_8 = True
s1_8 = False
# s1_9 = True
s1_9 = False
s8_9 = True
# s8_9 = False



def plot_performance( perf_df, load=None, show=False, save=False, plot_as_one=False, plot_many=False):
	
	_data = perf_df
	if s8_9: 
		mask = _data.applymap(type) != bool
		d = {True: 'TFB to NTFB', False: 'NTFB to TFB'}

		_data = _data.where(mask, _data.replace(d))

	measures = ['G', 'T']

	vars = {'P':'Session Performance', 'G':'Dexterity', 'T':'Speed', 
			'P_l':'Light Egg Session Performance', 'G_l':'Light Egg Dexterity', 'T_l':'Light Egg Speed', 
			'P_h':'Session Performance', 'G_h':'Heavy Egg Dexterity', 'T_h':'Heavy Egg Speed', }

	if plot_as_one == True:
	 
		fig, axlist = plt.subplots( 3, 2, sharex=True, sharey=True )
		axes = list(axlist.flatten())  # Convert axlist from a np.array to a list
	
		fig.suptitle('Comparison of measured metrics ({})'.format(load))
		axlist.flatten()[0].set_ylim([0,1])
		fig.set_size_inches(8, 8)
	 
		for var in measures: # Create plots for each metric (Combined, Grasp and Time)
		
			_idx = measures.index( var ) * 2
			_tmp_df = _data.iloc[:,_data.columns.str.contains(var)]
			utils.interaction_plot_w_errorbars( ax=axes[_idx], x=_data['Session'], trace=_data['Feedback'], response=_tmp_df[var], errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles, labels=labels)

			if _idx == 0: axes[_idx].set_title( 'Combined comparisons {}'.format( var ) )
			else: axes[_idx].set_title( '{}'.format( var ) )

			utils.interaction_plot_w_errorbars( ax=axes[_idx+1], x=_data['Session'], trace=_data['Feedback'], response=_tmp_df[var+'_l'], errorbars=True, colors=colors_l, e_colors=e_colors_l, markers=markers, e_markers=e_markers, linestyles=linestyles_l, labels=labels_l)
			utils.interaction_plot_w_errorbars( ax=axes[_idx+1], x=_data['Session'], trace=_data['Feedback'], response=_tmp_df[var+'_h'], errorbars=True, colors=colors_h, e_colors=e_colors_h, markers=markers, e_markers=e_markers, linestyles=linestyles_h, labels=labels_h)

			if _idx == 0: axes[_idx+1].set_title( 'Heavy vs Light egg {}'.format( var ) )
			else: axes[_idx+1].set_title( '{}'.format( var ) )
		
		fig.tight_layout(pad=1)
		fig.subplots_adjust(top=0.9, left=0.1, right=0.9, bottom=0.18)
		axes[-2].legend(loc='upper center', bbox_to_anchor=(0.5, -0.28),
								ncol=1, labels=labels)  # Place legend
		axes[-1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.28),
								ncol=2, labels=labels_l+labels_h)  # Place legend

		if save: plt.savefig( os.path.join(fig_path, 'All Performance metrics {}'.format(load)) )
		if show: plt.show()
  
	if plot_many == True:
		for var in measures:

			_tmp_df = _data.iloc[:,_data.columns.str.contains(var)]
			for var in _tmp_df.columns.values:
				fig, ax = plt.subplots()
				if not s8_9: utils.interaction_plot_w_errorbars( ax=ax, x=_data['Session'], trace=_data['Feedback'], response=_tmp_df[var], errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles, labels=labels, legend=True)
				if s8_9 and var != 'Feedback': 
					ticks = ['Session 8','Session 9']
					# _fb_data = [_data.loc[(_data['Session']==8) & (_data['Feedback']==True)][var].values.tolist(), _data.loc[(_data['Session']==9) & (_data['Feedback']==True)][var].values.tolist()]
					# _nfb_data = [ _data.loc[(_data['Session']==8) & (_data['Feedback']==False)][var].values.tolist(), _data.loc[(_data['Session']==9) & (_data['Feedback']==False)][var].values.tolist()]

					# utils.comparison_boxplot(_fb_data,_nfb_data, ticks=ticks, colours=['#D7191C','#2C7BB6'], labels=['TFB to NTFB','NTFB to TFB'])
					bxplt = sns.boxplot(data=_data, ax=ax, x='Session', y=var, hue='Feedback')#, hue_order=['TFB to NTFB','TFB to NTFB'] )
					
					utils.add_median_labels(bxplt)
					ax.set_ylim(0.2,1.05)
					ax.set_ylabel(vars[var])

     
				# plt.grid(axis='both')
				if not s8_9: 
					ax.set_title(vars[var]+' '+loads[load])
					ax.set_ylim(0.2,1)
				if s8_9: plt.suptitle(vars[var]+' '+loads[load])
				if save: plt.savefig( os.path.join(fig_path, 'Performance metrics {}-{}-{}'.format(load, var, case)) )
				if show:plt.show()

				plt.clf()
				plt.close()

def plot_tlx(tlx_df, load=None, show=False, save=False):

	_data = tlx_df
	if s8_9: 
		mask = _data.applymap(type) != bool
		d = {True: 'TFB to NTFB', False: 'NTFB to TFB'}

		_data = _data.where(mask, _data.replace(d))
	# Create axes and figure objects
	fig, axlist = plt.subplots(2, 3, sharex=True, sharey=True)
	axes = list(axlist.flatten())  # Convert axlist from a np.array to a list

	fig.suptitle('Comparison of TLX results ({})'.format(loads[load]))
	fig.set_size_inches(12, 8)

	for axis in axes:
		var_loc = axes.index(axis)  # Create index for plotting varibale in df
		var = _data.iloc[:, var_loc]

		if not s8_9: 
			utils.interaction_plot_w_errorbars(ax=axis, x=_data['Session'], trace=_data['Feedback'], response=var,
										   errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles)
			axis.xaxis.set_ticks([1, 2, 3, 4, 5, 6, 7, 8], minor=True)
			axis.xaxis.grid(which='minor', ls=':')
		else:  
			bxplt = sns.boxplot(data=_data, ax=axis, x='Session', y=var, hue='Feedback', hue_order=['TFB to NTFB','NTFB to TFB'], saturation=0.8 )
			axis.legend([],[],frameon=False)
			if s8_9: 
				try:
					utils.add_median_labels(bxplt)
				except: continue
	# Create some space below the plots by increasing the bottom-value
	fig.tight_layout(pad=1)
	fig.subplots_adjust(top=0.9, left=0.1, right=0.9, bottom=0.18)
	handles, _ = axis.get_legend_handles_labels()

	axlist.flatten()[-2].legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.18),
								ncol=2)#, labels=labels)  # Place legend
	if save:
		plt.savefig(os.path.join(fig_path, 'Individual TLX {}-{}'.format(load,case)))
	if show:
		plt.show()


	# Cleanup any figs that might still be active
	plt.clf()
	plt.close()

	for var in _data.columns:
		if (var != 'Session') and (var != 'Feedback'):
			fig, ax = plt.subplots()
			ax.set_title(var + ' ' + loads[load])
			
			
			if var != 'TLX totals': ax.set_ylim(0,20)
			if not s8_9: utils.interaction_plot_w_errorbars(ax=ax, x=_data['Session'], trace=_data['Feedback'], response=_data[var], errorbars=True,
										colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles, legend=True)
			else: 
					bxplt = sns.boxplot(data=_data, ax=ax, x='Session', y=var, hue='Feedback', hue_order=['TFB to NTFB','NTFB to TFB'], saturation=0.8 )
					try:
						utils.add_median_labels(bxplt)
					except: print(f'{var} failed to generate labels')
			if save: plt.savefig(os.path.join( fig_path, '{}_{}-{}.png'.format(var, load, case)))
			plt.clf()
			plt.close()

	# fig, ax = plt.subplots()
	# utils.interaction_plot_w_errorbars(ax=ax, x=_data['Session'], trace=_data['Feedback'], response=_data['TLX totals'],
	# 								   errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles, legend=True)
	# if save:
	# 	plt.savefig(os.path.join(fig_path, 'Total TLX {}'.format(load)))
	# if show:
	# 	plt.show()


	# Cleanup any figs that might still be active
	plt.clf()
	plt.close()

def plot_qual(qual_df, load=None, show=False, save=False):

	_data = qual_df
	if s8_9: 
		mask = _data.applymap(type) != bool
		d = {True: 'TFB to NTFB', False: 'NTFB to TFB'}

		_data = _data.where(mask, _data.replace(d))
  
	fig, axlist = plt.subplots(3, 3)  # Create axes and figure objects
	axes = list(axlist.flatten())  # Convert axlist from a np.array to a list

	fig.suptitle('Comparison of Qualitative results ({})'.format(load))
	fig.set_size_inches(12, 8)

	for axis in axes:
		var_loc = axes.index(axis)  # Create index for plotting varibale in df
		var = _data.iloc[:, var_loc]

		if not s8_9: 
			utils.interaction_plot_w_errorbars(ax=axis, x=_data['Session'], trace=_data['Feedback'], response=var,
										   errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles)
			axis.xaxis.set_ticks([1, 2, 3, 4, 5, 6, 7, 8], minor=True)
			axis.xaxis.grid(which='minor', ls=':')
		else:

			bxplt = sns.boxplot(data=_data, ax=axis, x='Session', y=var, hue='Feedback', hue_order=['TFB to NTFB','NTFB to TFB'], saturation=0.8 )
			try:	utils.add_median_labels(bxplt)
			except: continue

		if var.name != 'Q totals':
			axis.set_ylim([1, 7.1])
			axis.yaxis.set_ticks([1, 2, 3, 4, 5, 6, 7, 8], minor=True)
			axis.yaxis.grid(which='minor', ls=':')

	fig.tight_layout(pad=1)
	# Create some space below the plots by increasing the bottom-value
	fig.subplots_adjust(top=0.9, left=0.1, right=0.9, bottom=0.12)
	axlist.flatten()[-2].legend(loc='upper center', bbox_to_anchor=(0.5, -0.25),
								ncol=3, labels=[d[False],d[True]])  # Place legend
	if save:
		plt.savefig(os.path.join(
			fig_path, 'Individual Qualitative {}-{}'.format(load,case)))
	if show:
		plt.show()


	# Cleanup any figs that might still be active
	plt.clf()
	plt.close()
 
	for var in _data.columns:
		if (var != 'Session') and (var != 'Feedback'):
			fig, ax = plt.subplots()
			if not s8_9: utils.interaction_plot_w_errorbars(ax=ax, x=_data['Session'], trace=_data['Feedback'], response=_data[var], errorbars=True,
									   colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles, legend=True)
			else:  
				bxplt = sns.boxplot(data=_data, ax=ax, x='Session', y=var, hue='Feedback', hue_order=['TFB to NTFB','NTFB to TFB'], saturation=0.8 )
				utils.add_median_labels(bxplt)
			if var != 'Q totals' : 
				ax.set_ylim([0.9, 7.1])
				ax.set_title(var)
			else: 
				ax.set_title('Questionnaire totals ' + loads[load])
				ax.set_ylim(0,60)
			ax.set_ylabel('Score')
			if save: plt.savefig(os.path.join( fig_path, '{}_{}-{}.png'.format(var, load,case)))
			plt.clf()
			plt.close()

	fig, ax = plt.subplots()
	utils.interaction_plot_w_errorbars(ax=ax, x=_data['Session'], trace=_data['Feedback'], response=_data['Q totals'], errorbars=True,
									   colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles, legend=True)
	if save:
		plt.savefig(os.path.join(
			fig_path, 'Total Qualitative {}'.format(load)))
	if show:
		plt.show()


	# Cleanup any figs that might still be active
	plt.clf()
	plt.close()

def plot_grasp_metric_breakdown( gmb_df, load=None, show=False, save=False ):
	
	_data = gmb_df
	
	measures = ['grasps','drops','crushes']
	for var in measures:

		fig, ax = plt.subplots()
		utils.interaction_plot_w_errorbars( ax=ax, x=_data['Session'], trace=_data['Feedback'], response=_data[var], errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles, labels=labels, legend=True)
		ax.set_title('Mean number of {}{} for {} results'.format(var[0].upper(),var[1:], load))
		if save: plt.savefig( os.path.join(fig_path, 'Grasp breakdown metrics {}-{}'.format(load, var)) )
		if show: plt.show()
		plt.close()

def plot_adls(adl_df, load=None, show=False, save=False ):

	S1 = adl_df[adl_df.Session == 1]
	S4 = adl_df[adl_df.Session == 4]
	S8 = adl_df[adl_df.Session == 8]
	S9 = adl_df[adl_df.Session == 9]
 
	tasks = ['Cups', 'Pegs', 'Pens']

	if not s8_9:
		fig, axlist = plt.subplots(3,2,sharex=True, sharey=True)
		axes = list(axlist.flatten())
		


		for axis in axes:
			NFB_flag = False
			test_loc = axes.index(axis)
			if (test_loc % 2) == 0: test_loc = test_loc / 2
			else: 
				NFB_flag = True
				test_loc = (test_loc - 1) / 2
			print('adj_test loc =', test_loc)
			task = tasks[int(test_loc)]
			print(task, test_loc,'vs',axes.index(axis), NFB_flag)

			if NFB_flag:
				axis.boxplot([S1[S1.Feedback == False][task], S4[S4.Feedback == False][task], S8[S8.Feedback == False][task]])#, S9[S9.Feedback == False][task]])
				FB_fit = np.polyfit([1,2,3], [S1[S1.Feedback == False][task].mean(), S4[S4.Feedback == False][task].mean(), S8[S8.Feedback == False][task].mean()], 2)
				FB_fit_func = np.poly1d(FB_fit)
				if not s8_9: axis.plot(np.arange(1,3,0.1),FB_fit_func(np.arange(1,3,0.1)))
				axis.set_title(task + ' NTFB')
			else:
				axis.boxplot([S1[S1.Feedback == True][task], S4[S4.Feedback == True][task], S8[S8.Feedback == True][task]])#, S9[S9.Feedback == True][task]])
				FB_fit = np.polyfit([1,2,3], [S1[S1.Feedback == True][task].mean(), S4[S4.Feedback == True][task].mean(), S8[S8.Feedback == True][task].mean()], 2)
				FB_fit_func = np.poly1d(FB_fit)
				if not s8_9: axis.plot(np.arange(1,3,0.1),FB_fit_func(np.arange(1,3,0.1)))
				axis.set_title( task + ' TFB')
			
			axis.set_yticks( np.arange(0,12,1), minor=True )
			axis.set_ylabel('Impairment Ratio')

			if axes.index(axis) in [4,5]:	axis.set_xlabel('ADL assessment Session')
			fig.suptitle('Comparison of Impairment ratios between conditions')
			axis.grid()
			fig.set_size_inches(10,8)
   
	else: 
		
		fig, axlist = plt.subplots(3,1,sharex=True, sharey=True)
		axes = list(axlist.flatten())

  
		for task in tasks:
			idx = tasks.index(task)
			ax = axes[idx]
			_data = adl_df[adl_df.Session != 4]
			mask = _data.applymap(type) != bool
			d = {True: 'TFB to NTFB', False: 'NTFB to TFB'}
			_data = _data.where(mask, _data.replace(d))
   
			bxplt = sns.boxplot(_data, x='Session', y=task, hue='Feedback', ax=ax, hue_order=['TFB to NTFB','NTFB to TFB'])
			utils.add_median_labels(bxplt)
			ax.legend([],[],frameon=False)
			ax.set_title(task)
			ax.set_ylabel('Impairment Ratio')
			if idx != 2:
				ax.set_xlabel('')
			else: ax.set_xlabel(' ADL Assessment Session')
   
		fig.suptitle('Comparison of Impairment ratios when \n switching feedback conditions')
   
		handles, _ = ax.get_legend_handles_labels()

		axlist.flatten()[-1].legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, -0.5),
								ncol=2)
    
		fig.set_size_inches(5,8)
	
	# fig.legend()

	
	if save: plt.savefig( os.path.join( fig_path, "ADL metric scores" ) )
	if show: plt.show()



if __name__ == '__main__':

	for file in filenames:
		filepath = os.path.join(data_dir, file)
		data = pd.read_csv(filepath, index_col=0)
		load = file[:4].split('_', 1)[0].upper()
  
		if s1_8: 
			data = data[data.Session != 9]
			fig_path = os.path.join(fig_dir, "Output_figs 1-8")
			case =''
		elif s1_9:
			fig_path = os.path.join(fig_dir, "Output_figs 1-9")
			case = '1 to 9'
		elif s8_9:
			data = data[data['Session'].isin([1,8,9])]
			fig_path = os.path.join(fig_dir, "Output_figs 1-8-9")
			case = 'contra'
   
		utils.check_or_create_folder(fig_path)
  
  

		if file != 'adl_df.csv':
			# print('boop')
			performance_results = data[[
								'G', 'G_l', 'G_h', 'T', 'T_l', 'T_h', 'Session', 'Feedback' ]]
			TLX_results = data[['Mental Demand', 'Physical Demand', 'Temporal Demand',
								'Performance', 'Effort', 'Frustration Level', 'TLX totals', 'Session', 'Feedback']]
			Q_results = data[['It is easy to understand.', 'It is distracting.', 'It is user-friendly.', 'Using it is effortless.',
								'Both occasional and Regular users would like it.', 'It is difficult to learn how to use.', 'It works the way I want it to work.', 'It is pleasant to use.', 'Q totals', 'Session', 'Feedback']]
			# Q_results = data[['Q totals', 'Session', 'Feedback']]
			grasp_breakdown_results = data[['grasps', 'drops', 'crushes', 'Session', 'Feedback']]

			plot_performance( performance_results, load=load, show=False, save=True, plot_as_one=True, plot_many=True )
			plot_tlx( TLX_results, load=load, show=False, save=True )
			plot_qual( Q_results, load=load, show=False, save=True )
			# plot_grasp_metric_breakdown( grasp_breakdown_results, load=load, show=False, save=True )

		else: plot_adls(data, show=False, save=True)
