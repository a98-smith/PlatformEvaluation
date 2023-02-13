## Global libraries
import threading, os

## Local imports
import SensorReadingAcquisition as SRA
import utils

## Global Variables
debug = True
datapoints = 15



if __name__ == '__main__':
	
	# Obtain participant ID and trial number
	participantID = input("Enter the particpant ID: ")
	session = input("Enter the number of the surrent session (1-8): ")
	
	# Checks for required folders, and creates any missing directories
	sessionFolder = utils.create_participant_folders(debug, participantID, session)
	print("Folders created for P%s, Session %s \n\n" % (participantID, session))
 
	print("Proceed with Noise Floor evaluation.")	# Perform noise floor evaluation through Arduino Serial interface
	
	# Repeats data collection for each grasp to simplify analysis
	for trial in range(1, datapoints+1):
		input(f"Press enter to begin data collection for Trial {trial} of {datapoints}")
 
		acquisitionThread = threading.Thread(target=SRA.read_sensors) # Strips Sensor readings from server and adds to dictionary
		killswitchThread = threading.Thread(target=SRA.killswitch)  # Listens for serial input to stop data collection
		acquisitionThread.start()
		killswitchThread.start()
    
		# Saves collected data to .csv file in the defined directory
		trial_data_path = os.path.join(sessionFolder, str(trial))
		utils.save_to_csv(SRA.full_run, trial_data_path)
		SRA.full_run = SRA.empty_run # Clear the variable of the previous runs data
		
		# Wait for threads to terminate before starting again
		acquisitionThread.join()
		killswitchThread.join()
	
	
	print("Box and Blocks Session {} complete.".format(session))

  
  

