# Quick classifier that uses audiograms to classify hearing loss based off of clinical boundaries & military definitions.

# Usage
# Run this script in the terminal using the command: python hearing_profiler.py [military/clinical] [input_file].xlsx [output_file].xlsx

# Some packages
import os
import sys
import pandas as pd

# Main call
if __name__ == "__main__":

	# Ensure correct usage
	if (len(sys.argv) != 4): 
		print("Correct usage: python hearing_profiler.py [military/clinical] [input_file].xlsx [output_file].xlsx") # in R we might have to instead set a column name
		quit()
	boundaries = sys.argv[1]
	input = sys.argv[2]
	output = sys.argv[3]

	# Set the classification boundaries
	if (boundaries.lower() == "clinical"): # PLACEHOLDER these are just values I found from an online chart!
		ranges = [
			(0, 25, "Normal"),
			(25, 40, "Mild"),
			(40, 70, "Moderate"),
			(70, 90, "Severe"),
			(90, 120, "Profound")
		]
	elif (boundaries.lower() == "military"): # PLACEHOLDER these are just values I found from an online chart!
		ranges = [
			(0, 25, "Normal"),
			(25, 40, "Mild"),
			(40, 70, "Moderate"),
			(70, 90, "Severe"),
			(90, 120, "Profound")
		]
	else:
		print("Correct usage: python hearing_profiler.py [military/clinical] [input_file].xlsx [output_file].xlsx")
		quit()

	# Read in the file & classify
	df = pd.read_excel(input)
	profiles = []
	ids = []
	averages = []
	for index, row in df.iterrows():
		total_vals = 6
		average_score = (row['RU500'] + row['RU1000'] + row['RU2000'] + row['LU500'] + row['LU1000'] + row['LU2000']) / total_vals # Note: These are the channels we'll use
		profile = ""
		for min, max, label in ranges:
			if min <= average_score <= max:
				profile = label
			if profile != "":
				break
		ids.append(row['ID']) # This ensures the profiles are corresponding to the right ID
		profiles.append(profile)
		averages.append(average_score) # DEBUG
	data = {
		'ID' : ids,
		'Profile' : profiles,
		'Average[DEBUG]' : averages
	}
	final_df = pd.DataFrame(data)
	final_df.to_excel(output)

	# TODO: 
	# - Add real boundary ranges.
	# - Finish debugging.
	# - (If needed) Translate this into R and have it write an xlsx file.
				
	
