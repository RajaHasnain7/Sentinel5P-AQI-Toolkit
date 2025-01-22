try:
    from matplotlib import pyplot as plt # Visualization
    from termcolor import colored # Print colored text
    import cartopy.crs as ccrs # Projected visualizations
    import matplotlib.colors as colors # colors for visualization
    import xarray as xr # Process netCDF S-5p data
    import numpy as np # Data manupulation
    import cartopy # improved visualizations
    import matplotlib.gridspec as gridspec # create subplot 
    from glob import iglob # data access in file manager
    from os.path import join # same
    from functools import reduce # string manipulation
    import pandas as pd # data manipulation
    import harp # Preprocess L2 to L3 Sentinel5p data
    from harp._harppy import NoDataError # import specifc error that may happen when processing L2 to L3
    import itertools  # dict manipulation
    import cartopy.feature as cf 
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    import matplotlib.patches as mpatches
    import imageio # create gif 
    import ipywidgets as widgets
    import pickle
except ModuleNotFoundError as e:
    print(colored(f'Module import error: {e.name} not found', 'red'))
else:
    print(colored('\nAll libraries properly loaded. Ready to start!!!','green'),'\n')

from variables_for_harp import (
  qa_for_harp,
  unit_for_harp,
  pollutant_for_harp,
  L2_files_for_harp,
  L3_files_for_harp,
  lat_length,
  lat_offset,
  lon_length,
  lon_offset,
  xstep,
  ystep

)

# L2 pollutant path

product_path=L2_files_for_harp
input_files=sorted(list(iglob(join(product_path,'**',f'*{pollutant_for_harp}*.nc'),recursive=True)))
input_files_OFFL = sorted(list(iglob(join(product_path, '**', f'*OFFL*{pollutant_for_harp}*.nc'), recursive=True)))
input_files_RPRO = sorted(list(iglob(join(product_path, '**', f'*RPRO*{pollutant_for_harp}*.nc'), recursive=True)))
input_files_NRTI = sorted(list(iglob(join(product_path, '**', f'*NRTI*{pollutant_for_harp}*.nc'), recursive=True)))

# Export path
export_path = L3_files_for_harp

#HARP FUNCTION START

def generate_harp_commands(producttype, qa, unit, lon_step, lat_step, lat_edge_length, lat_edge_offset, lon_edge_length, lon_edge_offset):
    keep_general = [
        "latitude",
        "longitude",
        "sensor_altitude",
        "sensor_azimuth_angle",
        "sensor_zenith_angle",
        "solar_azimuth_angle",
        "solar_zenith_angle",
    ]

    harp_dict = {
        "L2__O3____": {
            "keep": [
                "O3_column_number_density",
                "O3_effective_temperature",
                "cloud_fraction",
            ],
            "filter": [f"O3_column_number_density_validity>={qa}"],
            "convert": [f"derive(O3_column_number_density [{unit}])"],
        },
        "L2__NO2___": {
            "keep": [
                "tropospheric_NO2_column_number_density",
                "NO2_column_number_density",
                "stratospheric_NO2_column_number_density",
                "NO2_slant_column_number_density",
                "tropopause_pressure",
                "absorbing_aerosol_index",
                "cloud_fraction",
            ],
            "filter": [
                f"tropospheric_NO2_column_number_density_validity>={qa}",
                "tropospheric_NO2_column_number_density>=0",
            ],
            "convert": [
                f"derive(tropospheric_NO2_column_number_density [{unit}])",
                f"derive(stratospheric_NO2_column_number_density [{unit}])",
                f"derive(NO2_column_number_density [{unit}])",
                f"derive(NO2_slant_column_number_density [{unit}])",
            ],
        },
        "L2__SO2___": {
            "keep": [
                "SO2_column_number_density",
                "SO2_column_number_density_amf",
                "SO2_slant_column_number_density",
                "cloud_fraction",
            ],
            "filter": [f"SO2_column_number_density_validity>={qa}"],
            "convert": [
                f"derive(SO2_column_number_density [{unit}])",
                f"derive(SO2_slant_column_number_density [{unit}])",
            ],
        },
        "L2__CO____": {
            "keep": ["CO_column_number_density", "H2O_column_number_density"],
            "filter": [f"CO_column_number_density_validity>={qa}"],
            "convert": [
                f"derive(CO_column_number_density [{unit}])",
                f"derive(H2O_column_number_density [{unit}])",
            ],
        },
        "L2__CH4___": {
            "keep": [
                "CH4_column_volume_mixing_ratio_dry_air",
                "aerosol_height",
                "aerosol_optical_depth",
                "cloud_fraction",
            ],
            "filter": [f"CH4_column_volume_mixing_ratio_dry_air_validity>={qa}"],
            "convert": [],
        },
        "L2__HCHO__": {
            "keep": [
                "tropospheric_HCHO_column_number_density",
                "tropospheric_HCHO_column_number_density_amf",
                "HCHO_slant_column_number_density",
                "cloud_fraction",
            ],
            "filter": [f"tropospheric_HCHO_column_number_density_validity>={qa}"],
            "convert": [
                f"derive(tropospheric_HCHO_column_number_density [{unit}])",
                f"derive(HCHO_slant_column_number_density [{unit}])",
            ],
        },
        "L2__CLOUD_": {
            "keep": [
                "cloud_fraction",
                "cloud_top_pressure",
                "cloud_top_height",
                "cloud_base_pressure",
                "cloud_base_height",
                "cloud_optical_depth",
                "surface_albedo",
            ],
            "filter": [f"cloud_fraction_validity>={qa}"],
            "convert": [],
        },
        "L2__AER_AI": {
            "keep": [
                "absorbing_aerosol_index",
            ],
            "filter": [f"absorbing_aerosol_index_validity>={qa}"],
            "convert": [],
        },
        "L2__AER_LH": {
            "keep": [
                "aerosol_height",
                "aerosol_pressure",
                "aerosol_optical_depth",
                "cloud_fraction",
            ],
            "filter": [f"aerosol_height_validity>={qa}"],
            "convert": [],
        },
        # Add other product types here as needed, following the same structure.
    }

    operations = (
         ";".join(harp_dict[producttype]["filter"])
        + (";" if len(harp_dict[producttype]["filter"]) != 0 else "")
        + ";".join(harp_dict[producttype]["convert"])
        + (";" if len(harp_dict[producttype]["convert"]) != 0 else "")
        + "derive(datetime_stop {time});"
        + f"bin_spatial({lat_edge_length},{lat_edge_offset},{lat_step},{lon_edge_length},{lon_edge_offset},{lon_step});"
        + "derive(latitude {latitude});derive(longitude {longitude});"
        + f"keep({','.join(harp_dict[producttype]['keep'] + keep_general)})"
    )
    
    return operations

