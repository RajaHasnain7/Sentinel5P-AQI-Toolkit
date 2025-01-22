import json
import os
from shapely.geometry import shape
from datetime import datetime
from tqdm import tqdm
import requests
import pandas as pd
import speedtest
import shutil
import geopandas
from datetime import timedelta


def get_user_choice(pollutants):
    print("Please select a pollutant by entering the corresponding number:")
    for i, pollutant in enumerate(pollutants, start=1):
        print(f"{i}. {pollutant['Parameter']} ({pollutant['Product type']})")
    
    while True:
        try:
            choice = int(input("Enter your choice (1-8): ")) - 1
            if 0 <= choice < len(pollutants):
                return pollutants[choice]['Product type']
            else:
                print("Invalid choice. Please enter a number between 1 and 8.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def load_geojson(file_path):
    """Load GeoJSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return None

def extract_aoi(geojson_data):
    """Extracts the AOI from GeoJSON data and returns it as a WKT string."""
    try:
        # Assuming the first feature is the AOI; adjust as needed
        first_feature = geojson_data['features'][0]
        geometry = first_feature['geometry']

        # Convert the geometry to a Shapely shape and then to WKT
        shapely_geom = shape(geometry)
        return shapely_geom.wkt
    except Exception as e:
        print(f"Error extracting AOI: {e}")
        return None

# Function to validate date format
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Function to get valid date input from user
def get_valid_date_input(prompt):
    while True:
        user_input = input(prompt)
        if is_valid_date(user_input):
            return user_input
        else:
            print("Invalid date format. Please enter date in YYYY-MM-DD format.")

# Function to validate QA value
def is_valid_qa(qa_str):
    try:
        qa = int(qa_str)
        return 0 <= qa <= 100
    except ValueError:
        return False

# Function to get valid QA input from user
def get_valid_qa_input():
    while True:
        qa_input = input("Enter QA value (0-100): ")
        if is_valid_qa(qa_input):
            return int(qa_input)
        else:
            print("Invalid QA value. Please enter a number between 0 and 100.")

# Function to display the chosen values in text format
def display_chosen_values(start_date, end_date, pollutant, qa, unit, num_threads, num_workers, L3_Files, L2_Files, aoi_name_to_display):
    # Define column widths
    col_width_1 = 30
    col_width_2 = 60
    # Print table header
    print("Chosen Values:")
    print("-" * (col_width_1 + col_width_2 + 5))
    print(f"|{'Title':{col_width_1}}|{'Value':{col_width_2}}|")
    print("-" * (col_width_1 + col_width_2 + 5))
    # Print table rows
    print(f"|{'Start Date':{col_width_1}}|{start_date:{col_width_2}}|")
    print(f"|{'End Date':{col_width_1}}|{end_date:{col_width_2}}|")
    print(f"|{'Pollutant':{col_width_1}}|{pollutant:{col_width_2}}|")
    print(f"|{'Area of interest':{col_width_1}}|{aoi_name_to_display:{col_width_2}}|")
    print(f"|{'QA Value':{col_width_1}}|{qa:{col_width_2}}|")
    print(f"|{'Unit':{col_width_1}}|{unit:{col_width_2}}|")
    print(f"|{'Number of Threads':{col_width_1}}|{num_threads:{col_width_2}}|")
    print(f"|{'Number of Workers':{col_width_1}}|{num_workers:{col_width_2}}|")
    print(f"|{'Path to L3 Files':{col_width_1}}|{L3_Files:{col_width_2}}|")
    print(f"|{'Path to L2 Files':{col_width_1}}|{L2_Files:{col_width_2}}|")
    print("-" * (col_width_1 + col_width_2 + 5))

# To analyze pollutant download speed
def analyze_pollutants(results):
    # Total number of products before filtering
    total_products = len(results)

    # Filter out products with a content length of 0
    filtered_results = results[results['ContentLength'] > 0]

    # Number of products after filtering (i.e., with positive content length)
    products_with_positive_content_length = len(filtered_results)

    # Calculate the number of products filtered out
    products_filtered_out = total_products - products_with_positive_content_length

    # Calculate total size in bytes for filtered results
    total_size_bytes = filtered_results['ContentLength'].sum()

    # Convert total size to megabytes (MB) and gigabytes (GB)
    total_size_mb = total_size_bytes / (1024 * 1024)
    total_size_gb = total_size_bytes / (1024 * 1024 * 1024)

    # Calculate average size in bytes for filtered results
    average_size_bytes = filtered_results['ContentLength'].mean()

    # Convert average size to megabytes (MB)
    average_size_mb = average_size_bytes / (1024 * 1024)

    # Create a Speedtest object
    s = speedtest.Speedtest()

    # Get best server based on ping
    s.get_best_server()

    # Perform download and upload speed tests
    download_speed_bps = s.download()
    upload_speed_bps = s.upload()

    # Calculate downloading time for products
    # Convert download speed from bits per second to bytes per second
    download_speed_bps = download_speed_bps / 8

    # Convert download and upload speeds from bytes per second (Bps) to megabits per second (Mbps)
    download_speed_mbps = download_speed_bps / (1024 * 1024)
    upload_speed_mbps = upload_speed_bps / (1024 * 1024)

    # Calculate downloading time in seconds
    downloading_time_seconds = total_size_bytes / download_speed_bps

    # Optionally, convert downloading time to minutes for readability
    downloading_time_minutes = downloading_time_seconds / 60

    # Define column widths
    col_width_1 = 60
    col_width_2 = 10

    print("-" * (col_width_1 + col_width_2 + 5))
    print(f"{'Title':{col_width_1}}|{'Value':>{col_width_2}}")  # Right-align the value column
    print("-" * (col_width_1 + col_width_2 + 5))
    # Print table rows
    print(f"{'Total number of pollutants found':<{col_width_1}}|{total_products:>{col_width_2}}")
    print(f"{'Number of pollutants filtered out':<{col_width_1}}|{products_filtered_out:>{col_width_2}}")
    print(f"{'Total size of all pollutants (excluding content length 0) ':<{col_width_1}}|{total_size_mb:>{col_width_2}.2f} MB")
    print(f"{'Average size of pollutants (excluding content length 0)':<{col_width_1}}|{average_size_mb:>{col_width_2}.2f} MB")
    print(f"{'Download speed ':<{col_width_1}}|{download_speed_mbps:>{col_width_2}.2f} Mbps")
    print(f"{'Upload speed ':<{col_width_1}}|{upload_speed_mbps:>{col_width_2}.2f} Mbps")
    print(f"{'Estimated downloading time for filtered products':<{col_width_1}}|{downloading_time_minutes:^{col_width_2}.2f}mins")
    print("-" * (col_width_1 + col_width_2 + 5))


def move_nc_files_and_cleanup(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        # Move .nc files to the root directory if not already there
        for name in files:
            if name.endswith('.nc') and root != directory:
                source = os.path.join(root, name)
                destination = os.path.join(directory, name)
                shutil.move(source, destination)
            elif not name.endswith('.nc'):
                # Delete files not ending with .nc
                os.remove(os.path.join(root, name))

    # Delete empty directories
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            if not os.listdir(dir_path):  # Check if directory is empty
                os.rmdir(dir_path)


def compute_lengths_and_offsets(minx, miny, maxx, maxy, ystep, xstep):

    lat_edge_length = int(abs(maxy - miny) / ystep + 1)
    lat_edge_offset = miny
    lon_edge_length = int(abs(maxx - minx) / xstep + 1)
    lon_edge_offset = minx

    return lat_edge_length, lat_edge_offset, lon_edge_length, lon_edge_offset




def get_user_choice_to_filter_data():
    base_type_mapping = {
        "1": "ALL",   # Represents all types
        "2": "OFFL",  # Offline data
        "3": "NRTI",  # Near real-time data
        "4": "RPRO"   # Reprocessed data
    }
    
    while True:
        print("\nSelect the type of data you wish to keep:")
        print("1: Keep all results")
        print("2: Keep only the offline data")
        print("3: Keep only the near real time data")
        print("4: Keep only the reprocessed data")
        user_choice = input("Enter your choice (1/2/3/4): ")
        
        if user_choice in base_type_mapping:
            base_type = base_type_mapping[user_choice]
            return user_choice, base_type
        else:
            print("Invalid choice. Please select a proper choice.")


def filter_data(df, choice):
    if choice == "2":  # Offline data
        return df[df['Name'].str.contains("_OFFL_")]
    elif choice == "3":  # Near real time data
        return df[df['Name'].str.contains("_NRTI_")]
    elif choice == "4":  # Reprocessed data
        return df[df['Name'].str.contains("_RPRO_")]
    else:  # Keep all data
        return df


# Function to count the occurrences and total
def count_pollutant_data_types(df):
    offline_count = df['Name'].str.contains("_OFFL_").sum()
    nrti_count = df['Name'].str.contains("_NRTI_").sum()
    rpro_count = df['Name'].str.contains("_RPRO_").sum()
    total_count = len(df)
    return offline_count, nrti_count, rpro_count, total_count

# Function to get the keycloak token and refresh token
def get_keycloak(username: str, password: str):
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    try:
        r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
                          data=data)
        r.raise_for_status()
    except Exception as e:
        raise Exception(f"Keycloak token creation failed. Response from the server was: {r.json()}")
    response_data = r.json()
    access_token = response_data["access_token"]
    refresh_token = response_data.get("refresh_token", None)
    return access_token, refresh_token

# Function to refresh the access token
def refresh_access_token(refresh_token: str):
    data = {
        "client_id": "cdse-public",
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    try:
        r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
                          data=data)
        r.raise_for_status()
    except Exception as e:
        raise Exception(f"Access token refresh failed. Response from the server was: {r.json()}")
    return r.json()["access_token"]

# Function to check if the refresh token is about to expire
def is_refresh_token_expired(token_acquired_time: datetime, lifespan_minutes=60) -> bool:
    return datetime.now() >= token_acquired_time + timedelta(minutes=lifespan_minutes)

# Function to check if the access token has expired
def is_access_token_expired(current_time, expiration_time):
    check_time = datetime.now()
    return check_time >= expiration_time


# Define the base regex pattern with a placeholder for the pollutant product type
def get_regex_pattern(base_type, pollutant_for_L3):
    if base_type == "ALL":
        # Match any of the types if "ALL" is selected
        base_pattern = r'S5P_(OFFL|NRTI|RPRO)_{product_type}_(\d{{8}})T'
    else:
        # Use the specific base_type if a single type is selected
        base_pattern = r'S5P_{base_type}_{product_type}_(\d{{8}})T'

    # Insert the chosen pollutant product type and base_type into the regex pattern
    return base_pattern.format(base_type=base_type, product_type=pollutant_for_L3)

def get_variables_to_include(pollutant_for_L3):
    if pollutant_for_L3 == "L3__O3____":
        variables_to_include = ['O3_column_number_density', 'O3_effective_temperature', 'cloud_fraction']
    elif pollutant_for_L3 == "L3__NO2___":
        variables_to_include = ['tropospheric_NO2_column_number_density', 'cloud_fraction']
    elif pollutant_for_L3 == "L3__CO____":
        variables_to_include = ['CO_column_number_density']
    elif pollutant_for_L3 == "L3__SO2___":
        variables_to_include = ['SO2_column_number_density', 'cloud_fraction']
    elif pollutant_for_L3 == "L3__AER_AI":
        variables_to_include = ['absorbing_aerosol_index']
    else:
        variables_to_include = []

    return variables_to_include
