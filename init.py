import os
import multiprocessing
import sys
sys.path.append('/content')
from utils import (
  get_valid_date_input,
  get_user_choice,
  get_valid_qa_input,
  display_chosen_values

)


# ALL THE NECESSARY CREDENTIALS
username="enter your username here"
password="enter your password here"

# ALL THE NECESSARY PARAMETERS

# Export file paths
L2_Files = L2_folder_path="/content/gdrive/MyDrive/Data_downloading/L2_Files"
L3_Files = L3_folder_path="/content/gdrive/MyDrive/Data_downloading/L3_Files"
Base_Merged_Files="/content/gdrive/MyDrive/Data_downloading/Merged files"
Base_Final_Files="/content/gdrive/MyDrive/Data_downloading/Final files"
Base_PBLH_T2M_Files="/content/gdrive/MyDrive/Data_downloading/PBLH and T2M"

# Timespan of downloads

# Get start date from user
start_date = get_valid_date_input("Enter start date (YYYY-MM-DD): ")
# Get end date from user
while True:
    end_date = get_valid_date_input("Enter end date (YYYY-MM-DD): ")
    if end_date >= start_date:
        break
    else:
        print("End date must be after or equal to start date.")
print("Start date:", start_date) # Example start_date = "2022-06-01"
print("End date:", end_date) # Example end_date = "2022-06-02"

# List of pollutants
pollutants = [
    {"Product type": "L2__O3____", "Parameter": "Ozone (O3) total column"},
    {"Product type": "L2__NO2___", "Parameter": "Nitrogen Dioxide (NO2), tropospheric, stratospheric, slant column"},
    {"Product type": "L2__SO2___", "Parameter": "Sulfur Dioxide (SO2) total column"},
    {"Product type": "L2__CO____", "Parameter": "Carbon Monoxide (CO) total column"},
    {"Product type": "L2__CH4___", "Parameter": "Methane (CH4) total column"},
    {"Product type": "L2__HCHO__", "Parameter": "Formaldehyde (HCHO) tropospheric, slant column"},
    {"Product type": "L2__AER_AI", "Parameter": "UV Aerosol Index"},
    {"Product type": "L2__CLOUD_", "Parameter": "Cloud fraction, albedo, top pressure"}
]
chosen_product_type = get_user_choice(pollutants)
pollutant = chosen_product_type

# Data collection
data_collection = "SENTINEL-5P"

# Area of study
aoi_file_path="path to your geojson file here e.g path/England.geojson"
# name of area of study
aoi_name_to_display = os.path.basename(aoi_file_path) # name with extension
aoi_name_to_display = os.path.splitext(aoi_name_to_display)[0] #remove extension

# Quality Assurance

# Get QA value from user
qa = get_valid_qa_input()
print("QA value:", qa) # Example qa=50

# Get unit value from the user
unit="mol/m2"
# Number of threads
cores = multiprocessing.cpu_count() # Count the number of cores in a computer
num_threads = cores  # Adjust based on your system's capability and network conditions
# Number of workers
num_virtual_cores = os.cpu_count() # Get the number of virtual cores
num_workers= num_virtual_cores
#aoi_format = "POLYGON((4.220581 50.958859,4.521264 50.953236,4.545977 50.906064,4.541858 50.802029,4.489685 50.763825,4.23843 50.767734,4.192435 50.806369,4.189689 50.907363,4.220581 50.958859))'"
# Display the chosen values in a table
display_chosen_values(start_date, end_date, pollutant, qa, unit, num_threads, num_workers, L3_Files, L2_Files, aoi_name_to_display)