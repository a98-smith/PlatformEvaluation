import analysis_utils as utils
import os
import pandas as pd
import matplotlib.pyplot as plt

# Directory definitions
data_dir = 'C:\\Users\\adr-smith\\Documents\\GitHub\\PlatformEvaluation\\Output logs'
filenames = ['combined_df.csv', 'cl_df.csv', 'nl_df.csv', 'adl_df.csv']
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

s1_8 = True
# s1_8 = False
# s1_9 = True
s1_9 = False
# s8_9 = True
s8_9 = False



def plot_performance( perf_df, load=None, show=False, save=False, plot_as_one=False, plot_many=False):
	
	_data = perf_df
	measures = ['P', 'G', 'T', 'F']


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
				utils.interaction_plot_w_errorbars( ax=ax, x=_data['Session'], trace=_data['Feedback'], response=_tmp_df[var], errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles, labels=labels, legend=True)
				ax.set_title(var+' '+load)
				
				if save: plt.savefig( os.path.join(fig_path, 'Performance metrics {}-{}'.format(load, var)) )
				if show:plt.show()

				plt.clf()
				plt.close()

def plot_tlx(tlx_df, load=None, show=False, save=False):

	_data = tlx_df
	# Create axes and figure objects
	fig, axlist = plt.subplots(2, 3, sharex=True, sharey=True)
	axes = list(axlist.flatten())  # Convert axlist from a np.array to a list

	fig.suptitle('Comparison of TLX results ({})'.format(load))
	fig.set_size_inches(12, 8)

	for axis in axes:
		var_loc = axes.index(axis)  # Create index for plotting varibale in df
		var = _data.iloc[:, var_loc]

		utils.interaction_plot_w_errorbars(ax=axis, x=_data['Session'], trace=_data['Feedback'], response=var,
										   errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles)
		axis.xaxis.set_ticks([1, 2, 3, 4, 5, 6, 7, 8], minor=True)
		axis.xaxis.grid(which='minor', ls=':')

	# Create some space below the plots by increasing the bottom-value
	fig.tight_layout(pad=1)
	fig.subplots_adjust(top=0.9, left=0.1, right=0.9, bottom=0.18)
	axlist.flatten()[-2].legend(loc='upper center', bbox_to_anchor=(0.5, -0.18),
								ncol=2, labels=labels)  # Place legend
	if save:
		plt.savefig(os.path.join(fig_path, 'Individual TLX {}'.format(load)))
	if show:
		plt.show()


	# Cleanup any figs that might still be active
	plt.clf()
	plt.close()

	fig, ax = plt.subplots()
	utils.interaction_plot_w_errorbars(ax=ax, x=_data['Session'], trace=_data['Feedback'], response=_data['TLX totals'],
									   errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles, legend=True)
	if save:
		plt.savefig(os.path.join(fig_path, 'Total TLX {}'.format(load)))
	if show:
		plt.show()


	# Cleanup any figs that might still be active
	plt.clf()
	plt.close()

def plot_qual(qual_df, load=None, show=False, save=False):

	_data = qual_df
	fig, axlist = plt.subplots(3, 3)  # Create axes and figure objects
	axes = list(axlist.flatten())  # Convert axlist from a np.array to a list

	fig.suptitle('Comparison of Qualitative results ({})'.format(load))
	fig.set_size_inches(12, 8)

	for axis in axes:
		var_loc = axes.index(axis)  # Create index for plotting varibale in df
		var = _data.iloc[:, var_loc]

		utils.interaction_plot_w_errorbars(ax=axis, x=_data['Session'], trace=_data['Feedback'], response=var,
										   errorbars=True, colors=colors, e_colors=e_colors, markers=markers, e_markers=e_markers, linestyles=linestyles)
		axis.xaxis.set_ticks([1, 2, 3, 4, 5, 6, 7, 8], minor=True)
		axis.xaxis.grid(which='minor', ls=':')

		if var.name != 'Q totals':
			axis.set_ylim([1, 8])
			axis.yaxis.set_ticks([1, 2, 3, 4, 5, 6, 7, 8], minor=True)
			axis.yaxis.grid(which='minor', ls=':')

	fig.tight_layout(pad=1)
	# Create some space below the plots by increasing the bottom-value
	fig.subplots_adjust(top=0.9, left=0.1, right=0.9, bottom=0.12)
	axlist.flatten()[-2].legend(loc='upper center', bbox_to_anchor=(0.5, -0.25),
								ncol=3, labels=['No Feedback', 'Feedback'])  # Place legend
	if save:
		plt.savefig(os.path.join(
			fig_path, 'Individual Qualitative {}'.format(load)))
	if show:
		plt.show()


	# Cleanup any figs that might still be active
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

if __name__ == '__main__':

	for file in filenames:
		filepath = os.path.join(data_dir, file)
		data = pd.read_csv(filepath, index_col=0)
		load = file[:4].split('_', 1)[0].upper()
  
		if s1_8: 
			data = data[data.Session != 9]
			fig_path = os.path.join(fig_dir, "Output_figs 1-8")
		elif s1_9:
			fig_path = os.path.join(fig_dir, "Output_figs 1-9")
		elif s8_9:
			data = data[data.Session in [8,9]]
			fig_path = os.path.join(fig_dir, "Output_figs 8-9")
   
		utils.check_or_create_folder(fig_path)
  
  

		if file != 'adl_df.csv':
			performance_results = data[[
								'P', 'P_l', 'P_h', 'G', 'G_l', 'G_h', 'T', 'T_l', 'T_h', 'F', 'F_l', 'F_h', 'Session', 'Feedback' ]]
			TLX_results = data[['Mental Demand', 'Physical Demand', 'Temporal Demand',
								'Performance', 'Effort', 'Frustration Level', 'TLX totals', 'Session', 'Feedback']]
			Q_results = data[['It is easy to understand.', 'It is distracting.', 'It is user-friendly.', 'Using it is effortless.',
								'Both occasional and Regular users would like it.', 'It is difficult to learn how to use.', 'It works the way I want it to work.', 'It is pleasant to use.', 'Q totals', 'Session', 'Feedback']]

			grasp_breakdown_results = data[['grasps', 'drops', 'crushes', 'Session', 'Feedback']]

			plot_performance( performance_results, load=load, show=False, save=True, plot_as_one=False, plot_many=True )
			plot_tlx( TLX_results, load=load, show=False, save=True )
			plot_qual( Q_results, load=load, show=False, save=True )
			plot_grasp_metric_breakdown( grasp_breakdown_results, load=load, show=False, save=True )
