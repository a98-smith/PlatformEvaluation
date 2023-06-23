import pandas as pd, os, numpy as np
import analysis_utils as utils
import matplotlib.pyplot as plt

class Participant:
	"""_summary_
	"""
 
	### Attributes and variables
	# Public attributes and variables
 
	# Private attributes and variables
	_questionnaire_name = "PEQRs.csv"
	_debug = True
	_misgrasp_adj = 0.125
	_fail_adj = 0.5
	_timeout = 6000

	### Methods and functions
	
	# Private methods and functions
	def __init__( self, results_dir, participant_number ):
		"""Initialisation function for Participant class that obtains all relevant file directories
			and prepares the class for use.

		Args:
			results_dir (str): Filepath-like object to results folder
			participant_number (str): Unique participant identifier
		"""

		self.ID = participant_number
		self.questionnaire = os.path.join( results_dir, self._questionnaire_name)
		self.resultsFolder = os.path.join( results_dir, self.ID )
		self.session_result_dirs = next( os.walk( self.resultsFolder ) )[1]

		self._create_storage_variables()

		if self._debug: print( "\n-----\nParticipant object created for P{}".format(self.ID))

	def _create_storage_variables( self ):
		"""_summary_
		"""

		self.ADL_results = pd.DataFrame( index=[ "Cups", "Pegs", "Pens" ] )
		self.Grasp_results = pd.DataFrame()
		self.CL_grasp_metrics = pd.DataFrame()
		self.NL_grasp_metrics = pd.DataFrame()
		self.COMB_grasp_metrics = pd.DataFrame()
  

  # Public methods and functions
	def load_questionnaire_results( self ):
		"""Function that extracts all participant relevant data from the qualitative questionnaire results
		and stores them in publicly available varibales for further analysis.
		"""
  
		self.Qresults_full = utils.extract_questionnaire_rows( pd.read_csv( self.questionnaire ), "Participant ID", self.ID )
		self.Qresults_CL   = utils.extract_questionnaire_rows( self.Qresults_full, "Participant ID", "CL" )
		self.Qresults_NL   = utils.extract_questionnaire_rows( self.Qresults_full, "Participant ID", "NL" )
		self.Qresults_full.reset_index 
		self.Qresults_CL.reset_index 
		self.Qresults_NL.reset_index 
  
		if self._debug: print( "\tSuccessfully loaded questionnaire results" )
  
	def load_ADL_scorecards( self ):
		"""_summary_
		"""
		
		for session in self.session_result_dirs:
			session_dir = os.path.join( self.resultsFolder, session )
			
			for scorecard in os.listdir( session_dir ):
				if scorecard.startswith("ADLScorecard"):
					_path = os.path.join( session_dir, scorecard )
					_tmp_df = pd.read_csv( _path, index_col="Trial" )

					self.ADL_results = self.ADL_results.join( _tmp_df, rsuffix=session )

		if self._debug: print( "\tADL results successfully loaded." )

	def load_Grasp_scorecards( self ):
		"""_summary_
		"""
		
		for session in self.session_result_dirs:
			session_dir = os.path.join( self.resultsFolder, session )
			
			for scorecard in os.listdir( session_dir ):
				if scorecard.startswith("Grasp"):
					_path = os.path.join( session_dir, scorecard )
					_tmp_df = pd.read_csv( _path, index_col="Trial" )

					self.Grasp_results = self.Grasp_results.join( _tmp_df, how='outer', rsuffix=session )

		if self._debug:	print( "\tGrasp results successfully loaded." )

	def process_ADL_results( self ):
		manual = self.ADL_results[[ x for x in self.ADL_results.columns if "Manual" in x ]].rename( columns={"Manual":"S1", "Manual4":"S4", "Manual8":"S8"} )
		platform = self.ADL_results[[ x for x in self.ADL_results.columns if "Platform" in x ]].rename( columns={"Platform":"S1", "Platform4":"S4", "Platform8":"S8"} )
		if self.ID.endswith("OPP"):
			self.ADL_ratios = pd.DataFrame( index=[ "Cups", "Pegs", "Pens" ], columns=[ "S1" ] )
		else: 
			self.ADL_ratios = pd.DataFrame( index=[ "Cups", "Pegs", "Pens" ], columns=[ "S1", "S4", "S8" ] )
			
   
		for column in self.ADL_ratios.columns:
			for task in self.ADL_ratios.index:
				try:
					self.ADL_ratios[column][task] = platform[column][task]/manual[column][task]
				except:
					if self._debug: print("\t\tError: Data missing for ADL session {}".format(column))
	
		if self._debug: print("\tADL metrics processed successfully.")

	def process_grasp_results( self ):
		"""_summary_
		"""
		self.CL_Grasp_results = self.Grasp_results.loc[ :, self.Grasp_results.columns.str.startswith( 'CL' ) ]
		self.CL_Grasp_results.columns = self.CL_Grasp_results.columns.str[3:]
		self.NL_Grasp_results = self.Grasp_results.loc[ :, self.Grasp_results.columns.str.startswith( 'NL' ) ]
		self.NL_Grasp_results.columns = self.NL_Grasp_results.columns.str[3:]
  
		self.COMB_Grasp_results = pd.concat( [ self.NL_Grasp_results[self.NL_Grasp_results.columns.drop(list(self.NL_Grasp_results.filter(regex='Egg')))], self.CL_Grasp_results[self.CL_Grasp_results.columns.drop(list(self.CL_Grasp_results.filter(regex='Egg')))] ] )

		for session in range( int( len( self.COMB_Grasp_results.columns ) / 3 ) ): # Combined performance averages across trial numbers and sessions (averaged between CL and NL cases, irrespective of eggs)
			_mis_col = session*3
			_tmp_df =  1 - ( self.COMB_Grasp_results.iloc[ :, _mis_col ] * self._misgrasp_adj + ( ( self.COMB_Grasp_results.iloc[ :, _mis_col + 1 ] + self.COMB_Grasp_results.iloc[:, _mis_col + 2 ] ) * self._fail_adj ) ) 
			_col_title = "Performance"+str(session+1)
			_tmp_df = _tmp_df.rename(_col_title)
			_tmp_df = pd.DataFrame(_tmp_df)
			_tmp_df[_tmp_df < 0] = 0 			# Turns any negative values into 0, should I though?
   
			total_mean_calc = pd.DataFrame( _tmp_df[_col_title].mean(axis=0, skipna=True, numeric_only=True), index=["Mean"], columns=[_col_title] )
			_tmp_df = pd.concat( [ _tmp_df, total_mean_calc ], axis=0 )
			self.COMB_grasp_metrics = pd.concat( [ self.COMB_grasp_metrics, _tmp_df ], axis=1 )
	
  
		for session in range( int( len( self.CL_Grasp_results.columns ) / 4 ) ): # Extracts and processes grasp results for Cognitive loading condition
			
			_egg_col = session*4
			_tmp_df =  1 - ( self.CL_Grasp_results.iloc[ :, _egg_col + 1 ] * self._misgrasp_adj + ( ( self.CL_Grasp_results.iloc[ :, _egg_col+2 ] + self.CL_Grasp_results.iloc[:, _egg_col+3 ] ) * self._fail_adj ) ) 
			_col_title = "Performance"+str(session+1)
			_tmp_df = _tmp_df.rename(_col_title)
			_tmp_df = pd.DataFrame(_tmp_df)
			_tmp_df[_tmp_df < 0] = 0 			# Turns any negative values into 0, should I though?
			_tmp_df = pd.concat( [ self.CL_Grasp_results.iloc[ :, _egg_col ], _tmp_df ] , axis=1 )
   
			total_mean_calc = pd.DataFrame( _tmp_df[_col_title].mean(axis=0, skipna=True, numeric_only=True), index=["Mean"], columns=[_col_title] )
			light_mean_calc = pd.DataFrame( _tmp_df[_tmp_df.iloc[:,0]=="L"][_col_title].mean(), index=["Mean_L"], columns=[_col_title] )
			heavy_mean_calc = pd.DataFrame( _tmp_df[_tmp_df.iloc[:,0]=="H"][_col_title].mean(), index=["Mean_H"], columns=[_col_title] )
			# total_num_crush = pd.DataFrame( )
			# light_num_crush = 
			_tmp_df = pd.concat( [ _tmp_df, total_mean_calc, light_mean_calc, heavy_mean_calc ], axis=0 )
			self.CL_grasp_metrics = pd.concat( [ self.CL_grasp_metrics, _tmp_df ], axis=1 )

		for session in range( int( len( self.NL_Grasp_results.columns ) / 4 ) ): # Extracts and processes grasp results for No loading condition
			
			_egg_col = session*4
			_tmp_df =  1 - ( self.NL_Grasp_results.iloc[ :, _egg_col + 1 ] * self._misgrasp_adj + ( ( self.NL_Grasp_results.iloc[ :, _egg_col+2 ] + self.NL_Grasp_results.iloc[:, _egg_col+3 ] ) * self._fail_adj ) ) 
			_col_title = "Performance"+str(session+1)
			_tmp_df = _tmp_df.rename(_col_title)
			_tmp_df = pd.DataFrame(_tmp_df)
			_tmp_df[_tmp_df < 0] = 0 			# Turns any negative values into 0, should I though?
			_tmp_df = pd.concat( [ self.NL_Grasp_results.iloc[ :, _egg_col ], _tmp_df ] , axis=1 )
   
			total_mean_calc = pd.DataFrame( _tmp_df[_col_title].mean(axis=0, skipna=True, numeric_only=True), index=["Mean"], columns=[_col_title] )
			light_mean_calc = pd.DataFrame( _tmp_df[_tmp_df.iloc[:,0]=="L"][_col_title].mean(), index=["Mean_L"], columns=[_col_title] )
			heavy_mean_calc = pd.DataFrame( _tmp_df[_tmp_df.iloc[:,0]=="H"][_col_title].mean(), index=["Mean_H"], columns=[_col_title] )
			_tmp_df = pd.concat( [ _tmp_df, total_mean_calc, light_mean_calc, heavy_mean_calc ], axis=0 )
			self.NL_grasp_metrics = pd.concat( [ self.NL_grasp_metrics, _tmp_df ], axis=1 )

		if self._debug: print( "\tGrasp metrics analysed successfully" )
  
	def load_trial_times( self ):
		
		cols = ['S1','S2','S3','S4','S5','S6','S7','S8']
		self.CL_contact_forces = pd.DataFrame(index=[1,2,3,4,5,6,7,8,9,10], columns=['S1E','S1','S2E','S2','S3E','S3','S4E','S4','S5E','S5','S6E','S6','S7E','S7','S8E','S8'])
		self.NL_contact_forces = pd.DataFrame(index=[1,2,3,4,5,6,7,8,9,10], columns=['S1E','S1','S2E','S2','S3E','S3','S4E','S4','S5E','S5','S6E','S6','S7E','S7','S8E','S8'])
		self.CL_contact_times = pd.DataFrame(index=[1,2,3,4,5,6,7,8,9,10], columns=['S1E','S1','S2E','S2','S3E','S3','S4E','S4','S5E','S5','S6E','S6','S7E','S7','S8E','S8'])
		self.NL_contact_times = pd.DataFrame(index=[1,2,3,4,5,6,7,8,9,10], columns=['S1E','S1','S2E','S2','S3E','S3','S4E','S4','S5E','S5','S6E','S6','S7E','S7','S8E','S8'])
		self.CL_times_avg= pd.DataFrame( index=['L','H','COMB'], columns=cols)
		self.NL_times_avg= pd.DataFrame( index=['L','H','COMB'], columns=cols)
		

		for session in self.session_result_dirs:
			session_dir = os.path.join( self.resultsFolder, session )  # Directory path for session (1-8)
			self.CL_contact_forces.loc['avg', 'S'+str(session)] = 0
			self.NL_contact_forces.loc['avg', 'S'+str(session)] = 0
			for condition in os.listdir(session_dir):

				if os.path.isdir( os.path.join( session_dir, condition ) ):
        
					session_loading_dir = os.path.join( session_dir, condition ) # Directory path for session (1-8) condition (CL/NL)

					for trial in os.listdir( session_loading_dir ):
							
						if not trial.startswith('Miss'):
							
							i = int( trial.split( '-', 1 )[0] ) # Indexing value to make sure trial results end up in the correct location in the DataFrame
							egg = trial.split( '-', 1 )[1][:1] # Trial Egg value
							trial_file = os.path.join( session_loading_dir, trial ) # Filepath for session (1-8) condition (CL/NL) trial (1-10) pressure information
       
							try:
								_tmp_df = pd.read_csv( trial_file )
								if condition == 'CL':

									self.CL_contact_forces.loc[i, 'S'+str(session)] = _tmp_df.loc[:,_tmp_df.any()].mean().values
									self.CL_contact_forces.loc[i, 'S'+str(session)+'E'] = egg

									self.CL_contact_times.loc[i, 'S'+str(session)] = len(self.CL_contact_forces.loc[i, 'S'+str(session)])
									self.CL_contact_times.loc[i, 'S'+str(session)+'E'] = egg
          
								elif condition == 'NL':
            
									self.NL_contact_forces.loc[i, 'S'+str(session)] = _tmp_df.loc[:,_tmp_df.any()].mean().values
									self.NL_contact_forces.loc[i, 'S'+str(session)+'E'] = egg

									self.NL_contact_times.loc[i, 'S'+str(session)] = len(self.NL_contact_forces.loc[i, 'S'+str(session)])
									self.NL_contact_times.loc[i, 'S'+str(session)+'E'] = egg
							
							except:
								print('\t\tException raised: Empty grasp file preloop - P{}-S{}-{}-{}'.format(self.ID, session, condition, trial))
		
		self.CL_contact_times = self.CL_contact_times.apply( lambda x: [np.NaN if str(y).isnumeric() and y > self._timeout else y for y in x ] ).replace( 0, np.NaN )
		self.NL_contact_times = self.NL_contact_times.apply( lambda x: [np.NaN if str(y).isnumeric() and y > self._timeout else y for y in x ] ).replace( 0, np.NaN )


  
		for col in cols:
			egg_iloc = self.CL_contact_times.columns.get_loc(col) - 1
			self.CL_times_avg.loc['COMB', col] = self.CL_contact_times[col].mean( axis=0)#, numeric_only=True )
			self.CL_times_avg.loc['L', col] = self.CL_contact_times[self.CL_contact_times.iloc[:,egg_iloc]=='L'][col].mean( axis=0)#, numeric_only=True )
			self.CL_times_avg.loc['H', col] = self.CL_contact_times[self.CL_contact_times.iloc[:,egg_iloc]=='H'][col].mean( axis=0)#, numeric_only=True )

			self.NL_times_avg.loc['COMB', col] = self.NL_contact_times[col].mean( axis=0)#, numeric_only=True )
			self.NL_times_avg.loc['L', col] = self.NL_contact_times[self.NL_contact_times.iloc[:,egg_iloc]=='L'][col].mean( axis=0)#, numeric_only=True )
			self.NL_times_avg.loc['H', col] = self.NL_contact_times[self.NL_contact_times.iloc[:,egg_iloc]=='H'][col].mean( axis=0)#, numeric_only=True )

	def plot_performance( self ):
		""""""
		if not self.ID.endswith('OPP'):
			fig, ax = plt.subplots()
			ax.plot( ( range(1,len(self.NL_grasp_metrics.loc["Mean", self.NL_grasp_metrics.columns.str.contains("Performance")].values)+1) ), self.NL_grasp_metrics.loc["Mean", self.NL_grasp_metrics.columns.str.contains("Performance")].values)
			ax.plot( ( range(1,len(self.CL_grasp_metrics.loc["Mean", self.CL_grasp_metrics.columns.str.contains("Performance")].values)+1) ), self.CL_grasp_metrics.loc["Mean", self.CL_grasp_metrics.columns.str.contains("Performance")].values )
			ax.set(xlim=(1, 8), xticks=np.arange(1, 8), ylim=(0, 1))
			plt.show()

	def combine_performance_and_time( self ):
		
		if not self.ID.endswith('OPP'):
			col_rename = {"Performance1":"S1",  "Performance2":"S2",   "Performance3":"S3",   "Performance4":"S4",   "Performance5":"S5",   "Performance6":"S6",   "Performance7":"S7",   "Performance8":"S8"}

			self.CL_timing_metrics = self.CL_contact_times[self.CL_contact_times.columns.drop(list(self.CL_contact_times.filter(regex='E')))]
			self.CL_timing_metrics = 1 - self.CL_timing_metrics.apply( lambda x: [(y-1)/(1500-100)  for y in x ] )
			self.CL_timing_metrics = self.CL_timing_metrics.apply( lambda x: [0 if y < 0 else y for y in x])

	
			self.NL_timing_metrics = 1 - self.NL_contact_times[self.NL_contact_times.columns.drop(list(self.NL_contact_times.filter(regex='E')))].div(1000)
			self.NL_timing_metrics = self.NL_timing_metrics.apply( lambda x: [(y-1)/(1500-100) for y in x ] )
			self.NL_timing_metrics = self.NL_timing_metrics.apply( lambda x: [0 if y < 0 else y for y in x] )

			self.CL_combined_performance = self.CL_timing_metrics * self.CL_grasp_metrics[self.CL_grasp_metrics.columns.drop(list(self.CL_grasp_metrics.filter(regex='Egg')))].rename(columns=col_rename)
				
			self.CL_combined_performance.drop([ 'Mean_H', 'Mean_L' ], inplace=True )
			self.CL_combined_performance.loc['Mean'] = self.CL_combined_performance.mean()
			self.CL_combined_performance.loc['STD'] = self.CL_combined_performance.iloc[0:10,:].std()
			print(self.CL_combined_performance.iloc[0:10,:])
			print(self.CL_combined_performance)



