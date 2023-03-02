import pandas as pd, numpy as np, os

class Participant:

	# Public attributes and variables
	ADL_dct = {} #pd.DataFrame() # Session 1 in rows 0-2 and Session 8 in rows 3-5
	Grasp_dct = {} #pd.DataFrame()

	# Public methods and functions
	def __init__(self, results_dir , participant_ID):
		"""_summary_

		Args:
			results_dir (str): Filepath-like object to results folder
			participant_ID (str): Participant identifier
		"""
		self.participant_ID = participant_ID
		self.questionnaire_dir = os.path.join(results_dir, "PEQRs.csv")
		self.resultsFolder = os.path.join(results_dir, self.participant_ID)
		self._load_results()
  
  	# Private attributes and variables
 
	# Private methods and functions
	def _load_results(self):
		
		# Extracts all questionnaire results relevant to the current participant
		self.questionnaire_results = self._extract_participant_rows(pd.read_csv(self.questionnaire_dir), "Participant ID", self.participant_ID)

		# Isolates the directory names of each session folder that exists
		session_results_folders = next(os.walk(self.resultsFolder))[1]
  
		for session in session_results_folders:
			sessionFolder = os.path.join( self.resultsFolder, session )
   
			for loading in os.listdir(sessionFolder):
				if loading.endswith(".csv"):
        
					if loading.startswith("ADL"): # Collates all ADL results
						_path = os.path.join(sessionFolder, loading)
						_tmp_df = pd.read_csv(_path)
						self.ADL_dct[session] = _tmp_df

					if loading.startswith("Grasp"): # Collates all Grasp results
						_path = os.path.join( sessionFolder, loading)
						_tmp_df = pd.read_csv(_path)
						self.Grasp_dct[session] = _tmp_df

	def _extract_participant_rows(self, df, column_name, search_string):
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


 
 
if __name__ == "__main__":

	
	results_dir = os.path.join(os.getcwd(), "results")
	participant_folders = next(os.walk(results_dir))[1] # Obtain a list of directories in the results folder
	Participants = [None]*len(participant_folders) # Initialise an empty list of length x, where x is the number of participant directories

	for participant in range(len(participant_folders)): # Creates a Participant object for each results folder and stores them in a list

		if os.path.isdir(os.path.join(results_dir,participant_folders[participant])): # Checks all paths to make sure they are a directory

			Participants[participant] = Participant(results_dir, participant_folders[participant])


