import os
import numpy as np
import matplotlib.pyplot as plt
from pyhdf.SD import SD, SDC
from pyhdf.HDF import HDF
from pyhdf.V import V
import glob

def compute_angstrom_exponent(ext_coeff_532, ext_coeff_1064):
    lambda1 = 532
    lambda2 = 1065
    ratio = ext_coeff_532 / ext_coeff_1064
    angstrom_exponent = np.log(ratio) / np.log(lambda1 / lambda2)
    return angstrom_exponent

def plot_profile(angstrom_exponent, altitudes, longitude, latitude, grid_lat, point_number, file, save_dir):
    plt.figure(figsize=(8, 6))
    plt.plot(angstrom_exponent, altitudes, label=f"Lat {latitude} (Point {point_number})")
    plt.title(f"Ångström Exponent profile at Lat {grid_lat} deg (Point {point_number})\nFile: {file}")
    plt.xlabel("Ångström Exponent")
    plt.ylabel("Altitude (km)")
    plt.ylim(0, 10)  # Set y-axis limits to always show up to 10 km
    plt.grid(True)
    plt.legend()
    
    # Create directory if it does not exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Save the plot
    plt.savefig(os.path.join(save_dir, f"GridPoint_{point_number}.png"))
    plt.close()

def process_hdf_files(directory, lat_range, lon_range, lat_step, lon_step, output_dir):
    files = glob.glob(f"{directory}/*.hdf")

    lat_tolerance = 1  # Latitude tolerance
    lon_tolerance = 1  # Longitude tolerance
    max_altitude = 10.0  # Maximum altitude in km

    # Create grid points
    grid_lats = np.arange(lat_range[0], lat_range[1] - lat_step, -lat_step)
    grid_lons = np.arange(lon_range[0], lon_range[1], lon_step)

    for file in files:
        try:
            hdf = SD(file, SDC.READ)
            vs = HDF(file).vstart()
            try:
                ext_coeff_532 = hdf.select('Extinction_Coefficient_532')[:]
                ext_coeff_1064 = hdf.select('Extinction_Coefficient_1064')[:]
                lon = hdf.select('Longitude')[:]
                lat = hdf.select('Latitude')[:]

                # Retrieve the altitude data
                xid = vs.find('metadata')
                altid = vs.attach(xid)
                altid.setfields('Lidar_Data_Altitudes')
                nrecs, _, _, _, _ = altid.inquire()
                altitude_data = altid.read(nRec=nrecs)
                altid.detach()
                altitudes = np.array([alt[0] for alt in altitude_data]).flatten()  # Ensure 1D

                # Cap altitudes at 10 km
                cap_index = np.where(altitudes <= max_altitude)[0]
                altitudes = altitudes[cap_index]

                print(f"Processing file: {file}")
                print(f"Grid latitudes: {grid_lats}")
                print(f"Grid longitudes: {grid_lons}")

                for lat_idx, grid_lat in enumerate(grid_lats, start=1):
                    for lon_idx, grid_lon in enumerate(grid_lons, start=1):
                        # Find points within the tolerance
                        lat_indices = np.where((lat >= grid_lat - lat_tolerance) & (lat <= grid_lat + lat_tolerance))
                        lon_indices = np.where((lon >= grid_lon - lon_tolerance) & (lon <= grid_lon + lon_tolerance))
                        
                        print(f"Grid point: ({grid_lat}, {grid_lon})")
                        print(f"Latitude indices: {lat_indices}")
                        print(f"Longitude indices: {lon_indices}")

                        common_indices = np.intersect1d(lat_indices[0], lon_indices[0])
                        
                        print(f"Common indices: {common_indices}")

                        if len(common_indices) > 0:
                            best_profile = None
                            best_altitudes = None
                            best_lat = None
                            best_lon = None
                            max_avg_angstrom = -np.inf

                            for index in common_indices:
                                ext_532_profile = ext_coeff_532[index, cap_index]  # Apply cap to extinction profile
                                ext_1064_profile = ext_coeff_1064[index, cap_index]

                                # Remove -9999 values
                                valid_indices = (ext_532_profile != -9999) & (ext_1064_profile != -9999)
                                ext_532_profile = ext_532_profile[valid_indices]
                                ext_1064_profile = ext_1064_profile[valid_indices]
                                valid_altitudes = altitudes[valid_indices]

                                if len(ext_532_profile) > 0 and len(ext_1064_profile) > 0:
                                    angstrom_exponent = compute_angstrom_exponent(ext_1064_profile, ext_532_profile)
                                    avg_angstrom = np.mean(angstrom_exponent)

                                    if avg_angstrom > max_avg_angstrom:
                                        max_avg_angstrom = avg_angstrom
                                        best_profile = angstrom_exponent
                                        best_altitudes = valid_altitudes
                                        best_lat = lat[index]
                                        best_lon = lon[index]

                            if best_profile is not None:
                                save_dir = os.path.join(output_dir, f"{int(grid_lat)}")
                                print(f"Saving best profile for point: ({best_lat}, {best_lon}) in file {file} to directory {save_dir}")
                                plot_profile(best_profile, best_altitudes, best_lon, best_lat, grid_lat, lon_idx, file, save_dir)
                        else:
                            print(f"No close trajectory point for grid point ({grid_lat}, {grid_lon}) in file {file}")
            except KeyError:
                print(f"Skipping file {file} due to missing data.")
            except Exception as e:
                print(f"Error processing file {file}: {e}")
        except Exception as e:
            print(f"Error reading file {file}: {e}")

# Directory containing the HDF files
directory = 'D:/CALIPSO/L2 PRO SMOKE'

# Output directory for saving plots
output_dir = 'D:/Diploma/Angstorm plot'

# Latitude and Longitude ranges and steps
lat_range = (62, 42)
lon_range = (-120, 20)
lat_step = 2
lon_step = 2

# Process the HDF files and plot the profiles
process_hdf_files(directory, lat_range, lon_range, lat_step, lon_step, output_dir)
