
import time, os
import threading
import urllib.request as request
from bs4 import BeautifulSoup as BS
from datetime import datetime as dt

from numpy import full

### Global Variables

debug = False
url = 'http://192.168.4.1/grip'
stop_flag = False
full_run = {}


### Functions

def extract_values(html_string):
	# Convert 'bytes' object to string
	html_string = str(html_string)
	# Remove the leading and trailing characters from the known form of the string
	html_string = html_string[2:(len(html_string)-1)]
	# Split the string at commas
	val_strings = html_string.split(',')
	# Convert to number value
	try: # Tries to convert to integer values
		vals = [int(val_string) for val_string in val_strings]
	except ValueError: # If unable to convert to int, convert to float
		vals = [float(val_string) for val_string in val_strings]

	return vals

def add_to_dict(lst, dct, datapoint):
	timestamp = str(dt.now().strftime("%Y-%m-%d %H:%M:%S")) + '.' + str(datapoint)
	dct[timestamp] = lst

def read_sensors():
	global stop_flag
	datapoint = 0
	while not stop_flag:
		req = request.Request(url)
		client = request.urlopen(req)
		htmldata = client.read()

		pressures = extract_values(htmldata)

		# Store to array with timestamps attached, probably a dictionary
		add_to_dict(pressures, full_run, datapoint)
		datapoint += 1

		if debug:
			print("Raw HTML data: " + str(htmldata))
			print("Processed data: " + str(pressures))

		time.sleep(0.007)

	print(full_run)

def killswitch():
	global stop_flag
	user_input = input("Data collection completed?")
	if user_input or not user_input:
		print("Stopping data collection...")
		stop_flag = True 

def check_or_create_folder(folder):
	if not os.path.isdir(folder):
		os.mkdir(folder)

def create_participant_folders(debug=False):

	# create required folders for complete experimental run for single participant
	resultsFolder = os.path.join(os.getcwd(), "results")
	participantFolder = os.path.join(resultsFolder, str(participantID))
	trainFolders = [ os.path.join(participantFolder, "trial_0%i" % trial) for trial in range(4)]
	reqFolders = [resultsFolder] + [participantFolder] + trainFolders

	if debug:
		print(resultsFolder)
		print(participantFolder)
		print(trainFolders)

	_ = [check_or_create_folder(folder) for folder in reqFolders]

	return reqFolders


if __name__ == '__main__':
	
	# Obtain participant ID and trial number
	p = input("Enter the particpant ID: ")
	s = input("Enter the number of the surrent session (1-8): ")

	# Create necessary folders
	


	reading_thread = threading.Thread(target=read_sensors)
	killswitch_thread = threading.Thread(target=killswitch)
	reading_thread.start()
	killswitch_thread.start()

	# Store readings into .csv and save to correct folder

		

	



