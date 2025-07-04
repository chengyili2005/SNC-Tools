# Description: Quick classifier that uses audiograms to classify hearing loss based off of clinical boundaries & military definitions.
# Usage: python hearing_profiler.py [military/clinical] [input_file].xlsx [output_file].xlsx

# Some packages
import os
import sys
import pandas as pd
import numpy as np

# Clinical classification boundaries
clinical_ranges = [
(0, 25, "Normal Hearing"),
(25, 40, "Mild Hearing Loss"),
(40, 60, "Moderate Hearing Loss"),
(60, np.inf, "Severe and Profound hearing loss")
]

# Military boundaries - This models the table from: https://pmc.ncbi.nlm.nih.gov/articles/PMC10571680/table/table1-23312165231198374/
military_ranges = {
	'H0' : {
		'Better' : {'500' : 20, '1000' : 20, '2000' : 20},
		'Worse' : {'500' : 20, '1000' : 20, '2000' : 20}
	},
	'H1' : {
		'Better' : {'500' : 25, '1000' : 25, '2000' : 25},
		'Worse' : {'500' : 30, '1000' : 30, '2000' : 30}
	},
	'H2' : {
		'Better' : {'500' : 25, '1000' : 30, '2000' : 25},
		'Worse' : {'500' : 40, '1000' : 40, '2000' : 60}
	},
	'H3' : {
		'Better' : {'500' : np.inf, '1000' : np.inf, '2000' : np.inf},
		'Worse' : {'500' : np.inf, '1000' : np.inf, '2000' : np.inf}
	}
}

# Helper function: Classifies a soldier's hearing profile based off of clinical metrics
def classify_clinical(RU500, RU1000, RU2000, LU500, LU1000, LU2000):

	# Clinical algorithm
	average_score = (RU500 + RU1000 + RU2000 + LU500 + LU1000 + LU2000)/6
	profile = ""
	for min, max, label in clinical_ranges:
		if min <= average_score <= max:
			profile = label
		if profile != "":
			break
	
	# Returns the profile and the PTA as an ordered pair
	return profile, average_score

# Helper function: Classifies a soldier's hearing profile based off of military metrics
def classify_military(RU500, RU1000, RU2000, LU500, LU1000, LU2000):

	# Military algorithm
	better_profile = ""
	worse_profile = ""
	profile = ""

	# Choose better ear with averages
	right_score = (RU500 + RU1000 + RU2000) / 3 
	left_score = (LU500 + LU1000 + LU2000) / 3 
	right_ear = {'500' : RU500, '1000' : RU1000, '2000' : RU2000}
	left_ear = {'500' : LU500, '1000' : LU1000, '2000' : LU2000}
	better_ear = right_ear if right_score <= left_score else left_ear
	worse_ear = left_ear if better_ear == right_ear else right_ear

	# Classify the better ear
	for label in military_ranges.keys():
		if better_ear['500'] <= military_ranges[label]['Better']['500'] and better_ear['1000'] <= military_ranges[label]['Better']['1000'] and better_ear['2000'] <= military_ranges[label]['Better']['2000']:
			better_profile = label
		if better_profile != "":
			break
	
	# Classify the worse ear
	for label in military_ranges.keys():
		if worse_ear['500'] <= military_ranges[label]['Worse']['500'] and worse_ear['1000'] <= military_ranges[label]['Worse']['1000'] and worse_ear['2000'] <= military_ranges[label]['Worse']['2000']:
			worse_profile = label
		if worse_profile != "":
			break
	
	# Pick the which ear's profile to use
	# NOTE: This is what I'm unsure about.
	# If the algorithm classifies the better ear differently than the worse ear, which one should I choose?
	# For example, 1031's better ear is classified as NH but worse ear is classified as H1
		# Furthermore, 1077's better ear is classified as H3 but worse ear is classified as H2
		# In other words, by PTA's standard of which ear is "better" 
		# is not necessarily the same as the military classification of which ear is better
	profile = worse_profile if better_profile == worse_profile else max(worse_profile, better_profile)
	
	# Rename H0 into 'NH'
	profile = 'NH' if profile == 'H0' else profile
	better_profile = 'NH' if better_profile == 'H0' else better_profile
	worse_profile = 'NH' if worse_profile == 'H0' else worse_profile

	# Return a tuple
	return profile, better_profile, worse_profile

# Main script
def main():

	# Ensure correct usage
	if (len(sys.argv) != 4): 
		print("Correct usage: python hearing_profiler.py [military/clinical] [input_file].xlsx [output_file].xlsx") # in R we might have to instead set a column name
		quit()
	boundaries = sys.argv[1]
	input = sys.argv[2]
	output = sys.argv[3]

	# Read in the file
	df = pd.read_excel(input)

	# Classify clinical
	if (boundaries.lower() == "clinical"):

		# Iterate through all rows, running the classification function
		profiles = []
		ids = []
		debugger = []
		for index, row in df.iterrows():
			profile, average_score = classify_clinical(row['RU500'], row['RU1000'], row['RU2000'], row['LU500'], row['LU1000'], row['LU2000'])
			ids.append(row['ID']) # This ensures the profiles are corresponding to the right ID
			profiles.append(profile)
			debugger.append(average_score) # For debugging

	# Classify military
	elif (boundaries.lower() == "military"): 

		# Iterate through all rows, running the classification function
		profiles = []
		ids = []
		debugger = []
		for index, row in df.iterrows():
			profile, better_profile, worse_profile = classify_military(row['RU500'], row['RU1000'], row['RU2000'], row['LU500'], row['LU1000'], row['LU2000'])
			ids.append(row['ID']) # This ensures the profiles are corresponding to the right ID
			profiles.append(profile)
			debugger.append(f"Better = {better_profile}, Worse = {worse_profile}")


	# Incorrect usage handling	
	else:
		print("Correct usage: python hearing_profiler.py [military/clinical] [input_file].xlsx [output_file].xlsx")
		quit()

	# Convert to excel spreadsheet
	data = {
		'ID' : ids,
		'Profile' : profiles,
		'Debugging' : debugger
	}
	final_df = pd.DataFrame(data)
	final_df.to_excel(output)

# Main call
if __name__ == "__main__":
	main()
	
