import os, pandas as pd, numpy as np, matplotlib.pyplot as plt, warnings
from scipy.stats import t
from statistics import mean

def extract_questionnaire_rows( df, column_name, search_string ):
	"""
	Extracts all rows from a DataFrame that contain a specified string in a particular column.

	Parameters:
	-----------
	df: pandas.DataFrame
		The DataFrame to search.
	column_name: str
		The name of the column to search for the string.
	search_string: str
		The string to search for.

	Returns:
	--------
	pandas.DataFrame
		A DataFrame containing all rows that match the search criteria.
	"""
	# Create a boolean mask by checking if the search_string is present in the specified column.
	mask = df[column_name].astype(str).str.contains( search_string, na=False )

	# Use the mask to select only the rows that match the search criteria.
	matching_rows = df[mask]

	return matching_rows


def check_or_create_folder(folder):
	if not os.path.isdir(folder):
		os.mkdir(folder)
  

def interaction_plot_w_errorbars( x, trace, response, func=np.mean, ax=None, plottype='b', xlabel=None, ylabel=None, colors=[], markers=[], linestyles=[], e_colors=[], e_markers=[], e_linestyles=[], legendloc='best', legendtitle=None, errorbars=False, errorbartyp='std', legend=False, labels=None, **kwargs ):
	
	data = pd.DataFrame(dict(x=x, trace=trace, response=response))
	plot_data = data.groupby(['trace', 'x']).aggregate(func).reset_index()

	if response.name == 'Q totals': ax.set_title('Overall Questionnaire Scores')
	elif response.name == 'TLX totals': ax.set_title('Overall TLX Scores')
	else: ax.set_title('{}'.format(response.name))
	ax.set_xlabel(x.name)
	ax.set_ylabel('Score')
	ax.grid(True)

	if errorbars:
		if errorbartyp == 'std':
			yerr = data.groupby(['trace', 'x']).aggregate( lambda xx: np.std(xx,ddof=1) ).reset_index()
		elif errorbartyp == 'ci95':
			yerr = data.groupby(['trace', 'x']).aggregate( t_ci ).reset_index()
		else:
			raise ValueError("Type of error bars %s not understood" % errorbartyp)

	n_trace = len(plot_data['trace'].unique())
	
	warnings.filterwarnings('ignore')
	if plottype == 'both' or plottype == 'b':
		for i, (values, group) in enumerate(plot_data.groupby(['trace'])):
      
			# trace label
			if labels == None: label = str(bool((group['trace'].values[0])))
			else: label = labels[i]

			if errorbars:
				ax.errorbar(group['x'], group['response'], 
						yerr=yerr.loc[ yerr['trace']==values ]['response'].values, 
						color=colors[i], ecolor=e_colors[i],
						marker=e_markers[i], label=label,
						linestyle=linestyles[i], elinewidth=.5,
						capsize=2, **kwargs)

	else: ax.plot(group['x'], group['response'], color=colors[i],
					marker=markers[i], label=label,
					linestyle=linestyles[i], **kwargs)

	warnings.filterwarnings('default')
	if legend: ax.legend( loc=legendloc, labels=['No Feedback', 'Feedback'] )
   
   
def t_ci( x, C=0.95 ):

    x = np.array( x )
    n = len( x )
    tstat = t.ppf( (1-C)/2, n )
    return np.std( x, ddof=1 ) * tstat / np.sqrt( n )

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)

def comparison_boxplot(data1, data2, data3=None, ticks=None, ylims=None, colours=None, labels=['data1','data2'], trendline=True ):
 
	# Create boxplots
	bpl = plt.boxplot( data1, positions=np.array(range(len(data1)))*2.0-0.4, sym='', widths=0.6, patch_artist=True )
	bpr = plt.boxplot( data2, positions=np.array(range(len(data2)))*2.0+0.4, sym='', widths=0.6, patch_artist=True )
 

	for bplot in (bpl, bpr):
		for patch, color in zip(bplot['boxes'], colours):
			patch.set_facecolor(color)
	
	if trendline:
		data1_trend = [mean(instance) for instance in data1]
		data2_trend = [mean(instance) for instance in data2]
		plt.plot( np.array(range(len(data1)))*2.0, data1_trend, c=colours[0], linestyle='dashed', label=labels[0]+' trendline' )
		plt.plot( np.array(range(len(data2)))*2.0, data2_trend, c=colours[1], linestyle='dashed', label=labels[1]+' trendline' )

	set_box_color(bpl, colours[0])
	set_box_color(bpr, colours[1])

	plt.plot([], c=colours[0], label=labels[0])
	plt.plot([], c=colours[1], label=labels[1])
	plt.legend()

	plt.xticks(range(0, len(ticks) * 2, 2), ticks)
	plt.xlim(-1, (len(ticks)*2) -1)
	if ylims == None: 
		ylims = [0,1]
	plt.ylim(ylims[0], ylims[1])
	# plt.tight_layout()