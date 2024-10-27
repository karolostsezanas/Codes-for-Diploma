import pandas as pd
import folium

# Load the data from the Excel file
file_path = 'D:\\Diploma\\modis_2023_Canada.csv'
data = pd.read_csv(file_path)

# Assuming the Excel file has columns named 'Latitude' and 'Longitude'
latitude_column = 'latitude'
longitude_column = 'longitude'
brightness_column = 'brightness'  # Adjust this based on your file

# Convert the acq_date column to datetime
data['acq_date'] = pd.to_datetime(data['acq_date'])

# Filter data for the week of 01/05/2023 to 07/05/2023
start_date = '2023-05-15'
end_date = '2023-05-25'
filtered_data = data[(data['acq_date'] >= start_date) & (data['acq_date'] <= end_date)]

# Aggregate by date to find the date with the most fires
date_counts = filtered_data['acq_date'].value_counts()
most_fires_date = date_counts.idxmax()
most_fires_count = date_counts.max()

print(f"The date with the most fires: {most_fires_date}, Number of fires: {most_fires_count}")

# Filter data for the specific date 19/05/23
specific_date = '2023-05-19'
fires_on_specific_date = filtered_data[filtered_data['acq_date'] == specific_date]

# Calculate the average latitude and longitude
avg_latitude = fires_on_specific_date['latitude'].mean()
avg_longitude = fires_on_specific_date['longitude'].mean()

print(f"Average Latitude (19/05/23): {avg_latitude}, Average Longitude (19/05/23): {avg_longitude}")

# Create a map centered around Canada
map_center = [56.1304, -106.3468]  # Coordinates of Canada
m = folium.Map(location=map_center, zoom_start=4)

# Function to calculate radius based on brightness
def calculate_radius(brightness):
    return (brightness - 300) / 10  # Adjust the divisor to control circle sizes

# Add data points to the map for the specific date
for _, row in fires_on_specific_date.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    brightness = row['brightness']
    acq_date = row['acq_date']
    radius = calculate_radius(brightness)
    folium.CircleMarker(
        location=[lat, lon],
        radius=radius if radius > 1 else 1,  # Ensure the minimum radius is 1
        popup=f'Brightness: {brightness}<br>Acquisition Date: {acq_date}<br>Latitude: {lat}<br>Longitude: {lon}',
        color='red',
        fill=True,
        fill_color='red'
    ).add_to(m)

# Save the map to an HTML file
m.save('fire_map_specific_date.html')
