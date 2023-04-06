import pandas as pd, numpy as np, os

class Participant:

	# Public attributes and variables
	ADL_dct = {}  # Session 1 in rows 0-2 and Session 8 in rows 3-5
	ADL1_metrics = {}
	ADL8_metrics = {}
	Grasp_dct = {} 
	NL_Grasp_metrics = {}
	CL_Grasp_metrics = {}

	# Public methods and functions
	def __init__(self, results_dir , participant_ID):
		"""_summary_

		Args:
			results_dir (str): Filepath-like object to results folder
			participant_ID (str): Participant identifier
		"""
		self._empty_storage_variables()
		self.participant_ID = participant_ID
		self.questionnaire_dir = os.path.join(results_dir, "PEQRs.csv")
		self.resultsFolder = os.path.join(results_dir, self.participant_ID)
		if self._debug: print("----------------------------- \n\t P" + self.participant_ID + "\n----------------------------- \t")
		self._load_results()
		self._process_ADLs()
		self._process_grasps()
  
  	# Private attributes and variables
	_debug = True
 
 
	# Private methods and functions
	def _empty_storage_variables(self):
		# Empty all storage functions
		self.Grasp_dct.clear()
		self.NL_Grasp_metrics.clear()
		self.CL_Grasp_metrics.clear()
		self.ADL_dct.clear()
		self.ADL1_metrics.clear()
		self.ADL8_metrics.clear()
 
	def _load_results(self):
		
		# Extracts all questionnaire results relevant to the current participant
		self.questionnaire_results = self._extract_questionnaire_rows(pd.read_csv(self.questionnaire_dir), "Participant ID", self.participant_ID)
		self.CL_Qresults = self._extract_questionnaire_rows(self.questionnaire_results, "Participant ID", "CL")
		self.NL_Qresults = self._extract_questionnaire_rows(self.questionnaire_results, "Participant ID", "NL")

		# Isolates the directory names of each session folder that exists
		session_results_folders = next(os.walk(self.resultsFolder))[1]
		for session in session_results_folders:
			sessionFolder = os.path.join( self.resultsFolder, session )
			for loading in os.listdir(sessionFolder):
				if loading.endswith(".csv"):
        
					if loading.startswith("ADLScorecard"): # Collates all ADL results
						_path = os.path.join(sessionFolder, loading)
						_tmp_df = pd.read_csv(_path, index_col="Trial")
						self.ADL_dct[session] = _tmp_df

					if loading.startswith("Grasp"): # Collates all Grasp results
						_path = os.path.join( sessionFolder, loading)
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

				if ADL_set == "8":
					self.ADL8_metrics[_adl] = self.ADL_dct[ADL_set].at[_adl,"Platform"] / self.ADL_dct[ADL_set].at[_adl,"Manual"]

	def _process_grasps(self):

		for session in self.Grasp_dct.keys():
			self.CL_Grasp_metrics[session] = {
				"Misgrasps" : self.Grasp_dct[session]["CL-Misgrasp"].sum(axis=0),
				"Drops" : self.Grasp_dct[session]["CL-Drop"].sum(axis=0) ,
				"Crushes" : self.Grasp_dct[session]["CL-Crush"].sum(axis=0) ,
				"SessionTotal" : self.Grasp_dct[session]["CL-Misgrasp"].sum(axis=0) + self.Grasp_dct[session]["CL-Drop"].sum(axis=0) + self.Grasp_dct[session]["CL-Crush"].sum(axis=0),
				}
			self.NL_Grasp_metrics[session] = {
				"Misgrasps" : self.Grasp_dct[session]["NL-Misgrasp"].sum(axis=0),
				"Drops" : self.Grasp_dct[session]["NL-Drop"].sum(axis=0) ,
				"Crushes" : self.Grasp_dct[session]["NL-Crush"].sum(axis=0) ,
				"SessionTotal" : self.Grasp_dct[session]["NL-Misgrasp"].sum(axis=0) + self.Grasp_dct[session]["NL-Drop"].sum(axis=0) + self.Grasp_dct[session]["NL-Crush"].sum(axis=0),
				}
		if self._debug:
			print("Loaded metrics:")
			print(self.CL_Grasp_metrics)
			print("Unoaded metrics:")
			print(self.NL_Grasp_metrics)
			print("----------------------------- \t\n\n")

FB_mask = { "001" : False,
            "002" : True , 
            "003" : True ,
            "004" : False,
            "006" : False,
            "009" : True ,
            "010" : True }


if __name__ == "__main__":

	
	results_dir = os.path.join(os.getcwd(), "results") # Define path to results folder
	participant_folders = next(os.walk(results_dir))[1] # Obtain a list of directories in the results folder
	Participants = [None]*len(participant_folders) # Initialise an empty list of length x, where x is the number of participant directories

	for participant in range(len(participant_folders)): # Creates a Participant object for each results folder and stores them in a list

		if os.path.isdir(os.path.join( results_dir, participant_folders[participant] )): # Checks all paths to make sure they are a directory

			Participants[participant] = Participant(results_dir, participant_folders[participant])

   
		


