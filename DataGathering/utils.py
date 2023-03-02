import os, csv, datetime, random, shutil


def check_or_create_folder(folder):
	if not os.path.isdir(folder):
		os.mkdir(folder)

def create_participant_folders(debug, p, s):

	# create required folders for complete experimental run for single participant
	resultsFolder = os.path.join(os.getcwd(), "results")
	participantFolder = os.path.join(resultsFolder, str(p))
	sessionFolder = os.path.join(participantFolder, str(s))
	CLFolder = os.path.join(sessionFolder, "CL")
	NLFolder = os.path.join(sessionFolder, "NL")
	reqFolders = [resultsFolder] + [participantFolder] + [sessionFolder] + [CLFolder] + [NLFolder]

	if debug:
		print(resultsFolder)
		print(participantFolder)

	_ = [check_or_create_folder(folder) for folder in reqFolders]

	return sessionFolder

def save_to_csv(dct, file_name):
	
	file_name = file_name + ".csv"
	with open(file_name, 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(dct.keys())
		writer.writerows(zip(*dct.values()))

def add_to_dict(lst, dct, datapoint):
	timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '.' + str(datapoint)
	dct[timestamp] = lst

def create_random_list(length, options):
	random_list = []
	for i in range(length):
		random_list.append(random.choice(options))
	
	return random_list

def shuffle_list(lst):
	"""
	Shuffle the elements in a list and returns as a new variable

	Args:
		lst (list): List to be shuffled

	Output:
		Shuffled list
	"""
	return random.sample(lst, len(lst))

def clone_file(src_repo, filename, dest_dir):
	"""
	Copy a file from a source repository to a target directory.

	Args:
		src_repo (str): Path to the source repository.
		filename (str): Name of the file to copy.
		dest_dir (str): Path to the target directory.
	"""
	src_file = os.path.join(src_repo, filename)
	shutil.copy(src_file, dest_dir)
 
 
def copy_rename_file(src_dir_path, src_file_name, dest_dir_path, new_file_name):
	"""
	Copy a file from a source directory to a destination directory and rename the file.

	Args:
		src_dir_path (str): Path of the source directory.
		src_file_name (str): Name of the file to be copied from the source directory.
		dest_dir_path (str): Path of the destination directory.
		new_file_name (str): Name of the copied file in the destination directory.
	"""
	# Create destination directory if it does not exist
	if not os.path.exists(dest_dir_path):
		os.makedirs(dest_dir_path)
  
	src_file_path = os.path.join(src_dir_path, src_file_name)
 
	# Construct the path for the new file in the destination directory
	dest_file_path = os.path.join(dest_dir_path, new_file_name)

	# Copy the file to the destination directory with the new name
	shutil.copy2(src_file_path, dest_file_path)