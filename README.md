
# Sentinel5P-AQI-Toolkit

A collection of Python scripts designed to automate the download and preprocessing of air pollution concentration data derived from the [Sentinel-5P](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-5P) mission from [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/), enabling efficient and accurate data analysis for environmental monitoring.

## Quick Start
The primary script for querying the Copernicus Catalogue, downloading, and processing data is `Complete_S5p_code.ipynb`. Google Colab is used as the execution environment with Google Drive as data storage, offering seamless data storage and processing capabilities.

### Steps:
1. **Run the Import Cell**:
   - This cell initializes the environment by:
     - Importing relevant libraries.
     - Loading necessary variables and credentials from `init.py`.
     - Importing utility functions from `utils.py`.

2. **Query and Download Data**:
   - The script queries the Copernicus Data Space Ecosystem for Sentinel-5P data based on user-defined parameters.
   - The resulting file is a raw Level 2 (L2) netCDF file saved in the `L2_files` folder

3. **Process Data**:
   - The `harpconversion.py` file is used to convert raw Level 2 (L2) files to Level 3 (L3) files. 
   - The resulting file is a netCDF file saved in the `L3_files` folder, binned by time, latitude, and longitude. These files are aligned on a regular grid with a default resolution of 0.01 x 0.01 arc degree.
   - This L3 file can further be converted into a `.csv` file for easier analysis.
   - This `.csv` file is stored in the `Final_Files` folder

---

## Downloading and Processing Data

### Parameters
This toolkit supports several user-defined parameters to customize the data download and processing workflow:

| Option              | Description                                                     |
|---------------------|-----------------------------------------------------------------|
| `--start_date`      | Date to define the start of the time interval. **Date format must be `YYYY-MM-DD`.** |
| `--end_date`        | Date to define the end of the time interval. **Date format must be `YYYY-MM-DD`.** |
| `--aoi_file_path`   | Path to the Area of Interest file in `.geojson` format. See the **Area of Interest** section below. |
| `--unit`            | Unit conversion for output data (default: `mol/m2`). Other supported units: <br> - `Pmolec/cm2` (×10^15 molecules per square centimeter) <br> - `molec/m2` <br> - To change the default unit, update the `unit` value in `init.py` and save the file before running the code. |
| `--qa`              | Quality assurance value threshold (default: `50`). All values below this threshold are filtered out. To adjust, modify the `--qa` parameter or set it manually in `init.py`. |
| `--resolution`      | Grid spatial resolution for Level 3 (L3) data (in arc degrees). |
| `--num-threads`     | Number of threads for downloading Level 2 (L2) data.             |
| `--num-workers`     | Number of worker processes for converting Level 3 (L3) data.     |

### Area of Interest
The `--aoi_file_path` option allows you to specify a custom geographical area using a `.geojson` file. 

#### How to Create a `.geojson` File:
1. Use [geojson.io](https://geojson.io) to generate a custom `.geojson` file for your area of interest.
2. Save the file locally and provide its path in the `--aoi_file_path` parameter.

The name of your area of interest will be automatically derived from the `.geojson` file name.

### Supported Pollutants
The `pollutant` parameter corresponds to a Sentinel-5P product type.Detailed explanation of these pollutants is available in the [Sentinel-5P Documentation](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel5P.html).

TROPOMI Level 2 geophysical products supported by this toolkit are:

| Product Type | Parameter Description                                       |
|--------------|-------------------------------------------------------------|
| `L2__O3____` | Ozone (O3) total column                                     |
| `L2__NO2___` | Nitrogen Dioxide (NO2), tropospheric, stratospheric, slant column |
| `L2__SO2___` | Sulfur Dioxide (SO2) total column                           |
| `L2__CO____` | Carbon Monoxide (CO) total column                           |
| `L2__CH4___` | Methane (CH4) total column                                  |
| `L2__HCHO__` | Formaldehyde (HCHO) tropospheric, slant column              |
| `L2__AER_AI` | UV Aerosol Index                                            |
| `L2__CLOUD_` | Cloud fraction, albedo, top pressure                        |

### Output
- The processed data will be saved in the directories specified in `init.py`.
- You can customize these directories to match your storage preferences:
  - **Level 2 (L2) Files**: Raw downloaded files.
  - **Level 3 (L3) Files**: Processed and gridded data.
  - **Merged and Final Files**: Aggregated and post-processed outputs.

## Dependencies
The necessary libraries and their respective versions required for L2-L3 conversion are provided in the `requirements for L3-L2 conversion.PNG` file. 

**Important Note**: Ensure that you adhere to the specified library versions listed in the file to avoid dependency conflicts during execution.


## Acknowledgements

This project is inspired by and builds upon the work presented in the following article:

@article{OMRANI2020105089,  
  title = "Spatio-temporal data on the air pollutant nitrogen dioxide derived from Sentinel satellite for France",  
  journal = "Data in Brief",  
  volume = "28",  
  pages = "105089",  
  year = "2020",  
  issn = "2352-3409",  
  doi = "https://doi.org/10.1016/j.dib.2019.105089",  
  url = "http://www.sciencedirect.com/science/article/pii/S2352340919314453",  
  author = "Hichem Omrani and Bilel Omrani and Benoit Parmentier and Marco Helbich",  
  keywords = "Air pollution, Remote sensing, Monitoring"  
}
