import pandas as pd, numpy as np, os

class Participant:

	# Public attributes and variables DEFINING MUTABLE OBJECTS (list, Dicts etc) HERE SHARES THEM AMONG ALL INSTANCES OF PARTICIPANT (UNDESIRABLE)
	# ADL_dct = {}  # Session 1 in rows 0-2 and Session 8 in rows 3-5
	# ADL1_metrics = {}
	# ADL8_metrics = {}
	# Grasp_dct = {} 
	# NL_Grasp_metrics = {}
	# CL_Grasp_metrics = {}

	# Public methods and functions
	def __init__(self, results_dir , participant_ID):
		"""_summary_

		Args:
			results_dir (str): Filepath-like object to results folder
			participant_ID (str): Participant identifier
		"""
		self._create_storage_variables()
		self.participant_ID = participant_ID
		self.questionnaire_dir = os.path.join(results_dir, "PEQRs.csv")
		self.resultsFolder = os.path.join(results_dir, self.participant_ID)
		if self._debug: print("----------------------------- \n\t P" + self.participant_ID + "\n----------------------------- \t")
		self._load_results()
		self._process_ADLs()
		self._process_grasps()
  
  	# Private attributes and variables
	# _debug = True
	_debug = False
 

  
  
	# Private methods and functions
 
	def _create_storage_variables(self):
		# Creates class variables for each individual participant
		self.ADL_dct = {}  # Session 1 in rows 0-2 and Session 8 in rows 3-5
		self.ADL1_metrics = {}
		self.ADL4_metrics = {}
		self.ADL8_metrics = {}
  
		self.Grasp_dct = {}
  
		self.CL_Light_Egg_dct = {}
		self.CL_Light_Egg_totals = {}
		self.CL_Heavy_Egg_dct = {}
		self.CL_Heavy_Egg_totals = {}
		self.CL_Grasp_dct = {}
		self.CL_Grasp_totals = {}
		self.CL_Performance_Light_Egg = {}
		self.CL_LE_Performance_averages = {}
    
		self.NL_Light_Egg_dct = {}
		self.NL_Light_Egg_totals = {}
		self.NL_Heavy_Egg_dct = {}
		self.NL_Heavy_Egg_totals = {}
		self.NL_Grasp_dct = {}
		self.NL_Grasp_totals = {}

  
	def _empty_storage_variables(self):
		# Empty all storage functions
		self.Grasp_dct.clear()
		self.NL_Grasp_totals.clear()
		self.CL_Grasp_totals.clear()
		self.ADL_dct.clear()
		self.ADL1_metrics.clear()
		self.ADL4_metrics.clear()
		self.ADL8_metrics.clear()
 
	def _load_results(self):
		
		# Extracts all questionnaire results relevant to the current participant
		self.questionnaire_results = self._extract_questionnaire_rows(pd.read_csv(self.questionnaire_dir), "Participant ID", self.participant_ID)
		self.CL_Qresults = self._extract_questionnaire_rows(self.questionnaire_results, "Participant ID", "CL")
		self.NL_Qresults = self._extract_questionnaire_rows(self.questionnaire_results, "Participant ID", "NL")

		# Isolates the directory names of each session folder that exists
		self.session_results_folders = next(os.walk(self.resultsFolder))[1]
		for session in self.session_results_folders:
			sessionFolder = os.path.join( self.resultsFolder, session )
			for scorecard in os.listdir(sessionFolder):
				if scorecard.endswith(".csv"):
					
					if scorecard.startswith("ADLScorecard"): # Collates all ADL results
						_path = os.path.join(sessionFolder, scorecard)
						_tmp_df = pd.read_csv(_path, index_col="Trial")
						self.ADL_dct[session] = _tmp_df

					if scorecard.startswith("Grasp"): # Collates all Grasp results
						_path = os.path.join( sessionFolder, scorecard)
						_tmp_df = pd.read_csv(_path, index_col="Trial")
						self.Grasp_dct[session] = _tmp_df

	def _extract_questionnaire_rows(self, df, column_name, search_string):
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
		mask = df[column_name].str.contains(search_string, na=False)

		# Use the mask to select only the rows that match the search criteria.
		matching_rows = df[mask]

		return matching_rows

	def _process_ADLs(self):
		for ADL_set in self.ADL_dct.keys():
			for _adl in self.ADL_dct[ADL_set].index:
				
				if ADL_set == "1":
					self.ADL1_metrics[_adl] = self.ADL_dct[ADL_set].at[_adl,"Platform"] / self.ADL_dct[ADL_set].at[_adl,"Manual"]

				if ADL_set == "4":
					self.ADL4_metrics[_adl] = self.ADL_dct[ADL_set].at[_adl,"Platform"] / self.ADL_dct[ADL_set].at[_adl,"Manual"]


				if ADL_set == "8":
					self.ADL8_metrics[_adl] = self.ADL_dct[ADL_set].at[_adl,"Platform"] / self.ADL_dct[ADL_set].at[_adl,"Manual"]

	def _process_grasps(self):

		for session in self.Grasp_dct.keys():
			self.CL_Grasp_dct[session] = self.Grasp_dct[session].loc[:, self.Grasp_dct[session].columns.str.startswith('CL')].rename(columns={"CL-Egg":"Egg", "CL-Misgrasp":"Misgrasp", "CL-Drop":"Drop", "CL-Crush":"Crush"})
			self.NL_Grasp_dct[session] = self.Grasp_dct[session].loc[:, self.Grasp_dct[session].columns.str.startswith('NL')].rename(columns={"NL-Egg":"Egg", "NL-Misgrasp":"Misgrasp", "NL-Drop":"Drop", "NL-Crush":"Crush"})
			
			self.CL_Light_Egg_dct[session] = self.CL_Grasp_dct[session][self.CL_Grasp_dct[session]["Egg"]=="L"].drop("Egg", axis=1)
			self.CL_Heavy_Egg_dct[session] = self.CL_Grasp_dct[session][self.CL_Grasp_dct[session]["Egg"]=="H"].drop("Egg", axis=1)

			self.NL_Light_Egg_dct[session] = self.NL_Grasp_dct[session][self.NL_Grasp_dct[session]["Egg"]=="L"].drop("Egg", axis=1)
			self.NL_Heavy_Egg_dct[session] = self.NL_Grasp_dct[session][self.NL_Grasp_dct[session]["Egg"]=="H"].drop("Egg", axis=1)

			self.CL_Grasp_totals[session] = {
				"Misgrasps" : self.CL_Grasp_dct[session]["Misgrasp"].sum(axis=0),
				"Drops" : self.CL_Grasp_dct[session]["Drop"].sum(axis=0) ,
				"Crushes" : self.CL_Grasp_dct[session]["Crush"].sum(axis=0) ,
				"SessionTotal" : self.CL_Grasp_dct[session]["Misgrasp"].sum(axis=0) + self.CL_Grasp_dct[session]["Drop"].sum(axis=0) + self.CL_Grasp_dct[session]["Crush"].sum(axis=0),
				}

			self.NL_Grasp_totals[session] = {
				"Misgrasps" : self.NL_Grasp_dct[session]["Misgrasp"].sum(axis=0),
				"Drops" : self.NL_Grasp_dct[session]["Drop"].sum(axis=0) ,
				"Crushes" : self.NL_Grasp_dct[session]["Crush"].sum(axis=0) ,
				"SessionTotal" : self.NL_Grasp_dct[session]["Misgrasp"].sum(axis=0) + self.NL_Grasp_dct[session]["Drop"].sum(axis=0) + self.NL_Grasp_dct[session]["Crush"].sum(axis=0),
				}

			self.CL_Light_Egg_totals[session] = {
				"Misgrasps" : self.CL_Light_Egg_dct[session]["Misgrasp"].sum(axis=0),
				"Drops" : self.CL_Light_Egg_dct[session]["Drop"].sum(axis=0) ,
				"Crushes" : self.CL_Light_Egg_dct[session]["Crush"].sum(axis=0) ,
				"SessionTotal" : self.CL_Light_Egg_dct[session]["Misgrasp"].sum(axis=0) + self.CL_Grasp_dct[session]["Drop"].sum(axis=0) + self.CL_Grasp_dct[session]["Crush"].sum(axis=0),
				}

			self.CL_Heavy_Egg_totals[session] = {
				"Misgrasps" : self.CL_Heavy_Egg_dct[session]["Misgrasp"].sum(axis=0),
				"Drops" : self.CL_Heavy_Egg_dct[session]["Drop"].sum(axis=0) ,
				"Crushes" : self.CL_Heavy_Egg_dct[session]["Crush"].sum(axis=0) ,
				"SessionTotal" : self.CL_Heavy_Egg_dct[session]["Misgrasp"].sum(axis=0) + self.CL_Heavy_Egg_dct[session]["Drop"].sum(axis=0) + self.CL_Heavy_Egg_dct[session]["Crush"].sum(axis=0),
				}
   
			self.NL_Light_Egg_totals[session] = {
				"Misgrasps" : self.NL_Light_Egg_dct[session]["Misgrasp"].sum(axis=0),
				"Drops" : self.NL_Light_Egg_dct[session]["Drop"].sum(axis=0) ,
				"Crushes" : self.NL_Light_Egg_dct[session]["Crush"].sum(axis=0) ,
				"SessionTotal" : self.NL_Light_Egg_dct[session]["Misgrasp"].sum(axis=0) + self.NL_Light_Egg_dct[session]["Drop"].sum(axis=0) + self.NL_Light_Egg_dct[session]["Crush"].sum(axis=0),
				}

			self.NL_Heavy_Egg_totals[session] = {
				"Misgrasps" : self.NL_Heavy_Egg_dct[session]["Misgrasp"].sum(axis=0),
				"Drops" : self.NL_Heavy_Egg_dct[session]["Drop"].sum(axis=0) ,
				"Crushes" : self.NL_Heavy_Egg_dct[session]["Crush"].sum(axis=0) ,
				"SessionTotal" : self.NL_Heavy_Egg_dct[session]["Misgrasp"].sum(axis=0) + self.NL_Heavy_Egg_dct[session]["Drop"].sum(axis=0) + self.NL_Heavy_Egg_dct[session]["Crush"].sum(axis=0),
				}

			
			CL_LE_trial_performance = [1 - (( self.CL_Light_Egg_dct[session].loc[trial].drop(columns=['Egg','Misgrasp']).sum(axis=0) / 10 ) + 
				( self.CL_Light_Egg_dct[session].loc[trial]['Misgrasp'] / 40 )) for trial in self.CL_Light_Egg_dct[session].index.array]
			CL_LE_trial_performance = [ 0 if result < 0 else result for result in CL_LE_trial_performance] # Sets any negative values to 0 to indicate minimum scoring
     
			self.CL_Performance_Light_Egg[session] = CL_LE_trial_performance
			try:
				self.CL_LE_Performance_averages[session] = round(sum(CL_LE_trial_performance) / len(CL_LE_trial_performance), 3)
			except:
				""""""""
			
		# print(self.CL_Performance_Light_Egg)
		if len(self.participant_ID) < 5:
			print(self.participant_ID + ":\t\t", self.CL_LE_Performance_averages)
		else:
			print(self.participant_ID + ":\t", self.CL_LE_Performance_averages)

   
		if self._debug:
			print("Loaded totals:")
			print(self.CL_Grasp_totals)
			print("Unoaded totals:")
			print(self.NL_Grasp_totals)
			print("----------------------------- \t\n\n")



if __name__ == "__main__":

	
	results_dir = os.path.join(os.getcwd(), "results_rnd2") # Define path to results folder
	participant_folders = next(os.walk(results_dir))[1] # Obtain a list of directories in the results folder
	Participants = [None]*len(participant_folders) # Initialise an empty list of length x, where x is the number of participant directories

	for participant in range(len(participant_folders)): # Creates a Participant object for each results folder and stores them in a list

		if os.path.isdir(os.path.join( results_dir, participant_folders[participant] )): # Checks all paths to make sure they are a directory

			Participants[participant] = Participant(results_dir, participant_folders[participant])


	some_variable = [ participant.CL_LE_Performance_averages for participant in Participants]
	print(some_variable)
	# for p in range(len(Participants)):
	# 	for key in Participants[p].ADL1_metrics.keys():	
	# 		try:
	# 			print( Participants[p].participant_ID, key+":" )
	# 			print( Participants[p].ADL1_metrics[key] - Participants[p].ADL4_metrics[key] ) 
	# 			print( Participants[p].ADL4_metrics[key] - Participants[p].ADL8_metrics[key] ) 
	# 		except:
	# 			print("Error")
 
	
   
