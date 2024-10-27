import pandas as pd
from pyhdf.SD import SD, SDC
import numpy as np

def read_hdf_data(hdf_file, dataset_name):
    hdf = SD(hdf_file, SDC.READ)
    data = hdf.select(dataset_name)[:]
    return data

def extract_aerosol_layers(vfm_data, layer_top_altitude, layer_base_altitude, lat, lon, target_lat, max_alt=10):
    aerosol_types = {
        0: 'Invalid',
        1: 'Clean Marine',
        2: 'Dust',
        3: 'Polluted Continental',
        4: 'Clean Continental',
        5: 'Polluted Dust',
        6: 'Smoke',
        7: 'Other'
    }
    
    data_ft = vfm_data & 7
    vfm_data[(data_ft > 3) | (data_ft < 3)] = 0
    vfm_data = (vfm_data >> 9) & 7

    lat = np.array(lat)
    lon = np.array(lon)
    if len(lat.shape) == 1:
        lat = lat[:, np.newaxis]
    if len(lon.shape) == 1:
        lon = lon[:, np.newaxis]

    valid_top_altitude = (layer_top_altitude <= max_alt) & (layer_top_altitude != -9999)
    valid_base_altitude = (layer_base_altitude <= max_alt) & (layer_base_altitude != -9999)

    lat_range_mask = (lat >= target_lat[1]) & (lat <= target_lat[0])

    valid_data_mask = np.zeros(vfm_data.shape, dtype=bool)
    for i in range(vfm_data.shape[0]):
        if lat_range_mask[i, 0]:
            valid_data_mask[i, :] = valid_top_altitude[i, :] & valid_base_altitude[i, :]

    valid_data = vfm_data[valid_data_mask]
    valid_layer_top_altitudes = layer_top_altitude[valid_data_mask]
    valid_layer_base_altitudes = layer_base_altitude[valid_data_mask]
    valid_latitudes = np.repeat(lat[:, np.newaxis], vfm_data.shape[1], axis=1)[valid_data_mask]
    valid_longitudes = np.repeat(lon[:, np.newaxis], vfm_data.shape[1], axis=1)[valid_data_mask]
    
    unique_aerosols = np.unique(valid_data)
    aerosol_layers_info = []
    
    for aerosol in unique_aerosols:
        aerosol_mask = valid_data == aerosol
        top_altitudes = valid_layer_top_altitudes[aerosol_mask]
        base_altitudes = valid_layer_base_altitudes[aerosol_mask]
        if len(top_altitudes) > 0 and len(base_altitudes) > 0:
            top_altitude = np.max(top_altitudes)
            bottom_altitude = np.min(base_altitudes)
            aerosol_layers_info.append({
                'type': aerosol_types.get(aerosol, 'Unknown'),
                'top_altitude': top_altitude,
                'bottom_altitude': bottom_altitude,
                'lat_min': np.min(valid_latitudes[aerosol_mask]),
                'lat_max': np.max(valid_latitudes[aerosol_mask])
            })
    
    return aerosol_layers_info

# Read the Excel file
excel_file_path = 'D:/Diploma/Backscatter plot/latitudes.xlsx'
df = pd.read_excel(excel_file_path)

# Prepare to store results
results = []

# Process each file
for _, row in df.iterrows():
    lat_max = row['Lat_Max']
    lat_min = row['Lat_Min']
    hdf_file_base = row['File_Name'].replace('_PRO', '_LAY')
    hdf_file = f"D:/CALIPSO/L2 LAY SMOKE/{hdf_file_base}"
    
    # Read data from HDF file
    latitude_data = read_hdf_data(hdf_file, 'Latitude')
    longitude_data = read_hdf_data(hdf_file, 'Longitude')
    vfm_data = read_hdf_data(hdf_file, 'Feature_Classification_Flags')
    layer_top_altitude = read_hdf_data(hdf_file, 'Layer_Top_Altitude')
    layer_base_altitude = read_hdf_data(hdf_file, 'Layer_Base_Altitude')
    
    target_lat = (lat_max, lat_min)
    aerosol_layers_info = extract_aerosol_layers(vfm_data, layer_top_altitude, layer_base_altitude, latitude_data, longitude_data, target_lat)
    
    for layer in aerosol_layers_info:
        results.append({
            'Layer_Base_Altitude': layer['bottom_altitude'],
            'Layer_Top_Altitude': layer['top_altitude'],
            'Number_of_Layers': len(aerosol_layers_info),
            'Lat_Min': layer['lat_min'],
            'Lat_Max': layer['lat_max'],
            'Subtype': layer['type'],
            'File_Name': row['File_Name']
        })

# Create a DataFrame for the results
results_df = pd.DataFrame(results)

# Save the results to a new Excel file
results_df.to_excel('D:/Diploma/Backscatter plot/aerosol_layers_results.xlsx', index=False)

print("Processing complete. Results saved to 'D:/Diploma/Backscatter plot/aerosol_layers_results.xlsx'")
