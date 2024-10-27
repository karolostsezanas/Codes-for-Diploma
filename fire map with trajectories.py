import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pyhdf.SD import SD, SDC
import glob
import re

# Function to generate grid points
def generate_grid(lon_min, lon_max, lat_min, lat_max, step):
    longitudes = np.arange(lon_min, lon_max + step, step)
    latitudes = np.arange(lat_min, lat_max + step, step)
    return np.meshgrid(longitudes, latitudes)

# Function to load and process CALIPSO data from HDF files
def load_hdf_data(file_path):
    hdf_file = SD(file_path, SDC.READ)
    lat = hdf_file.select('Latitude')
    lon = hdf_file.select('Longitude')
    lat_data = lat[:].flatten()
    lon_data = lon[:].flatten()
    hdf_file.end()
    return pd.DataFrame({'latitude': lat_data, 'longitude': lon_data})

# Load fire data from CSV
file_path = 'D:\\Diploma\\modis_2023_Canada.csv'
data = pd.read_csv(file_path)
data['acq_date'] = pd.to_datetime(data['acq_date'])
start_date = '2023-05-15'
end_date = '2023-05-25'
filtered_data = data[(data['acq_date'] >= start_date) & (data['acq_date'] <= end_date)]
specific_date = '2023-05-19'
fires_on_specific_date = filtered_data[filtered_data['acq_date'] == specific_date]

# Configuration for grid
lon_min, lon_max = -120, 8
lat_min, lat_max = 42, 62
step = 2

# Generate grid points
longitudes, latitudes = generate_grid(lon_min, lon_max, lat_min, lat_max, step)

# Set up the map
fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_extent([lon_min - 2, lon_max + 2, lat_min - 2, lat_max + 2], crs=ccrs.PlateCarree())

# Add gridlines and labels
gridlines = ax.gridlines(draw_labels=True, dms=False, x_inline=False, y_inline=False)
gridlines.top_labels = False
gridlines.right_labels = False
gridlines.xlocator = plt.FixedLocator(np.arange(lon_min - 2, lon_max + 12, 10))
gridlines.ylocator = plt.FixedLocator(np.arange(lat_min - 2, lat_max + 4, 2))

# Plot the grid points
ax.scatter(longitudes, latitudes, color='orange', s=10, transform=ccrs.PlateCarree(), label='Grid Points')

# Plot fire data
ax.scatter(fires_on_specific_date['longitude'], fires_on_specific_date['latitude'], color='red', s=20, transform=ccrs.PlateCarree(), label='Fires')

# Load and plot CALIPSO trajectories
directory_path = 'D:/CALIPSO/L1 SMOKE'
file_paths = glob.glob(f"{directory_path}/*.hdf")
for file_path in file_paths:
    df = load_hdf_data(file_path)
    if re.search(r'\d+_2_L1', file_path):
        color = 'green'
    elif re.search(r'\d+_1_L1', file_path):
        color = 'blue'
    else:
        color = 'gray'
    ax.plot(df['longitude'], df['latitude'], color=color, linewidth=1, transform=ccrs.PlateCarree(), label=f'Trajectory ({file_path})')

# Adding coastlines and borders for better visual context
ax.coastlines()
ax.add_feature(cfeature.BORDERS, linestyle=':')

# Set labels for axes
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Adjust the legend to be outside the plot
ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize='small')

# Show the plot
plt.show()
