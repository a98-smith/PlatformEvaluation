
import time, threading, utils
import urllib.request as request


### Local Variables

debug = False
url = 'http://192.168.4.1/grip'
stop_flag = False
empty_run = {}
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

def read_sensors():
	global stop_flag
	datapoint = 0
	while not stop_flag:
		req = request.Request(url)
		client = request.urlopen(req)
		htmldata = client.read()

		pressures = extract_values(htmldata)

		# Store to array with timestamps attached, probably a dictionary
		utils.add_to_dict(pressures, full_run, datapoint)
		datapoint += 1

		if debug:
			print("Raw HTML data: " + str(htmldata))
			print("Processed data: " + str(pressures))

		time.sleep(0.007)

	if debug:
		print(full_run)

def killswitch():
	global stop_flag
	user_input = input("Data collection completed?")
	if user_input or not user_input:
		print("Stopping data collection...")
		stop_flag = True 

		

	



