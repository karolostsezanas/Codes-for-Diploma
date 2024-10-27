import pandas as pd
import folium
import matplotlib.colors as mcolors
import os

# Load the data from the CSV file
file_path = 'D:\\Diploma\\modis_2023_Canada.csv'
data = pd.read_csv(file_path)

# Convert the acq_date column to datetime
data['acq_date'] = pd.to_datetime(data['acq_date'])

# Initialize the map centered around Canada
map_center = [56.1304, -106.3468]  # Coordinates of Canada
m = folium.Map(location=map_center, zoom_start=4)

# Function to calculate radius based on brightness
def calculate_radius(brightness):
    return (brightness - 300) / 10  # Adjust the divisor to control circle sizes

# Function to get color for each week
def get_color(week_number):
    colors = list(mcolors.TABLEAU_COLORS.values())
    return colors[week_number % len(colors)]

# Function to add markers to the map
def add_weekly_markers(week_data, color):
    for _, row in week_data.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        brightness = row['brightness']
        acq_date = row['acq_date']
        radius = calculate_radius(brightness)
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius if radius > 1 else 1,  # Ensure the minimum radius is 1
            popup=f'Brightness: {brightness}<br>Acquisition Date: {acq_date}',
            color=color,
            fill=True,
            fill_color=color
        ).add_to(m)

# Generate date ranges for each week in May and June
start_dates = pd.date_range(start='2023-05-01', end='2023-06-30', freq='W-MON')
end_dates = start_dates + pd.DateOffset(days=6)

# Dictionary to store fire counts per week
fire_counts = {}

# Filter data for each week and add to the map
for week_number, (start_date, end_date) in enumerate(zip(start_dates, end_dates)):
    week_data = data[(data['acq_date'] >= start_date) & 
                     (data['acq_date'] <= end_date)]
    color = get_color(week_number)
    add_weekly_markers(week_data, color)
    
    # Store the count of fires for the week
    fire_counts[f"Week {week_number + 1} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"] = len(week_data)

# Find the week with the most fire occurrences
max_fire_week = max(fire_counts, key=fire_counts.get)
max_fire_count = fire_counts[max_fire_week]

# Print the week with the most fire occurrences
print(f"The week with the most fire occurrences is {max_fire_week} with {max_fire_count} fires.")

# Save the map to an HTML file
output_file_path = 'fire_map.html'
m.save(output_file_path)

# Check if the file is saved correctly
if os.path.getsize(output_file_path) > 0:
    print(f"Map saved successfully to {output_file_path}")
else:
    print("Error: The map was not saved correctly.")
