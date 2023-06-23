import os

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