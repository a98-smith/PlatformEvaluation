import os
import pandas as pd, numpy as np
import analysis_utils as utils
import pingouin as pg
# from statsmodels.stats.anova import AnovaRM

import warnings

class Participant:

    _misgrasp_adj = 0.125
    _fail_adj = 0.5

    def __init__( self, results_dir, participant_number, questionnaire_filename='PEQRs.csv', debug=False, timeout=30 ):
        
        self.ID = participant_number    # Stores participant ID
        self._debug = debug             # Sets debug status for the participant
        self._timeout = timeout         # Sets timeout counter for grasp profiles
        self.questionnaire_filepath = os.path.join( results_dir, questionnaire_filename )   # Generates filepath for questionnaire results
        self.results_dir = os.path.join( results_dir, self.ID )         # Creates filepath for the participant's results folder
        self.session_dirs = next( os.walk( self.results_dir ) )[1]      # Creates a list of the sessions in the results folder
        if self._debug: print('Participant {} initialising...'.format(self.ID))


    def create_storage_variables( self ):

        self.raw_grasp_results  = pd.DataFrame()    # DataFrame to store all raw grasp results when loading from scorecards
        self.raw_adl_results    = pd.DataFrame()    # DataFrame to store all raw ADL results when loading from scorecards
        
        fp_idxs = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'mean', 'mean_l', 'mean_h'] # Add stdv here?
        fp_cols = ['S1E','S1','S2E','S2','S3E','S3','S4E','S4','S5E','S5','S6E','S6','S7E','S7','S8E','S8']
        self.raw_force_profiles_cl = pd.DataFrame( index=fp_idxs, columns=fp_cols ) # DataFrane to store force profiles for each trial when loading from results dir
        self.raw_force_profiles_nl = pd.DataFrame( index=fp_idxs, columns=fp_cols ) # DataFrane to store force profiles for each trial when loading from results dir
    
    def load_questionnaire_results( self ):
        """Function that extracts all participant relevant data from the qualitative questionnaire results
        and stores them in publicly available varibales for further analysis.
        """

        self.questionnaire_results      = utils.extract_questionnaire_rows( pd.read_csv( self.questionnaire_filepath ), "Participant ID", self.ID )
        self.questionnaire_results_cl   = utils.extract_questionnaire_rows( self.questionnaire_results, "Participant ID", "CL" )
        self.questionnaire_results_nl   = utils.extract_questionnaire_rows( self.questionnaire_results, "Participant ID", "NL" )
        self.questionnaire_results.reset_index 
        self.questionnaire_results_cl.reset_index 
        self.questionnaire_results_nl.reset_index 

        if self._debug: print( "\tSuccessfully loaded questionnaire results" )
    
    def load_all_scorecards( self ):
        
        ### session for loop to be moved outside of function. ###
        for session in self.session_dirs:
            session_dir = os.path.join( self.results_dir, session )

            for scorecard in [ 'GraspFailureScorecard.csv', 'ADLScorecard.csv' ]:
                _path = os.path.join( session_dir, scorecard )      # Generates path to scorecard object
                try: 
                    _tmp_df = pd.read_csv( _path, index_col='Trial' )   # Reads the scorecard
                    _tmp_df.columns = _tmp_df.columns.map( lambda x: str(x) + session ) # Appends the session to the column names to prevent conflicts when joining
                except:
                    if self._debug: print('No ADL file is session {}'.format(session))

                if scorecard.startswith( 'GraspFailure' ):
                    self.raw_grasp_results = self.raw_grasp_results.join( _tmp_df, how='outer' )   # Appends the scorecard to the raw grasp results dataframe

                if scorecard.startswith( 'ADLScorecard' ):
                    self.raw_adl_results - self.raw_adl_results.join( _tmp_df, how='outer' )        # Appends the scorecard to the raw ADL results DataFrame
                
        if self._debug: print( 'Finished loading scorecards.' )

    def load_force_profiles( self ):

        ### session for loop can be moved outside of function as above ###
        for session in self.session_dirs:
            session_dir = os.path.join( self.results_dir, session )

            for condition in ['CL','NL']:
                condition_dir = os.path.join( session_dir, condition )
                trials = [trial for trial in os.listdir( condition_dir ) if trial.endswith( '.csv' ) ] # Extracts all trial .csv files from the list of files in the folder
                
                for trial in trials:
                    
                    idx = int( trial.split( '-', 1 )[0] )               # Indexing value to make sure the trials end up in the correct index on the DataFrame
                    col = 'S' + str( session )
                    egg = egg = trial.split( '-', 1 )[1][:1]            # Extract egg information from filename
                    trial_file = os.path.join( condition_dir, trial )   # Filepath for session (1-8) condition (CL/NL) trial (1-10) pressure information
       
                    try:
                        _tmp_df = pd.read_csv( trial_file )
                        if condition == 'CL':
                            self.raw_force_profiles_cl.loc[ idx, col ] = _tmp_df.loc[ :, _tmp_df.any() ].mean().values # Averages the finger forces together and strips any points where no contact is experienced
                            self.raw_force_profiles_cl.loc[ idx, col+'E'] = egg

                        elif condition == 'NL':
                            self.raw_force_profiles_nl.loc[ idx, col ] = _tmp_df.loc[ :, _tmp_df.any() ].mean().values
                            self.raw_force_profiles_nl.loc[ idx, col+'E'] = egg
                    
                    except:
                        if self._debug: print('\t\tException raised while loading grasp file P{}/S{}/{}/{}'.format(self.ID, session, condition, trial))
        
        if self._debug: print( 'Loaded force profiles.' )

    def process_grasp_data( self, remove_timeouts=True ):

            ### Process timing and force data
        self.contact_times_cl = self.raw_force_profiles_cl.apply( lambda x: [ len( y ) / 100 if isinstance( y, ( list, tuple, np.ndarray ) ) else y for y in x ] ).replace( 0, np.NaN ) # Calculates the time in seconds that the platform was in contact with an object, and replaces all 0s with NaN to not mess with averaging later
        self.contact_times_nl = self.raw_force_profiles_nl.apply( lambda x: [ len( y ) / 100 if isinstance( y, ( list, tuple, np.ndarray ) ) else y for y in x ] ).replace( 0, np.NaN ) # Calculates the time in seconds that the platform was in contact with an object, and replaces all 0s with NaN to not mess with averaging later

        self.peak_forces_cl = self.raw_force_profiles_cl.apply( lambda x: [ max( y, default=np.NaN ) if isinstance( y, ( list, tuple, np.ndarray ) ) else y for y in x ] ).replace( 0, np.NaN )
        self.peak_forces_nl = self.raw_force_profiles_nl.apply( lambda x: [ max( y, default=np.NaN  ) if isinstance( y, ( list, tuple, np.ndarray ) ) else y for y in x ] ).replace( 0, np.NaN )

        if remove_timeouts:
            self.contact_times_cl = self.contact_times_cl.apply( lambda x: [np.NaN if isinstance( y, ( float, int )) and y > self._timeout else y for y in x ] ) # Replaces values larger than the timeout value with NaN
            self.contact_times_nl = self.contact_times_nl.apply( lambda x: [np.NaN if isinstance( y, ( float, int )) and y > self._timeout else y for y in x ] ) # Replaces values larger than the timeout value with NaN
             
                ## Generate timing metrics

        self.speed_metrics_cl = self.contact_times_cl.apply( lambda x: [ 1 - ( ( y - 1 ) / ( 14 ) ) if isinstance(y,(float, int)) else y for y in x ] )
        self.speed_metrics_nl = self.contact_times_nl.apply( lambda x: [ 1 - ( ( y - 1 ) / ( 14 ) ) if isinstance(y,(float, int)) else y for y in x ] )
        self.speed_metrics_cl = self.speed_metrics_cl.apply( lambda x: [ 0 if isinstance(y,(float, int)) and y < 0 else y for y in x ] )        # Constrain metrics to between 1 and 0 based on timing (1s and 15s respectively)
        self.speed_metrics_nl = self.speed_metrics_nl.apply( lambda x: [ 0 if isinstance(y,(float, int)) and y < 0 else y for y in x ] )
        self.speed_metrics_cl = self.speed_metrics_cl.apply( lambda x: [ 1 if isinstance(y,(float, int)) and y > 1 else y for y in x ] )
        self.speed_metrics_nl = self.speed_metrics_nl.apply( lambda x: [ 1 if isinstance(y,(float, int)) and y > 1 else y for y in x ] )
        
        self.contact_times_nl.loc['mean'] = self.contact_times_nl[:10].mean(axis=0, skipna=True,numeric_only=True) # Calculates the overall mean time in contact
        self.contact_times_cl.loc['mean'] = self.contact_times_cl[:10].mean(axis=0, skipna=True,numeric_only=True)
        self.peak_forces_nl.loc['mean'] = self.peak_forces_nl[:10].mean(axis=0, skipna=True,numeric_only=True) # Calculates the overall mean peak force
        self.peak_forces_cl.loc['mean'] = self.peak_forces_cl[:10].mean(axis=0, skipna=True,numeric_only=True)
        self.speed_metrics_nl.loc['mean'] = self.speed_metrics_nl[:10].mean(axis=0, skipna=True,numeric_only=True) # Calculates the overall mean speed metric
        self.speed_metrics_cl.loc['mean'] = self.speed_metrics_cl[:10].mean(axis=0, skipna=True,numeric_only=True)

        for sesh in range( int( len( self.contact_times_cl.columns ) / 2 ) ):       # Calculates the mean for each session for light and heavy eggs individually
            sesh = sesh*2
            self.contact_times_cl.iloc[11,sesh+1] = self.contact_times_cl[self.contact_times_cl.iloc[:,sesh]=='L'][self.contact_times_cl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.contact_times_cl.iloc[12,sesh+1] = self.contact_times_cl[self.contact_times_cl.iloc[:,sesh]=='H'][self.contact_times_cl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.contact_times_nl.iloc[11,sesh+1] = self.contact_times_nl[self.contact_times_nl.iloc[:,sesh]=='L'][self.contact_times_nl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.contact_times_nl.iloc[12,sesh+1] = self.contact_times_nl[self.contact_times_nl.iloc[:,sesh]=='H'][self.contact_times_nl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.peak_forces_cl.iloc[11,sesh+1] = self.peak_forces_cl[self.peak_forces_cl.iloc[:,sesh]=='L'][self.peak_forces_cl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.peak_forces_cl.iloc[12,sesh+1] = self.peak_forces_cl[self.peak_forces_cl.iloc[:,sesh]=='H'][self.peak_forces_cl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.peak_forces_nl.iloc[11,sesh+1] = self.peak_forces_nl[self.peak_forces_nl.iloc[:,sesh]=='L'][self.peak_forces_nl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.peak_forces_nl.iloc[12,sesh+1] = self.peak_forces_nl[self.peak_forces_nl.iloc[:,sesh]=='H'][self.peak_forces_nl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.speed_metrics_cl.iloc[11,sesh+1] = self.speed_metrics_cl[self.speed_metrics_cl.iloc[:,sesh]=='L'][self.speed_metrics_cl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.speed_metrics_cl.iloc[12,sesh+1] = self.speed_metrics_cl[self.speed_metrics_cl.iloc[:,sesh]=='H'][self.speed_metrics_cl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.speed_metrics_nl.iloc[11,sesh+1] = self.speed_metrics_nl[self.speed_metrics_nl.iloc[:,sesh]=='L'][self.speed_metrics_nl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            self.speed_metrics_nl.iloc[12,sesh+1] = self.speed_metrics_nl[self.speed_metrics_nl.iloc[:,sesh]=='H'][self.speed_metrics_nl.columns[sesh+1]].mean(axis=0, skipna=True,numeric_only=True)
            ### Process grasping data
        
        ## Extracts and splits grasping data from scorecards
        self.grasp_results_cl = self.raw_grasp_results.loc[ :, self.raw_grasp_results.columns.str.startswith( 'CL' ) ] # Extracts all columns relating to the high cognative load
        self.grasp_results_cl.columns = self.grasp_results_cl.columns.str[3:] # Trims the loading prefix off the columns for easier handling
        self.grasp_results_nl = self.raw_grasp_results.loc[ :, self.raw_grasp_results.columns.str.startswith( 'NL' ) ] # Extracts all columns relating to the low cognative load
        self.grasp_results_nl.columns = self.grasp_results_nl.columns.str[3:] # Trims the loading prefix off the columns for easier handling
        
        self.grasp_results_combined = pd.concat( [ self.grasp_results_nl[ self.grasp_results_nl.columns.drop( list( self.grasp_results_nl.filter( regex='Egg' ) ) ) ], self.grasp_results_cl[ self.grasp_results_cl.columns.drop( list( self.grasp_results_cl.filter( regex='Egg' ) ) ) ] ] ) 

        ## Generate grasping success metrics
        self.grasp_metrics_combined = pd.DataFrame()
        self.grasp_metrics_cl = pd.DataFrame()
        self.grasp_metrics_nl = pd.DataFrame()

        for session in range( int( len( self.grasp_results_combined.columns ) / 3 ) ): # Combined performance averages across trial numbers and sessions (averaged between CL and NL cases, irrespective of eggs)
            _mis_col = session*3
            _tmp_df =  1 - ( self.grasp_results_combined.iloc[ :, _mis_col ] * self._misgrasp_adj + ( ( self.grasp_results_combined.iloc[ :, _mis_col + 1 ] + self.grasp_results_combined.iloc[:, _mis_col + 2 ] ) * self._fail_adj ) ) 
            _col_title = 'S'+str(session+1)
            _tmp_df = _tmp_df.rename(_col_title)
            _tmp_df = pd.DataFrame(_tmp_df)
            _tmp_df[_tmp_df < 0] = 0 			# Turns any negative values into 0, should I though?

            total_mean_calc = pd.DataFrame( _tmp_df[_col_title].mean(axis=0, skipna=True, numeric_only=True), index=["mean"], columns=[_col_title] )
            _tmp_df = pd.concat( [ _tmp_df, total_mean_calc ], axis=0 )
            self.grasp_metrics_combined = pd.concat( [ self.grasp_metrics_combined, _tmp_df ], axis=1 )
    
        for session in range( int( len( self.grasp_results_cl.columns ) / 4 ) ): # Extracts and processes grasp results for Cognitive loading condition
            
            _egg_col = session*4
            _tmp_df =  1 - ( self.grasp_results_cl.iloc[ :, _egg_col + 1 ] * self._misgrasp_adj + ( ( self.grasp_results_cl.iloc[ :, _egg_col+2 ] + self.grasp_results_cl.iloc[:, _egg_col+3 ] ) * self._fail_adj ) ) 
            _col_title = 'S'+str(session+1)
            _egg_title = 'Egg'+str(session+1)
            _tmp_df = _tmp_df.rename(_col_title)
            _tmp_df = pd.DataFrame(_tmp_df)
            _tmp_df[_tmp_df < 0] = 0 			# Turns any negative values into 0, should I though?
            _tmp_df = pd.concat( [ self.grasp_results_cl.iloc[ :, _egg_col ], _tmp_df ] , axis=1 ).rename(columns={_egg_title:_col_title+'E'})
            total_mean_calc = pd.DataFrame( _tmp_df[_col_title].mean(axis=0, skipna=True, numeric_only=True), index=["mean"], columns=[_col_title] )
            light_mean_calc = pd.DataFrame( _tmp_df[_tmp_df.iloc[:,0]=="L"][_col_title].mean(), index=["mean_l"], columns=[_col_title] )
            heavy_mean_calc = pd.DataFrame( _tmp_df[_tmp_df.iloc[:,0]=="H"][_col_title].mean(), index=["mean_h"], columns=[_col_title] )

            _tmp_df = pd.concat( [ _tmp_df, total_mean_calc, light_mean_calc, heavy_mean_calc ], axis=0 )
            self.grasp_metrics_cl = pd.concat( [ self.grasp_metrics_cl, _tmp_df ], axis=1 )

        for session in range( int( len( self.grasp_results_nl.columns ) / 4 ) ): # Extracts and processes grasp results for Low loading condition
            
            _egg_col = session*4
            _tmp_df =  1 - ( self.grasp_results_nl.iloc[ :, _egg_col + 1 ] * self._misgrasp_adj + ( ( self.grasp_results_nl.iloc[ :, _egg_col+2 ] + self.grasp_results_nl.iloc[:, _egg_col+3 ] ) * self._fail_adj ) ) 
            _col_title = 'S'+str(session+1)
            _tmp_df = _tmp_df.rename(_col_title)
            _tmp_df = pd.DataFrame(_tmp_df)
            _tmp_df[_tmp_df < 0] = 0 			# Turns any negative values into 0, should I though?
            _tmp_df = pd.concat( [ self.grasp_results_nl.iloc[ :, _egg_col ], _tmp_df ] , axis=1 )

            total_mean_calc = pd.DataFrame( _tmp_df[_col_title].mean(axis=0, skipna=True, numeric_only=True), index=["mean"], columns=[_col_title] )
            light_mean_calc = pd.DataFrame( _tmp_df[_tmp_df.iloc[:,0]=="L"][_col_title].mean(), index=["mean_l"], columns=[_col_title] )
            heavy_mean_calc = pd.DataFrame( _tmp_df[_tmp_df.iloc[:,0]=="H"][_col_title].mean(), index=["mean_h"], columns=[_col_title] )
            _tmp_df = pd.concat( [ _tmp_df, total_mean_calc, light_mean_calc, heavy_mean_calc ], axis=0 )
            self.grasp_metrics_nl = pd.concat( [ self.grasp_metrics_nl, _tmp_df ], axis=1 )

        self.performance_metrics_nl = self.grasp_metrics_nl.select_dtypes( exclude=[ 'object' ] ) * self.speed_metrics_nl.select_dtypes( exclude=[ 'object' ] )
        self.performance_metrics_cl = self.grasp_metrics_cl.select_dtypes( exclude=[ 'object' ] ) * self.speed_metrics_cl.select_dtypes( exclude=[ 'object' ] )

        if self._debug: print( "Processing grasp metrics complete" )

    def process_adl_results( self ):

        manual = self.raw_adl_results[ [ x for x in self.raw_adl_results.columns if 'Manual' in x ] ]           # Extracts datapoints from huamn hand function
        platform = self.raw_adl_results[ [ x for x in self.raw_adl_results.columns if 'Platform' in x ] ]       # Extracts datapoints using machine platform
        manual.columns = manual.columns.map( lambda x: 'S' + x[-1] )          # Rename DF columns to be compatible with future transforms
        platform.columns = platform.columns.map( lambda x: 'S' + x[-1] )      #( if this doesnt work maybe phrase a y in x thing)

        self.adl_ratios = platform / manual     # Compute ratios for all ADLs

        if self._debug: print( 'Processing ADLs complete.' )

    def create_analysis_dataframe( self ):
        
        self.analysis_df = pd.DataFrame()

        for session in range( len( self.session_dirs ) ):
            col = 'S' + str( session + 1 )
            for loading in [ 'CL', 'NL' ]:
                if loading == 'CL':
                    _tmp_df_quant = { 'ID' : self.ID,                                               # Participant ID
                                'Session' : session + 1,                                            # Session Number
                                'Loading' : loading,                                                # Cognitive Load
                                'P' : self.performance_metrics_cl.loc['mean', col] ,                # Mean performance metric (inc. time)
                                'P_l' : self.performance_metrics_cl.loc['mean_l', col] ,            # ^^ for light eggs only
                                'P_h' : self.performance_metrics_cl.loc['mean_h', col] ,            # ^^ for heavy eggs only
                                'G' : self.grasp_metrics_cl.loc['mean', col] ,
                                'G_l' : self.grasp_metrics_cl.loc['mean_l', col] ,
                                'G_h' : self.grasp_metrics_cl.loc['mean_h', col] ,
                                'T' : self.speed_metrics_cl.loc['mean', col] ,
                                'T_l' : self.speed_metrics_cl.loc['mean_l', col] ,
                                'T_h' : self.speed_metrics_cl.loc['mean_h', col] ,
                                'F' : self.peak_forces_cl.loc['mean', col] ,
                                'F_l' : self.peak_forces_cl.loc['mean_l', col] ,
                                'F_h' : self.peak_forces_cl.loc['mean_h', col] } 
                    
                    _tmp_dct_qual = utils.extract_questionnaire_rows(self.questionnaire_results_cl, 'Session Number', str( session + 1 ) ).iloc[ :, 4: ]
                    
                if loading == 'NL':
                    _tmp_df_quant = { 'ID' : self.ID,
                                'Session' : session + 1,
                                'Loading' : loading,
                                'P' : self.performance_metrics_nl.loc['mean', col] ,
                                'P_l' : self.performance_metrics_nl.loc['mean_l', col] ,
                                'P_h' : self.performance_metrics_nl.loc['mean_h', col] ,
                                'G' : self.grasp_metrics_nl.loc['mean', col] ,
                                'G_l' : self.grasp_metrics_nl.loc['mean_l', col] ,
                                'G_h' : self.grasp_metrics_nl.loc['mean_h', col] ,
                                'T' : self.speed_metrics_nl.loc['mean', col] ,
                                'T_l' : self.speed_metrics_nl.loc['mean_l', col] ,
                                'T_h' : self.speed_metrics_nl.loc['mean_h', col] ,
                                'F' : self.peak_forces_nl.loc['mean', col] ,
                                'F_l' : self.peak_forces_nl.loc['mean_l', col] ,
                                'F_h' : self.peak_forces_nl.loc['mean_h', col] } 
                    
                    _tmp_dct_qual = utils.extract_questionnaire_rows(self.questionnaire_results_nl, 'Session Number', str( session + 1 ) ).iloc[ :, 4: ]                                     
                    
                _tmp_dct_qual.reset_index(inplace=True)
                _tmp_df = pd.DataFrame( _tmp_df_quant, index=[0] ).join( _tmp_dct_qual, how='left' )
                
                self.analysis_df = pd.concat( [ self.analysis_df, _tmp_df ] )
                
        self.analysis_df.reset_index(inplace=True, drop=True)

        if self._debug: print('Analysis DataFrame generated')

    def print_all_metric_dfs( self ):
        print( '###### PERFORMANCE METRICS ######' )
        print( 'CL', self.performance_metrics_cl, '\n-------------------------------------------' )
        print( 'NL', self.performance_metrics_nl, '\n-------------------------------------------' )
        
        print( '###### GRASP METRICS ######' )
        print( 'CL', self.grasp_metrics_cl, '\n-------------------------------------------' )
        print( 'NL', self.grasp_metrics_nl, '\n-------------------------------------------' )

        print( '###### SPEED METRICS ######' )
        print( 'CL', self.speed_metrics_cl, '\n-------------------------------------------' )
        print( 'NL', self.speed_metrics_nl, '\-------------------------------------------' )

if __name__ == "__main__":

    results_dir = os.path.join(os.getcwd(), "results_rnd2") # Define path to results folder
    participant_folders = next(os.walk(results_dir))[1] # Obtain a list of directories in the results folder
    Participants = [None]*len(participant_folders) # Initialise an empty list of length x, where x is the number of participant directories
    
    feedback_mask = [ '021', '023', '026', '030', '031', '032' ]

    combined_analysis_dataframe = pd.DataFrame()
 
    for participant in range(len(participant_folders) ): # Creates a Participant object for each results folder and stores them in a list

        if os.path.isdir(os.path.join( results_dir, participant_folders[participant] )): # Checks all paths to make sure they are a directory

            Participants[participant] = Participant(results_dir, participant_folders[participant], debug=False)
            _self = Participants[participant]
            if not _self.ID.endswith('OPP'):
                _self.create_storage_variables()
                _self.load_questionnaire_results()
                _self.load_all_scorecards()
                _self.load_force_profiles()
                _self.process_grasp_data()
                _self.process_adl_results()
                _self.create_analysis_dataframe()
                # _self.print_all_metric_dfs()
                
                combined_analysis_dataframe = pd.concat( [combined_analysis_dataframe, _self.analysis_df]).drop('index', axis=1)
    
    combined_analysis_dataframe.reset_index( inplace=True, drop=True )        
    combined_analysis_dataframe = combined_analysis_dataframe.join( combined_analysis_dataframe['ID'].isin( feedback_mask ).rename('Feedback') ) # Adds in column containing boolean map of participants in the feedback condition
    combined_analysis_dataframe['Feedback'] = combined_analysis_dataframe['Feedback'].replace( { True:1, False:0 } )
    cl_analysis_dataframe = combined_analysis_dataframe[combined_analysis_dataframe['Loading']=='CL']
    cl_analysis_dataframe.reset_index( inplace=True, drop=True )
    nl_analysis_dataframe = combined_analysis_dataframe[combined_analysis_dataframe['Loading']=='NL']
    nl_analysis_dataframe.reset_index( inplace=True, drop=True )
    
    utils.check_or_create_folder('Output logs')
    
    combined_analysis_dataframe.to_csv( os.path.join( os.getcwd(), os.path.join('Output logs', 'combined_df.csv')))
    cl_analysis_dataframe.to_csv( os.path.join( os.getcwd(), os.path.join('Output logs', 'cl_df.csv')))
    nl_analysis_dataframe.to_csv( os.path.join( os.getcwd(), os.path.join('Output logs', 'nl_df.csv')))
    
    warnings.filterwarnings('ignore')
    print( 'Beginning statistical analysis...')

    for var in combined_analysis_dataframe.columns[3:29]:

        aov = pg.mixed_anova( data=combined_analysis_dataframe, dv=var, within='Session', subject='ID', between='Feedback') # Runs mixed_measures anova over entire dataframe
        aov_cl = pg.mixed_anova( data=cl_analysis_dataframe, dv=var, within='Session', subject='ID', between='Feedback') # Runs mixed_measures anova over high cognitive load condition
        aov_nl = pg.mixed_anova( data=nl_analysis_dataframe, dv=var, within='Session', subject='ID', between='Feedback') # Runs mixed_measures anova over low cognitive load condition
    
    
        if (aov['p-unc'] <= 0.05).any() : 
        
            high_significance = aov[(aov['p-unc'] <= 0.05)]
            
            for case in high_significance['Source'].values:
                if not case == 'Session':
                    print( 'High Significance achieved for dependant variable {} across {}.'.format( var, case ) )
                    print(aov.round(3))
                    
        elif (aov['p-unc'] <= 0.1).any() :
            
            low_significance = aov[(aov['p-unc'] <= 0.1)]
            
            for case in low_significance['Source'].values:
                if not case == 'Session':
                    print( 'Low Significance achieved for dependant variable {} across {}.'.format( var, case ) )
                    print(aov.round(3))
                    
        # if (aov_cl['p-unc'] < 0.1).any() : 
        
        #     significance = aov_cl[(aov_cl['p-unc'] < 0.05)]
            
        #     for case in significance['Source'].values:
        #         if not case == 'Session':
        #             print( 'Significance achieved for dependant variable {} across {} IN HIGH COGNITIVE LOADING.'.format( var, case ) )
            
        #     # print('Dependant variable: ', var)
        #             print(aov_cl.round(3))
                    
        # if (aov_nl['p-unc'] < 0.1).any() : 
        
        #     significance = aov_nl[(aov_nl['p-unc'] < 0.05)]
            
        #     for case in significance['Source'].values:
        #         if not case == 'Session':
        #             print( 'Significance achieved for dependant variable {} across {} IN LOW COGNITIVE LOADING.'.format( var, case ) )
        #             print(aov_nl.round(3))
                    
        # aov.round(5).to_csv('boobs.csv', sep=',')