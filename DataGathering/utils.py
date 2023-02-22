import os, csv, datetime, random


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
	# return random.shuffle(lst)
	return random.sample(lst, len(lst))