#HARP FUNCTION ENDED

not_processed = []

for i in input_files:
    try:
        # Generate HARP command for the current file
       
        producttype = pollutant_for_harp  #producttype = "L2__NO2___" (Example product type, adjust as needed)
        
        qa = qa_for_harp #qa = 50 (Quality assurance level)
        
        unit = unit_for_harp #unit = "Pmolec/cm2" or "mol/m2"  (Unit for derived quantities)
        
        
        lon_step = xstep #lon_step = 0.01 (Longitude step)
        lat_step = ystep #lat_step = 0.01 (Latitude step)

        
        lat_edge_length = lat_length  #lat_edge_length = 39 (Number of latitude bins)

        
        lat_edge_offset = lat_offset  #lat_edge_offset = 12.85  (Starting latitude)
        
        lon_edge_length = lon_length  #lon_edge_length = 20  (Number of longitude bins)
        
        lon_edge_offset = lon_offset  #lon_edge_offset = 80.14  (Starting longitude)

        harp_command = generate_harp_commands(producttype, qa, unit, lon_step, lat_step, lat_edge_length, lat_edge_offset, lon_edge_length, lon_edge_offset)

        # Process the file with the generated HARP command
        harp_L2_L3 = harp.import_product(i, operations=harp_command)

        # Construct the export folder path and file name
        export_folder = "{export_path}/{name}".format(export_path=export_path, name=i.split('/')[-1].replace('L2', 'L3'))
        harp.export_product(harp_L2_L3, export_folder, file_format='netcdf')

    except Exception as e:
        print(f"Error processing {i}: {e}")
        not_processed.append(i)

# Summary after processing
print(colored(f"{len(input_files)-len(not_processed)}/{len(input_files)} L2 products converted to L3.",'green'))
if not_processed:
    print(colored("Non-processed L2 products:", not_processed,'red'))

# Save two orignal attributes from the L2 product (time_coverage_start and time_coverage_end)
attributes = {
        i.split('/')[-1]: {
            'time_coverage_start': xr.open_dataset(i).attrs['time_coverage_start'],
            'time_coverage_end': xr.open_dataset(i).attrs['time_coverage_end'],
        } for i in input_files
    }

# Save the attributes dictionary to a .pkl file so that we can export this dict to main collab notebook
with open('attributes.pkl', 'wb') as f:
    pickle.dump(attributes, f)