### NON CLASS FUNCTIONS & VARIBALES

condition_mask = [ '021', '023', '026', '030', '031', '032' ]

def calculate_all_performance_means( participant_list ):
		
	NL_means 		=	pd.DataFrame()
	NL_means_L  	=	pd.DataFrame()
	NL_means_H 		=	pd.DataFrame()
	CL_means 		=	pd.DataFrame()
	CL_means_L		=	pd.DataFrame()
	CL_means_H		=	pd.DataFrame()
	FB_COMB_means	=	pd.DataFrame()
	FB_NL_means		=	pd.DataFrame()
	FB_NL_means_L	=	pd.DataFrame()
	FB_NL_means_H	=	pd.DataFrame()
	FB_CL_means 	=	pd.DataFrame()
	FB_CL_means_L	=	pd.DataFrame()
	FB_CL_means_H	=	pd.DataFrame()
	NFB_COMB_means	=	pd.DataFrame()
	NFB_NL_means	=	pd.DataFrame()
	NFB_NL_means_L	=	pd.DataFrame()
	NFB_NL_means_H	=	pd.DataFrame()
	NFB_CL_means	=	pd.DataFrame()
	NFB_CL_means_L	=	pd.DataFrame()
	NFB_CL_means_H	=	pd.DataFrame()
 
	for participant in participant_list:
		if not participant.ID.endswith("OPP"):
			try:
				NL_means = pd.concat( [NL_means, participant.NL_grasp_metrics.loc["Mean", participant.NL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean':participant.ID})
				CL_means = pd.concat( [CL_means, participant.CL_grasp_metrics.loc["Mean", participant.CL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean':participant.ID})
				NL_means_L = pd.concat( [NL_means_L, participant.NL_grasp_metrics.loc["Mean_L", participant.NL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_L':participant.ID})
				CL_means_L = pd.concat( [CL_means_L, participant.CL_grasp_metrics.loc["Mean_L", participant.CL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_L':participant.ID})
				NL_means_H = pd.concat( [NL_means_H, participant.NL_grasp_metrics.loc["Mean_H", participant.NL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_H':participant.ID})
				CL_means_H = pd.concat( [CL_means_H, participant.CL_grasp_metrics.loc["Mean_H", participant.CL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_H':participant.ID})
			except:
				""""""
				print("Unable to plot, data missing.")
			
			if participant.ID in condition_mask:
				FB_COMB_means = pd.concat( [FB_COMB_means, participant.COMB_grasp_metrics.loc["Mean", participant.COMB_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean':participant.ID})
				FB_NL_means = pd.concat( [FB_NL_means, participant.NL_grasp_metrics.loc["Mean", participant.NL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean':participant.ID})
				FB_CL_means = pd.concat( [FB_CL_means, participant.CL_grasp_metrics.loc["Mean", participant.CL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean':participant.ID})
				FB_NL_means_L = pd.concat( [FB_NL_means_L, participant.NL_grasp_metrics.loc["Mean_L", participant.NL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_L':participant.ID})
				FB_CL_means_L = pd.concat( [FB_CL_means_L, participant.CL_grasp_metrics.loc["Mean_L", participant.CL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_L':participant.ID})
				FB_NL_means_H = pd.concat( [FB_NL_means_H, participant.NL_grasp_metrics.loc["Mean_H", participant.NL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_H':participant.ID})
				FB_CL_means_H = pd.concat( [FB_CL_means_H, participant.CL_grasp_metrics.loc["Mean_H", participant.CL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_H':participant.ID})
	
 
			else:
				NFB_COMB_means = pd.concat( [NFB_COMB_means, participant.COMB_grasp_metrics.loc["Mean", participant.COMB_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean':participant.ID})
				NFB_NL_means = pd.concat( [NFB_NL_means, participant.NL_grasp_metrics.loc["Mean", participant.NL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean':participant.ID})
				NFB_CL_means = pd.concat( [NFB_CL_means, participant.CL_grasp_metrics.loc["Mean", participant.CL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean':participant.ID})
				NFB_NL_means_L = pd.concat( [NFB_NL_means_L, participant.NL_grasp_metrics.loc["Mean_L", participant.NL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_L':participant.ID})
				NFB_CL_means_L = pd.concat( [NFB_CL_means_L, participant.CL_grasp_metrics.loc["Mean_L", participant.CL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_L':participant.ID})
				NFB_NL_means_H = pd.concat( [NFB_NL_means_H, participant.NL_grasp_metrics.loc["Mean_H", participant.NL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_H':participant.ID})
				NFB_CL_means_H = pd.concat( [NFB_CL_means_H, participant.CL_grasp_metrics.loc["Mean_H", participant.CL_grasp_metrics.columns.str.contains("Performance")]], axis=1, join='outer').rename(columns={'Mean_H':participant.ID})
	
	NL_means["Mean"] = NL_means.mean(axis=1)
	CL_means["Mean"] = CL_means.mean(axis=1)
	NL_means_L["Mean"] = NL_means_L.mean(axis=1)
	CL_means_L["Mean"] = CL_means_L.mean(axis=1)
	NL_means_H["Mean"] = NL_means_H.mean(axis=1)
	CL_means_H["Mean"] = CL_means_H.mean(axis=1)
	FB_COMB_means["Mean"] = FB_COMB_means.mean(axis=1)
	FB_NL_means["Mean"] = FB_NL_means.mean(axis=1)
	FB_CL_means["Mean"] = FB_CL_means.mean(axis=1)
	FB_NL_means_L["Mean"] = FB_NL_means_L.mean(axis=1)
	FB_CL_means_L["Mean"] = FB_CL_means_L.mean(axis=1)
	FB_NL_means_H["Mean"] = FB_NL_means_H.mean(axis=1)
	FB_CL_means_H["Mean"] = FB_CL_means_H.mean(axis=1)
	NFB_COMB_means["Mean"] = NFB_COMB_means.mean(axis=1)
	NFB_NL_means["Mean"] = NFB_NL_means.mean(axis=1)
	NFB_CL_means["Mean"] = NFB_CL_means.mean(axis=1)
	NFB_NL_means_L["Mean"] = NFB_NL_means_L.mean(axis=1)
	NFB_CL_means_L["Mean"] = NFB_CL_means_L.mean(axis=1)
	NFB_NL_means_H["Mean"] = NFB_NL_means_H.mean(axis=1)
	NFB_CL_means_H["Mean"] = NFB_CL_means_H.mean(axis=1)
    
	return NL_means, NL_means_L, NL_means_H, CL_means, CL_means_L, CL_means_H, FB_NL_means, FB_NL_means_L, FB_NL_means_H, FB_CL_means, FB_CL_means_L, FB_CL_means_H, NFB_NL_means, NFB_NL_means_L, NFB_NL_means_H, NFB_CL_means, NFB_CL_means_L, NFB_CL_means_H, FB_COMB_means, NFB_COMB_means

def calculate_all_qualitative_means( participant_list ):
	
	Participants = participant_list
	Qresults_CL_FB = pd.DataFrame()
	Qresults_CL_FB_avg = pd.DataFrame()
	Qresults_NL_FB = pd.DataFrame()
	Qresults_NL_FB_avg = pd.DataFrame()
	Qresults_CL_NFB = pd.DataFrame()
	Qresults_CL_NFB_avg = pd.DataFrame()
	Qresults_NL_NFB = pd.DataFrame()
	Qresults_NL_NFB_avg = pd.DataFrame()
	
	for participant in Participants:
		if (not participant.ID.endswith('OPP')) and (participant.ID in condition_mask):

			Qresults_CL_FB = pd.concat( [ Qresults_CL_FB, participant.Qresults_CL ], ignore_index = True, axis=0)
			Qresults_NL_FB = pd.concat( [ Qresults_NL_FB, participant.Qresults_NL ], ignore_index = True, axis=0)
			
		elif (not participant.ID.endswith('OPP')) and (not participant.ID in condition_mask):

			Qresults_CL_NFB = pd.concat( [ Qresults_CL_NFB, participant.Qresults_CL ], ignore_index = True, axis=0)
			Qresults_NL_NFB = pd.concat( [ Qresults_NL_NFB, participant.Qresults_NL ], ignore_index = True, axis=0)	
   		
	Qresults_CL_FB = Qresults_CL_FB[~Qresults_CL_FB['Participant ID'].str.contains("-S9")].drop(['Timestamp', 'ADLS?'], axis=1)
	Qresults_CL_FB.reset_index
	
	Qresults_NL_FB = Qresults_NL_FB[~Qresults_NL_FB['Participant ID'].str.contains("-S9")].drop(['Timestamp', 'ADLS?'], axis=1)
	Qresults_NL_FB.reset_index
	
	Qresults_CL_NFB = Qresults_CL_NFB[~Qresults_CL_NFB['Participant ID'].str.contains("-S9")].drop(['Timestamp', 'ADLS?'], axis=1)
	Qresults_CL_NFB.reset_index
 
	Qresults_NL_NFB = Qresults_NL_NFB[~Qresults_NL_NFB['Participant ID'].str.contains("-S9")].drop(['Timestamp', 'ADLS?'], axis=1)
	Qresults_NL_NFB.reset_index

	for session in range(1,9):
     
		_tmp_df_CL = Qresults_CL_FB[Qresults_CL_FB['Session Number']==session]
		_tmp_df_CL = _tmp_df_CL.drop(['Participant ID'], axis=1 )
		_tmp_df_CL_avg = pd.DataFrame(_tmp_df_CL.mean(axis=0)).T
		Qresults_CL_FB_avg = pd.concat([Qresults_CL_FB_avg, _tmp_df_CL_avg], join='outer', axis=0)

		_tmp_df_NL = Qresults_NL_FB[Qresults_NL_FB['Session Number']==session]
		_tmp_df_NL = _tmp_df_NL.drop(['Participant ID'], axis=1 )
		_tmp_df_NL_avg = pd.DataFrame(_tmp_df_NL.mean(axis=0)).T
		Qresults_NL_FB_avg = pd.concat([Qresults_NL_FB_avg, _tmp_df_NL_avg], join='outer', axis=0)

		_tmp_df_CL = Qresults_CL_NFB[Qresults_CL_NFB['Session Number']==session]
		_tmp_df_CL = _tmp_df_CL.drop(['Participant ID'], axis=1 )
		_tmp_df_CL_avg = pd.DataFrame(_tmp_df_CL.mean(axis=0)).T
		Qresults_CL_NFB_avg = pd.concat([Qresults_CL_NFB_avg, _tmp_df_CL_avg], join='outer', axis=0)

		_tmp_df_NL = Qresults_NL_NFB[Qresults_NL_NFB['Session Number']==session]
		_tmp_df_NL = _tmp_df_NL.drop(['Participant ID'], axis=1 )
		_tmp_df_NL_avg = pd.DataFrame(_tmp_df_NL.mean(axis=0)).T
		Qresults_NL_NFB_avg = pd.concat([Qresults_NL_NFB_avg, _tmp_df_NL_avg], join='outer', axis=0)

	Qresults_NL_FB_avg.set_index('Session Number', inplace=True )
	Qresults_CL_FB_avg.set_index('Session Number', inplace=True )
	Qresults_NL_NFB_avg.set_index('Session Number', inplace=True )
	Qresults_CL_NFB_avg.set_index('Session Number', inplace=True )
 
	return 	Qresults_CL_FB,	Qresults_CL_FB_avg, Qresults_NL_FB, Qresults_NL_FB_avg,	Qresults_CL_NFB, Qresults_CL_NFB_avg, Qresults_NL_NFB, Qresults_NL_NFB_avg

def plot_overall_performance_means( show = False, save = False ):
	plt.errorbar( range( len( FB_COMB_means.index ) ), FB_COMB_means["Mean"], yerr= FB_COMB_means.std( axis=1 ).values, fmt='slateblue', label='FB performance averages', ecolor='midnightblue', elinewidth=.5, capsize=3 )
	# plt.errorbar( range( len( FB_NL_means.index ) ), FB_NL_means["Mean"], yerr= FB_NL_means.std( axis=1 ).values, fmt='slateblue', label='FB No loading performance averages', ecolor='midnightblue', elinewidth=.5, capsize=3 )
	# plt.errorbar( range( len( FB_CL_means.index ) ), FB_CL_means["Mean"], yerr= FB_CL_means.std( axis=1 ).values, fmt='violet', linestyle='--', linewidth=.5, label='FB No loading performance averages', ecolor='purple', elinewidth=.25, capsize=1 )
	# plt.errorbar( range( len( FB_COMB_means.index ) ), ( FB_COMB_means["Mean"] ), yerr= FB_COMB_means.std( axis=1 ).values, fmt='green', label='FB COMB performance averages', ecolor='midnightblue', elinewidth=.5, capsize=3 )
	plt.errorbar( range( len( NFB_COMB_means.index ) ), NFB_COMB_means["Mean"], yerr= NFB_COMB_means.std( axis=1 ).values, fmt='orange', label='NFB performance averages',  ecolor='darkorange', elinewidth=.5, capsize=3 )
	# plt.errorbar( range( len( NFB_NL_means.index ) ), NFB_NL_means["Mean"], yerr= NFB_NL_means.std( axis=1 ).values, fmt='orange', label='NFB No loading performance averages',  ecolor='darkorange', elinewidth=.5, capsize=3 )
	# plt.errorbar( range( len( NFB_CL_means.index ) ), NFB_CL_means["Mean"], yerr= NFB_CL_means.std( axis=1 ).values, fmt='orangered', linestyle='--', linewidth=.5, label='NFB No loading performance averages',  ecolor='darkred', elinewidth=.25, capsize=1 )
	# plt.errorbar( range( len( NFB_COMB_means.index ) ), ( NFB_COMB_means["Mean"] ), yerr= NFB_COMB_means.std( axis=1 ).values, fmt='pink', label='NFB COMB performance averages',  ecolor='darkorange', elinewidth=.5, capsize=3 )
	plt.xlim(0, 8)
	plt.ylim(0.45, 1)
	plt.legend(loc='lower right')
	plt.title('Performance averages across sessions')
	if save: plt.savefig( os.path.join( os.getcwd(), os.path.join("Output_figs", "Performance" ) ) )
	if show: plt.show()
 

	plt.clf()
	plt.close()

def plot_TLX_scores( condition, show = False, save = False ):
	fig, ( ( ax1, ax2, ax3 ), ( ax4, ax5, ax6 ) ) = plt.subplots( 2, 3 )
 
	if condition == 'CL':
		fig.suptitle('Comparison of TLX scores under cognitive load')
		TLX_results_FB = Qresults_CL_FB_avg
		TLX_results_NFB = Qresults_CL_NFB_avg
		app = 'under cognitive loading'
  
	elif condition == 'NL':
		fig.suptitle('Comparison of TLX scores without cognitive load')
		TLX_results_FB = Qresults_NL_FB_avg
		TLX_results_NFB = Qresults_NL_NFB_avg
		app = 'without cognitive loading'
  
	else:
		print('No valid condition set, defaulting to without loading.')
		fig.suptitle('Comparison of TLX scores without cognitive load')
		TLX_results_FB = Qresults_NL_FB_avg
		TLX_results_NFB = Qresults_NL_NFB_avg
		app = 'without cognitive loading'
 
	axes = [ ax1, ax2, ax3, ax4, ax5, ax6 ]

	_TLX_FB = TLX_results_FB[['Mental Demand' , 'Physical Demand', 'Temporal Demand', 'Performance', 'Effort', 'Frustration Level']]
	_TLX_FB['Totals'] = _TLX_FB.sum(axis=1)
	_TLX_NFB = TLX_results_NFB[['Mental Demand' , 'Physical Demand', 'Temporal Demand', 'Performance', 'Effort', 'Frustration Level']]
	_TLX_NFB['Totals'] = _TLX_NFB.sum(axis=1)
 
	for axis in axes:
	
		loc = axes.index(axis)
	
		axis.plot( Qresults_CL_FB_avg.index.values, _TLX_FB.iloc[:,loc].values , label='FB' )
		axis.plot( Qresults_CL_NFB_avg.index.values, _TLX_NFB.iloc[:,loc].values, label='NFB' )
		axis.set_title( _TLX_FB.columns.values[loc] )
		axis.grid( which='both' )
		axis.set_ylim( [0, 16] )
  
	plt.legend( loc='upper right' )
	if save: plt.savefig( os.path.join( os.getcwd(), os.path.join("Output_figs", "Individual {} TLX".format(condition) ) ) )
	if show: plt.show()
	
	fig, ax = plt.subplots()
	ax.plot( TLX_results_FB.index.values, _TLX_FB['Totals'].values , label='FB' )
	ax.plot( TLX_results_NFB.index.values, _TLX_NFB['Totals'].values, label='NFB' )
	ax.set_title('Combined TLX scores {}'.format(app))
	ax.grid()
	plt.legend( loc='upper right' )
	if save: plt.savefig( os.path.join( os.getcwd(), os.path.join("Output_figs", "Combined {} TLX".format(condition) ) ) )
	if show: plt.show()
 
	plt.clf()
	plt.close()

def plot_qual_scores( condition, show = False, save = False ):
	fig, ( ( ax1, ax2, ax3 ), ( ax4, ax5, ax6 ), ( ax7, ax8, ax9 ) ) = plt.subplots( 3, 3 )
 
	if condition == 'CL':
		fig.suptitle('Comparison of Likert scores under high cognitive load')
		qual_results_FB = Qresults_CL_FB_avg
		qual_results_NFB = Qresults_CL_NFB_avg
		app = 'under high cognitive load'
  
	elif condition == 'NL':
		fig.suptitle('Comparison of Likert scores under low cognitive load')
		qual_results_FB = Qresults_NL_FB_avg
		qual_results_NFB = Qresults_NL_NFB_avg
		app = 'under low cognitive load'
  
	else:
		print('No valid condition set, defaulting to without loading.')
		fig.suptitle('Comparison of Likert scores without cognitive load')
		qual_results_FB = Qresults_NL_FB_avg
		qual_results_NFB = Qresults_NL_NFB_avg
		app = 'without cognitive loading'
 
	axes = [ ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9 ]
	
	_qual_FB = qual_results_FB[['It is easy to understand.','It is distracting.','It is user-friendly.','Using it is effortless.','Both occasional and Regular users would like it.','It is difficult to learn how to use.','It works the way I want it to work.','It is pleasant to use.']]
	_qual_FB['Totals'] = _qual_FB.sum(axis=1)
	_qual_NFB = qual_results_NFB[['It is easy to understand.','It is distracting.','It is user-friendly.','Using it is effortless.','Both occasional and Regular users would like it.','It is difficult to learn how to use.','It works the way I want it to work.','It is pleasant to use.']]
	_qual_NFB['Totals'] = _qual_NFB.sum(axis=1)
 
	for axis in axes:
	
		loc = axes.index(axis)
	
		axis.plot( _qual_FB.index.values, _qual_FB.iloc[:,loc].values , label='FB' )
		axis.plot( _qual_NFB.index.values, _qual_NFB.iloc[:,loc].values, label='NFB' )
		axis.set_title( _qual_FB.columns.values[loc] )
		axis.grid( which='both' )
		if not _qual_FB.columns.values[loc] == 'Totals':
			axis.set_ylim( [1, 7] )
  
	plt.legend( loc='upper right' )
	fig.set_size_inches(20,12)
	if save: plt.savefig( os.path.join( os.getcwd(), os.path.join("Output_figs", "{} Qualitative".format(condition) ) ) )
	if show: plt.show()
   
def plot_ADL_scores( participant_list, show = False, save = False ):
	
	FB_ADL = pd.DataFrame()
	NFB_ADL = pd.DataFrame()
	ADL_FB_averages = pd.DataFrame( index=['Cups','Pegs','Pens'], columns=[ 'S1', 'S4', 'S8' ])
	ADL_NFB_averages = pd.DataFrame( index=['Cups','Pegs','Pens'], columns=[ 'S1', 'S4', 'S8' ])
	
	for participant in participant_list:
		if participant is not None and participant.ID in condition_mask:
			FB_ADL = FB_ADL.join( participant.ADL_ratios, how='outer', rsuffix=( "-" + str(participant.ID) ) )
		elif participant is not None and participant.ID not in condition_mask:
			NFB_ADL = NFB_ADL.join( participant.ADL_ratios, how='outer', rsuffix=( '-' + str(participant.ID ) ) )
   
	for session in ADL_NFB_averages.columns:
		ADL_FB_averages[session] = FB_ADL.loc[:,FB_ADL.columns.str.startswith(session)].mean(axis=1)
		ADL_NFB_averages[session] = NFB_ADL.loc[:,NFB_ADL.columns.str.startswith(session)].mean(axis=1)

	fig, (( ax1, ax4), (ax2, ax5), (ax3,ax6) ) = plt.subplots(3,2,sharex=True, sharey=True)

	axes = [ ax1, ax2, ax3, ax4, ax5, ax6]	
	
	for axis in axes:
	# for test in ADL_NFB_averages.index:
		NFB_flag = False
		test_loc = axes.index(axis)
		if test_loc > 2:
			NFB_flag = True
			test_loc -=3
		test = ADL_FB_averages.index[test_loc]
		
		if NFB_flag: 
			axis.boxplot( [ FB_ADL.loc[test, FB_ADL.columns.str.startswith('S1')].dropna(), FB_ADL.loc[test, FB_ADL.columns.str.startswith('S4')].dropna(), FB_ADL.loc[test, FB_ADL.columns.str.startswith('S8')].dropna() ], widths=.6 )
			axis.set_title(str(test) + ' FB')
			FB_fit = np.polyfit([1,2,3],[FB_ADL.loc[test, FB_ADL.columns.str.startswith('S1')].dropna().mean(), FB_ADL.loc[test, FB_ADL.columns.str.startswith('S4')].dropna().mean(), FB_ADL.loc[test, FB_ADL.columns.str.startswith('S8')].dropna().mean()], 2)
			FB_fit_func = np.poly1d(FB_fit)
			axis.plot(np.arange(1,3,0.1),FB_fit_func(np.arange(1,3,0.1)))
		else: 
			axis.boxplot( [ NFB_ADL.loc[test, NFB_ADL.columns.str.startswith('S1')].dropna(), NFB_ADL.loc[test, NFB_ADL.columns.str.startswith('S4')].dropna(), NFB_ADL.loc[test, NFB_ADL.columns.str.startswith('S8')].dropna() ], widths=.6 )#, FB_ADL.loc[test,FB_ADL.columns.str.startswith('S4')].values, FB_ADL.loc[test,FB_ADL.columns.str.startswith('S8')].values ]   )
			axis.set_title(str(test) + ' NFB')
			NFB_fit = np.polyfit([1,2,3],[NFB_ADL.loc[test, NFB_ADL.columns.str.startswith('S1')].dropna().mean(), NFB_ADL.loc[test, NFB_ADL.columns.str.startswith('S4')].dropna().mean(), NFB_ADL.loc[test, NFB_ADL.columns.str.startswith('S8')].dropna().mean()], 2)
			NFB_fit_func = np.poly1d(NFB_fit)
			axis.plot(np.arange(1,3,0.1),NFB_fit_func(np.arange(1,3,0.1)))
   
		axis.set_yticks( np.arange(0,12,1), minor=True )
		axis.grid()
   

	
	# fig.legend()
	fig.set_size_inches(10,8)
	fig.suptitle('Comparison of ADL metrics between conditions')
	if save: plt.savefig( os.path.join( os.getcwd(), os.path.join("Output_figs", "ADL metric scores" ) ) )
	if show: plt.show()
 
	plt.clf()
	plt.close()
		
def plot_times( participant_list, save=False, show = False ):
	
	i = 0
	j = 0
	
	FB_CL_collated_times = pd.DataFrame(index=['L','H','COMB'], columns=['S1','S2','S3','S4','S5','S6','S7','S8']).fillna(0)
	FB_NL_collated_times = pd.DataFrame(index=['L','H','COMB'], columns=['S1','S2','S3','S4','S5','S6','S7','S8']).fillna(0)
	NFB_CL_collated_times = pd.DataFrame(index=['L','H','COMB'], columns=['S1','S2','S3','S4','S5','S6','S7','S8']).fillna(0)
	NFB_NL_collated_times = pd.DataFrame(index=['L','H','COMB'], columns=['S1','S2','S3','S4','S5','S6','S7','S8']).fillna(0)

	for participant in participant_list:
		if participant is not None and not participant.ID.endswith('OPP'):
			if participant.ID in condition_mask:
				i += 1
				FB_CL_collated_times += participant.CL_times_avg.fillna(0)
				FB_NL_collated_times += participant.NL_times_avg.fillna(0)

			else:
				j += 1
				NFB_CL_collated_times += participant.CL_times_avg.fillna(0)
				NFB_NL_collated_times += participant.NL_times_avg.fillna(0)
     
	FB_CL_collated_times = FB_CL_collated_times.div(i*100)
	FB_NL_collated_times = FB_NL_collated_times.div(i*100)
	NFB_CL_collated_times = NFB_CL_collated_times.div(j*100)
	NFB_NL_collated_times = NFB_NL_collated_times.div(j*100)
 
	fig, ( ( ax1, ax2, ax3) , ( ax4, ax5, ax6 ) ) = plt.subplots(2,3)
	axes = [ax1, ax2, ax3, ax4, ax5, ax6 ]
	cond = ['L','H','COMB']	
 
	for axis in axes:
		loc = axes.index(axis)
		axis.set_ylim([0,20])
		axis.grid()
		if loc > 2:
			loc = loc-3
			axis.plot( FB_CL_collated_times.columns.values, FB_CL_collated_times.iloc[loc,:].values , label='FB' )
			axis.plot( NFB_CL_collated_times.columns.values, NFB_CL_collated_times.iloc[loc,:].values , label='NFB' )
			axis.set_title('CL '+ str(FB_CL_collated_times.index[loc]))

		else:
			axis.plot( FB_NL_collated_times.columns.values, FB_NL_collated_times.iloc[loc,:].values , label='FB' )
			axis.plot( NFB_NL_collated_times.columns.values, NFB_NL_collated_times.iloc[loc,:].values , label='NFB' )
			axis.set_title('NL '+ str(FB_NL_collated_times.index[loc]))

		axis.legend(loc='upper right')

	fig.suptitle('Average time in contact with egg')
	fig.set_size_inches(10,6)
	if save: plt.savefig( os.path.join( os.getcwd(), os.path.join("Output_figs", "Grasp time" ) ) )
	if show: plt.show()

	plt.clf()
	plt.close()
 
	return FB_CL_collated_times, FB_NL_collated_times, NFB_CL_collated_times, NFB_NL_collated_times


if __name__ == "__main__":

	results_dir = os.path.join(os.getcwd(), "results_rnd2") # Define path to results folder
	participant_folders = next(os.walk(results_dir))[1] # Obtain a list of directories in the results folder
	Participants = [None]*len(participant_folders) # Initialise an empty list of length x, where x is the number of participant directories

 
	for participant in range(len(participant_folders) ): # Creates a Participant object for each results folder and stores them in a list

		if os.path.isdir(os.path.join( results_dir, participant_folders[participant] )): # Checks all paths to make sure they are a directory

			Participants[participant] = Participant(results_dir, participant_folders[participant])
			_self = Participants[participant]
			_self.load_questionnaire_results()
			_self.load_ADL_scorecards()
			_self.load_Grasp_scorecards()
			_self.load_trial_times()
			_self.process_ADL_results()
			_self.process_grasp_results()
			_self.combine_performance_and_time()
   
			# _self.plot_performance()
			
	print("\n\nDone loading\n\n")
	
	NL_means, NL_means_L, NL_means_H, CL_means, CL_means_L, CL_means_H, FB_NL_means, FB_NL_means_L, FB_NL_means_H, FB_CL_means, FB_CL_means_L, FB_CL_means_H, NFB_NL_means, NFB_NL_means_L, NFB_NL_means_H, NFB_CL_means, NFB_CL_means_L, NFB_CL_means_H, FB_COMB_means, NFB_COMB_means = calculate_all_performance_means( Participants )
	
	Qresults_CL_FB, Qresults_CL_FB_avg, Qresults_NL_FB, Qresults_NL_FB_avg,	Qresults_CL_NFB, Qresults_CL_NFB_avg, Qresults_NL_NFB, Qresults_NL_NFB_avg = calculate_all_qualitative_means( Participants )

	FB_CL_collated_times, FB_NL_collated_times, NFB_CL_collated_times, NFB_NL_collated_times = plot_times( Participants, save = True )
 
	plt.rcParams.update({'font.size':7})
	# plot_overall_performance_means( save = True )
	# plot_TLX_scores( 'CL', save = True )
	# plot_TLX_scores( 'NL', save = True )
	# plot_qual_scores( 'CL', save = True )
	# plot_qual_scores( 'NL', save = True )
	# plot_ADL_scores( Participants, save = True )
	
 
	
	

